# -*- coding: utf-8 -*-
"""通知済みニュースのキャッシュ管理モジュール."""

import json
from pathlib import Path
from typing import Set

from src.utils.logger import get_logger

logger = get_logger(__name__)


class CacheManager:
    """通知済みURLを管理するキャッシュマネージャー."""

    def __init__(self, cache_file: str) -> None:
        """初期化.

        Args:
            cache_file: キャッシュファイルのパス
        """
        self.cache_file = Path(cache_file)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self._notified_urls: Set[str] = self._load_cache()

    def _load_cache(self) -> Set[str]:
        """キャッシュファイルから通知済みURLを読み込み.

        Returns:
            通知済みURLのセット
        """
        if not self.cache_file.exists():
            logger.info(f"キャッシュファイルが存在しないため新規作成します: {self.cache_file}")
            return set()

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                urls = set(data.get("notified_urls", []))
                logger.info(f"キャッシュから{len(urls)}件のURLを読み込みました")
                return urls
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"キャッシュファイルの読み込みに失敗しました: {e}")
            return set()

    def _save_cache(self) -> None:
        """キャッシュファイルに通知済みURLを保存."""
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"notified_urls": list(self._notified_urls)},
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
            logger.debug(f"キャッシュを保存しました: {len(self._notified_urls)}件")
        except IOError as e:
            logger.error(f"キャッシュファイルの保存に失敗しました: {e}")

    def is_notified(self, url: str) -> bool:
        """指定されたURLが通知済みかチェック.

        Args:
            url: チェックするURL

        Returns:
            通知済みの場合True
        """
        return url in self._notified_urls

    def add_notified_url(self, url: str) -> None:
        """通知済みURLを追加.

        Args:
            url: 追加するURL
        """
        self._notified_urls.add(url)
        self._save_cache()
        logger.debug(f"通知済みURLを追加: {url}")

    def add_notified_urls(self, urls: list[str]) -> None:
        """複数の通知済みURLを追加.

        Args:
            urls: 追加するURLのリスト
        """
        self._notified_urls.update(urls)
        self._save_cache()
        logger.info(f"{len(urls)}件の通知済みURLを追加しました")

    def clear_cache(self) -> None:
        """キャッシュをクリア."""
        self._notified_urls.clear()
        self._save_cache()
        logger.info("キャッシュをクリアしました")

    def get_cache_size(self) -> int:
        """キャッシュに保存されているURL数を取得.

        Returns:
            URL数
        """
        return len(self._notified_urls)
