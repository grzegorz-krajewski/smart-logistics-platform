package main

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

func main() {
	// Gin.Default() automatycznie dodaje logowanie i odzyskiwanie po błędach
	r := gin.Default()

	// Endpoint do sprawdzania, czy bramka żyje
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "Go Gateway działa!",
			"time":    time.Now().Format(time.RFC3339),
			"v":       "0.6.1",
		})
	})

	// To będzie nasz ultra-szybki punkt przyjęć dla skanerów
	r.POST("/scan", func(c *gin.Context) {
		c.JSON(http.StatusAccepted, gin.H{
			"status": "Skan odebrany przez Go",
		})
	})

	// Startujemy na porcie 8081 (Python ma 8000)
	r.Run(":8081")
}
