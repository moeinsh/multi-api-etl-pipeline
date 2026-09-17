"""Logging setup: structured, human-readable, stdout + optional file."""

import logging
import sys


def setup_logging(log_file=None, level=logging.INFO):
    """Configure root logger. Returns the pipeline logger."""
    fmt = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(level=level, format=fmt, datefmt=datefmt,
                        handlers=handlers, force=True)
    return logging.getLogger("etl")
