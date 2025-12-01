import logging
from pathlib import Path

def get_logger(module_file: str):
    """
    Returns a logger that logs:
    - to console (root)
    - to a per-module file logs/<module>.log
    """
    module_name = Path(module_file).stem
    logger = logging.getLogger(module_name)

    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Add a file handler if not already present
    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        file_path = logs_dir / f"{module_name}.log"
        fh = logging.FileHandler(file_path, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(fh)
        logger.setLevel(logging.INFO)

    # Prevent logs from propagating to root and duplicating
    logger.propagate = False

    return logger
