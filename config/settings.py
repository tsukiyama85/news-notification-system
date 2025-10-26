# -*- coding: utf-8 -*-
"""環境変数とアプリケーション設定を管理するモジュール."""

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()


class Settings:
    """アプリケーション設定クラス."""

    # LINE設定
    LINE_CHANNEL_ACCESS_TOKEN: str = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")

    # Gemini設定
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Geminiモデル名
    DEFAULT_LLM_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "gemini-2.5-flash")

    # Ollama設定
    OLLAMA_API_URL: str = os.getenv("OLLAMA_API_URL", "http://localhost:11434")

    # LLM設定
    DEFAULT_LLM_PROVIDER: Literal["gemini", "ollama"] = os.getenv(
        "DEFAULT_LLM_PROVIDER", "gemini"
    )  # type: ignore

    # ログ設定
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "data/logs/news_notification.log")

    # キャッシュ設定
    CACHE_FILE: str = os.getenv("CACHE_FILE", "data/cache/notified_urls.json")

    # キーワード設定ファイル
    KEYWORDS_FILE: str = os.getenv("KEYWORDS_FILE", "config/keywords.yaml")

    # プロジェクトルートディレクトリ
    PROJECT_ROOT: Path = Path(__file__).parent.parent

    @classmethod
    def get_absolute_path(cls, relative_path: str) -> Path:
        """相対パスから絶対パスを取得.

        Args:
            relative_path: プロジェクトルートからの相対パス

        Returns:
            絶対パス
        """
        return cls.PROJECT_ROOT / relative_path

    @classmethod
    def validate(cls) -> None:
        """設定の検証を行う.

        Raises:
            ValueError: 必須設定が不足している場合
        """
        if not cls.LINE_CHANNEL_ACCESS_TOKEN:
            raise ValueError("LINE_CHANNEL_ACCESS_TOKENが設定されていません")

        if cls.DEFAULT_LLM_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            raise ValueError(
                "DEFAULT_LLM_PROVIDERがgeminiですが、GEMINI_API_KEYが設定されていません"
            )

        if cls.DEFAULT_LLM_PROVIDER not in ["gemini", "ollama"]:
            raise ValueError(
                f"DEFAULT_LLM_PROVIDERが不正です: {cls.DEFAULT_LLM_PROVIDER}"
            )

        keywords_file_path = cls.get_absolute_path(cls.KEYWORDS_FILE)
        if not keywords_file_path.exists():
            raise ValueError(f"キーワード設定ファイルが存在しません: {keywords_file_path}")


# シングルトンインスタンス
settings = Settings()
