package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"

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
	client := ws.New(cfg, pub)
	if err := client.Start(); err != nil {
		log.Fatal(err)
	}

	go func() {
		http.Handle("/metrics", promhttp.Handler())
		http.ListenAndServe(":2112", nil)
	}()

	sig := make(chan os.Signal, 1)
	signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)
	<-sig
	client.Stop()
	pub.Publish(context.Background(), []byte("shutdown"))
}
