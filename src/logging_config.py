import logging
import os
from pathlib import Path


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # すでに handler があれば二重登録しない
    if logger.handlers:
        return

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )

    # 共通：コンソール出力（stdout）
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Lambda 実行判定
    is_lambda = os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None

    if not is_lambda:
        # ローカルのみ：ファイル出力
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(
            log_dir / "app.log", encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
