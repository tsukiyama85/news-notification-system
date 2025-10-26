# -*- coding: utf-8 -*-
"""通知ビジネスロジック."""

from typing import List

from src.infrastructure.cache_manager import CacheManager
from src.infrastructure.line_client import LineClient
from src.models.news_article import NewsArticle
from src.models.notification import Notification
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Notifier:
    """通知管理クラス."""

    def __init__(self, line_client: LineClient, cache_manager: CacheManager) -> None:
        """初期化.

        Args:
            line_client: LINEクライアント
            cache_manager: キャッシュマネージャー
        """
        self.line_client = line_client
        self.cache_manager = cache_manager

    def send_notification(
        self, target_name: str, line_user_id: str, articles: List[NewsArticle]
    ) -> None:
        """ニュース記事を通知.

        Args:
            target_name: 通知先の名前
            line_user_id: LINE User ID
            articles: 通知する記事のリスト

        Raises:
            Exception: 通知に失敗した場合
        """
        if not articles:
            logger.info("通知する記事がありません")
            return

        logger.info(
            f"通知送信開始: target={target_name}, user_id={line_user_id}, "
            f"articles={len(articles)}件"
        )

        try:
            # LINE通知を送信
            self.line_client.send_news_notification(
                user_id=line_user_id, articles=articles, target_name=target_name
            )

            # 通知済みURLをキャッシュに追加
            urls = [article.get_url_string() for article in articles]
            self.cache_manager.add_notified_urls(urls)

            logger.info(f"通知送信完了: {len(articles)}件")

        except Exception as e:
            logger.error(f"通知送信エラー: {e}")
            raise

    def send_error_notification(self, line_user_id: str, error_message: str) -> None:
        """エラー通知を送信.

        Args:
            line_user_id: LINE User ID
            error_message: エラーメッセージ

        Raises:
            Exception: 通知に失敗した場合
        """
        logger.info(f"エラー通知送信: user_id={line_user_id}")

        try:
            self.line_client.send_error_notification(
                user_id=line_user_id, error_message=error_message
            )
            logger.info("エラー通知送信完了")
        except Exception as e:
            logger.error(f"エラー通知送信失敗: {e}")
            raise

    def create_notification(
        self, target_name: str, line_user_id: str, articles: List[NewsArticle]
    ) -> Notification:
        """通知データを作成.

        Args:
            target_name: 通知先の名前
            line_user_id: LINE User ID
            articles: 通知する記事のリスト

        Returns:
            通知データ
        """
        notification = Notification(
            target_name=target_name, line_user_id=line_user_id, articles=articles
        )
        logger.debug(
            f"通知データ作成: target={target_name}, articles={len(articles)}件"
        )
        return notification
