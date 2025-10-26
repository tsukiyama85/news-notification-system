# -*- coding: utf-8 -*-
"""loggerモジュールのテストコード."""

import logging
import tempfile
from pathlib import Path

import pytest

from src.utils.logger import get_logger, setup_logger


def test_setup_logger_basic() -> None:
    """基本的なロガーのセットアップテスト."""
    logger = setup_logger("test_logger", log_level="DEBUG")

    assert logger.name == "test_logger"
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) >= 1  # コンソールハンドラーが存在


def test_setup_root_logger() -> None:
    """ルートロガーのセットアップテスト."""
    logger = setup_logger("", log_level="INFO")

    assert logger.name == "root"
    assert logger.level == logging.INFO
    assert len(logger.handlers) >= 1


def test_setup_logger_with_file() -> None:
    """ファイルハンドラー付きロガーのテスト."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
        temp_log = f.name

    try:
        logger = setup_logger("test_file_logger", log_file=temp_log, log_level="WARNING")

        assert logger.level == logging.WARNING
        assert len(logger.handlers) == 2  # コンソール + ファイル

        # ログファイルが作成されることを確認
        assert Path(temp_log).exists()
    finally:
        Path(temp_log).unlink(missing_ok=True)


def test_get_logger() -> None:
    """get_loggerのテスト."""
    # まずセットアップ
    setup_logger("test_get", log_level="ERROR")

    # 取得
    logger = get_logger("test_get")

    assert logger.name == "test_get"
    assert logger.level == logging.ERROR


def test_child_logger_inherits_root() -> None:
    """子ロガーがルートロガーの設定を継承することのテスト."""
    # ルートロガーをセットアップ
    root_logger = setup_logger("", log_level="DEBUG")

    # 子ロガーを取得
    child_logger = get_logger("src.business.test")

    # 子ロガーはルートロガーのハンドラーを使用
    assert child_logger.name == "src.business.test"

    # ログレベルは継承される（明示的に設定されていない場合）
    # 子ロガーは親のハンドラーにログを伝播する
    assert len(root_logger.handlers) >= 1


def test_logger_levels() -> None:
    """各ログレベルのテスト."""
    levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    for level in levels:
        logger = setup_logger(f"test_{level.lower()}", log_level=level)
        assert logger.level == getattr(logging, level)


def test_logger_clear_handlers() -> None:
    """ハンドラーがクリアされることのテスト."""
    logger_name = "test_clear"

    # 最初のセットアップ
    logger1 = setup_logger(logger_name, log_level="INFO")
    handler_count_1 = len(logger1.handlers)

    # 再度セットアップ（ハンドラーはクリアされるべき）
    logger2 = setup_logger(logger_name, log_level="DEBUG")
    handler_count_2 = len(logger2.handlers)

    # ハンドラーが重複していない
    assert handler_count_1 == handler_count_2
