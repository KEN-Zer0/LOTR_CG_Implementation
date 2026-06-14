import sys
from datetime import datetime
from pathlib import Path
from typing import TextIO

LOGS_DIR        = Path("logs")
_LOG_PREFIX     = "game-log"
_LOG_GLOB       = f"{_LOG_PREFIX}-*.txt"
_LOG_DT_FORMAT  = "%d-%m-%Y-%H-%M"


def default_log_path() -> Path:
    """Return an auto-generated log path and ensure the logs directory exists."""
    LOGS_DIR.mkdir(exist_ok=True)
    log_id = len(list(LOGS_DIR.glob(_LOG_GLOB))) + 1
    dt = datetime.now().strftime(_LOG_DT_FORMAT)
    return LOGS_DIR / f"{_LOG_PREFIX}-{log_id:04d}-{dt}.txt"


class Logger:
    """Global toggle for verbose game logging. Call Logger.enable() to activate."""

    _enabled: bool = False
    _file: TextIO | None = None

    @classmethod
    def enable(cls, file_path: str | Path | None = None) -> None:
        cls._enabled = True
        if file_path:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            cls._file = open(path, "w", encoding="utf-8")
            cls._file.write(path.name + "\n")
        else:
            cls._file = None
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")

    @classmethod
    def log(cls, message: str = "") -> None:
        if cls._enabled:
            if cls._file:
                cls._file.write(message + "\n")
            else:
                print(message)

    @classmethod
    def close(cls) -> None:
        if cls._file:
            cls._file.close()
            cls._file = None
        cls._enabled = False
