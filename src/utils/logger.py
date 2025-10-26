# -*- coding: utf-8 -*-
"""ログ設定モジュール."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "",
    log_file: Optional[str] = None,
    log_level: str = "INFO",
) -> logging.Logger:
    """ロガーをセットアップ.

    Args:
        name: ロガーの名前（空文字列の場合はルートロガー、デフォルト: ""）
        log_file: ログファイルのパス（オプション）
        log_level: ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）

    Returns:
        設定済みのLogger

    Note:
        nameを空文字列にすると、ルートロガーが設定され、
        すべての子ロガーが自動的にこの設定を継承します。
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # 既存のハンドラーをクリア
    logger.handlers.clear()

    # フォーマッター
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # コンソールハンドラー
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ファイルハンドラー（オプション）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # ルートロガーの場合は伝播を無効化
    if name == "":
        logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """既存のロガーを取得.

    Args:
        name: ロガーの名前

    Returns:
        Logger
    """
    return logging.getLogger(name)
