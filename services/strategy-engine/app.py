"""Strategy engine service."""
from __future__ import annotations

import asyncio
import json
import os
from decimal import Decimal
from typing import Dict, List

import backoff
import pandas as pd
import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException, Request
from shared.validation.fastapi import ValidationMiddleware
from shared.security.auth.fastapi import AuthMiddleware
from pydantic import BaseModel, Field

from .strategies.base import BaseStrategy
from .strategies.loader import load_strategy, LoaderError


class EngineError(Exception):
    """General engine failure."""


def get_redis() -> aioredis.Redis:
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return aioredis.from_url(url)


class StrategyRequest(BaseModel):
    path: str = Field(..., description="Strategy class path")
    params: Dict[str, str] = Field(default_factory=dict)
    position_size: Decimal = Field(..., gt=Decimal("0"))


class StrategyManager:
    def __init__(self) -> None:
        self._strategies: Dict[str, BaseStrategy] = {}

    def add(self, name: str, strat: BaseStrategy) -> None:
        self._strategies[name] = strat

    def list(self) -> List[str]:
        return list(self._strategies)

    def values(self) -> List[BaseStrategy]:
        return list(self._strategies.values())


manager = StrategyManager()
app = FastAPI()
app.state.service_name = os.getenv("SERVICE_NAME", "strategy-engine")
app.add_middleware(AuthMiddleware)
app.add_middleware(ValidationMiddleware, schemas={"/strategies": "strategy_request"})


@app.post("/strategies")
async def add_strategy(req: StrategyRequest, request: Request) -> Dict[str, str]:
    data = request.scope.get("state", {}).get("validated")
    payload = data or req.dict()
    try:
        strat = load_strategy(
            payload["path"],
            payload["path"].split(".")[-1],
            Decimal(payload["position_size"]),
            **payload.get("params", {}),
        )
    except LoaderError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    manager.add(req.path, strat)
    return {"status": "added"}


@app.get("/strategies")
async def list_strategies() -> List[str]:
    return manager.list()


@backoff.on_exception(backoff.expo, aioredis.RedisError, max_tries=3)
async def publish_signal(redis: aioredis.Redis, signal: Dict[str, str]) -> None:
    await redis.publish("signals", json.dumps(signal))


async def listen_market_data() -> None:
    redis = get_redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe("market")
    async for msg in pubsub.listen():
        if msg.get("type") != "message":
            continue
        try:
            data = pd.read_json(msg["data"])
        except ValueError:
            continue
        for strat in manager.values():
            signal = strat.generate_signal(data)
            if signal:
                await publish_signal(redis, signal.__dict__)
