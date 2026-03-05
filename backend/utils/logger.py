"""Structured logging setup for ChronosGraph."""

import logging
import sys
from pathlib import Path
from config import settings


def setup_logging() -> None:
    log_dir = settings.resolve_path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    root = logging.getLogger("chronosgraph")
    root.setLevel(logging.DEBUG)
    fmt = logging.Formatter("[%(asctime)s] %(levelname)-8s %(name)s — %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)
    root.addHandler(console)
    sys_fh = logging.FileHandler(log_dir / "system.log", encoding="utf-8")
    sys_fh.setLevel(logging.DEBUG)
    sys_fh.setFormatter(fmt)
    root.addHandler(sys_fh)
    err_fh = logging.FileHandler(log_dir / "error.log", encoding="utf-8")
    err_fh.setLevel(logging.ERROR)
    err_fh.setFormatter(fmt)
    root.addHandler(err_fh)
    root.info("Logging initialized — %s", log_dir)
