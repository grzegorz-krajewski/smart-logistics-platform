package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

// Struktura skanu
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

func main() {
	r := gin.Default()
	r.SetTrustedProxies([]string{"127.0.0.1"})

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

	r.Run(":8081")
}

// Funkcja wysyłająca dane do Pythona
func forwardToPython(scan ScanRequest) {
	pythonURL := "http://127.0.0.1:8000/pallets/"

	payload := PythonPallet{
		Barcode: scan.Barcode,
		Weight:  scan.Weight,
	}

	jsonData, _ := json.Marshal(payload)

	// Tworzymy klienta z krótkim timeoutem
	client := &http.Client{Timeout: 5 * time.Second}

	resp, err := client.Post(pythonURL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		println("!!! BŁĄD PRZEKAZANIA DO PYTHONA:", err.Error())
		return
	}
	defer resp.Body.Close()

	println(">>> [HANDSHAKE SUCCESS] Dane wysłane do Pythona. Status:", resp.Status)
}
