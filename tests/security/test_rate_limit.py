from importlib import util
from pathlib import Path
import asyncio
import pytest

spec = util.spec_from_file_location("rl", Path("shared/security/auth/rate_limit.py").resolve())
rl_mod = util.module_from_spec(spec)
spec.loader.exec_module(rl_mod)

@pytest.mark.asyncio
async def test_rate_limiter():
    limiter = rl_mod.RateLimiter(limit=2, window=1)
    assert await limiter.allow("k")
    assert await limiter.allow("k")
    assert not await limiter.allow("k")
    await asyncio.sleep(1)
    assert await limiter.allow("k")
