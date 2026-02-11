package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"net/url"
	"sync"
	"time"
	"github.com/gin-gonic/gin"
	"os"
)

type ScanRequest struct {
	Barcode   string `json:"barcode" binding:"required"`
	DockNum   string `json:"dock_number" binding:"required"`
	ScannerID string `json:"scanner_id" binding:"required"`
	Weight    int    `json:"weight" binding:"required"`
}

type PythonPallet struct {
	Barcode string `json:"barcode"`
	Weight  int    `json:"weight"`
}

// ===== Auth cache =====

type tokenResponse struct {
	AccessToken string `json:"access_token"`
	TokenType   string `json:"token_type"`
}

var (
	tokenMu     sync.Mutex
	cachedToken string
	tokenExp    time.Time
)

const (
	apiBase := mustEnv("PY_API_BASE")        
	serviceUser := mustEnv("PY_API_USER")       
	servicePass := mustEnv("PY_API_PASS")       
	palletURL := apiBase + "/api/pallets"
	loginURL := apiBase + "/api/auth/login"
)

func main() {
	r := gin.Default()
	_ = r.SetTrustedProxies([]string{"127.0.0.1"})

	r.POST("/scan", func(c *gin.Context) {
		var scan ScanRequest
		if err := c.ShouldBindJSON(&scan); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		go forwardToPython(scan)

		c.JSON(http.StatusAccepted, gin.H{
			"status": "Accepted",
			"info":   "Skan przekazany do przetwarzania",
		})
	})

	_ = r.Run(":8081")
}

func forwardToPython(scan ScanRequest) {
	payload := PythonPallet{
		Barcode: scan.Barcode,
		Weight:  scan.Weight,
	}

	jsonData, _ := json.Marshal(payload)

	client := &http.Client{Timeout: 5 * time.Second}

	// 1) pobierz token (cache)
	tok, err := getBearerToken(client)
	if err != nil {
		println("!!! BŁĄD AUTH:", err.Error())
		return
	}

	// 2) request do API
	req, _ := http.NewRequest("POST", palletURL, bytes.NewBuffer(jsonData))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+tok)

	resp, err := client.Do(req)
	if err != nil {
		println("!!! BŁĄD PRZEKAZANIA DO PYTHONA:", err.Error())
		return
	}
	defer resp.Body.Close()

	// jeśli token wygasł lub coś się rozjechało — spróbuj raz odświeżyć i ponowić
	if resp.StatusCode == http.StatusUnauthorized {
		invalidateToken()

		tok, err = getBearerToken(client)
		if err != nil {
			println("!!! BŁĄD AUTH (refresh):", err.Error())
			return
		}

		req2, _ := http.NewRequest("POST", palletURL, bytes.NewBuffer(jsonData))
		req2.Header.Set("Content-Type", "application/json")
		req2.Header.Set("Authorization", "Bearer "+tok)

		resp2, err := client.Do(req2)
		if err != nil {
			println("!!! BŁĄD PRZEKAZANIA DO PYTHONA (retry):", err.Error())
			return
		}
		defer resp2.Body.Close()

		println(">>> retry status:", resp2.Status)
		return
	}

	body, _ := io.ReadAll(resp.Body)
	println(">>> [PY API] Status:", resp.Status, "Body:", string(body))
}

func invalidateToken() {
	tokenMu.Lock()
	defer tokenMu.Unlock()
	cachedToken = ""
	tokenExp = time.Time{}
}

func getBearerToken(client *http.Client) (string, error) {
	tokenMu.Lock()
	if cachedToken != "" && time.Now().Before(tokenExp) {
		t := cachedToken
		tokenMu.Unlock()
		return t, nil
	}
	tokenMu.Unlock()

	// login form-data (x-www-form-urlencoded)
	form := url.Values{}
	form.Set("username", serviceUser)
	form.Set("password", servicePass)

	req, _ := http.NewRequest("POST", loginURL, bytes.NewBufferString(form.Encode()))
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")

	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		b, _ := io.ReadAll(resp.Body)
		return "", errors.New("login failed: " + resp.Status + " " + string(b))
	}

	var tr tokenResponse
	if err := json.NewDecoder(resp.Body).Decode(&tr); err != nil {
		return "", err
	}
	if tr.AccessToken == "" {
		return "", errors.New("empty token from auth")
	}

	// W Twoim Pythonie token jest na 60 min.
	// Bez dekodowania JWT ustawiamy bezpiecznie np. 55 min.
	tokenMu.Lock()
	cachedToken = tr.AccessToken
	tokenExp = time.Now().Add(55 * time.Minute)
	tokenMu.Unlock()

	return tr.AccessToken, nil
}

func mustEnv(key string) string {
	v := os.Getenv(key)
	if v == "" {
		panic("missing env: " + key)
	}
	return v
}