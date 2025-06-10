package main

import (
	"context"
	"crypto/tls"
	"crypto/x509"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/alphaflow-trading/market-data/auth"
	"github.com/prometheus/client_golang/prometheus/promhttp"

	"github.com/alphaflow-trading/market-data/config"
	"github.com/alphaflow-trading/market-data/publisher"
	ws "github.com/alphaflow-trading/market-data/websocket"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("config error: %v", err)
	}

	pub := publisher.NewRedisPublisher(cfg.RedisAddr, cfg.Channel)
	client := ws.New(cfg, pub, "marketdata.db")
	if err := client.Start(); err != nil {
		log.Fatal(err)
	}

	go func() {
		mux := http.NewServeMux()
		mux.Handle("/metrics", promhttp.Handler())
		secret := os.Getenv("SERVICE_JWT_SECRET")
		service := os.Getenv("SERVICE_NAME")
		handler := auth.Middleware(secret, service)(mux)
		srv := &http.Server{
			Addr:              ":2112",
			Handler:           handler,
			ReadHeaderTimeout: 5 * time.Second,
		}
		cert := os.Getenv("TLS_CERT_FILE")
		key := os.Getenv("TLS_KEY_FILE")
		ca := os.Getenv("TLS_CA_FILE")
		if cert != "" && key != "" && ca != "" {
			srv.TLSConfig = authTLSConfig(ca)
			if err := srv.ListenAndServeTLS(cert, key); err != nil {
				log.Printf("https server error: %v", err)
			}
		} else {
			if err := srv.ListenAndServe(); err != nil {
				log.Printf("http server error: %v", err)
			}
		}
	}()

	sig := make(chan os.Signal, 1)
	signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)
	<-sig
	client.Stop()
	pub.Publish(context.Background(), []byte("shutdown"))
}

func authTLSConfig(ca string) *tls.Config {
	certPool := x509.NewCertPool()
	caData, err := os.ReadFile(ca)
	if err == nil {
		certPool.AppendCertsFromPEM(caData)
	}
	return &tls.Config{ClientCAs: certPool, ClientAuth: tls.RequireAndVerifyClientCert}
}
