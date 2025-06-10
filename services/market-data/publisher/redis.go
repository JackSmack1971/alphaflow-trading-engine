package publisher

import (
	"context"

	"github.com/go-redis/redis/v8"
)

type Publisher interface {
	Publish(ctx context.Context, msg []byte) error
}

type RedisPublisher struct {
	client  *redis.Client
	channel string
}

func NewRedisPublisher(addr, channel string) *RedisPublisher {
	return &RedisPublisher{client: redis.NewClient(&redis.Options{Addr: addr}), channel: channel}
}

func (p *RedisPublisher) Publish(ctx context.Context, msg []byte) error {
	return p.client.Publish(ctx, p.channel, msg).Err()
}
