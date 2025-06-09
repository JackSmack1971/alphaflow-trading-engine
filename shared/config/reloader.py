"""Config hot reloading utility."""
from __future__ import annotations

import asyncio
from typing import Any, Callable, Dict

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .loader import ConfigLoader


class ConfigReloader(FileSystemEventHandler):
    """Watch config file and reload on change."""

    def __init__(self, loader: ConfigLoader, callback: Callable[[Dict[str, Any]], None]):
        self._loader = loader
        self._callback = callback
        self._observer = Observer()

    def start(self) -> None:
        path = self._loader.config_dir / f"{self._loader.env}.yaml"
        self._observer.schedule(self, path=path.parent, recursive=False)
        self._observer.start()

    def stop(self) -> None:
        self._observer.stop()
        self._observer.join()

    def on_modified(self, event) -> None:  # type: ignore[override]
        if not event.is_directory:
            asyncio.create_task(self._reload())

    async def _reload(self) -> None:
        cfg = await self._loader.load()
        self._callback(cfg)
