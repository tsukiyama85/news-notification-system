# -*- coding: utf-8 -*-
"""ニュース収集ビジネスロジック."""

from typing import List

from src.infrastructure.cache_manager import CacheManager
from src.infrastructure.google_news_client import GoogleNewsClient
from src.models.news_article import NewsArticle
from src.utils.date_helper import is_today_jst
from src.utils.logger import get_logger

logger = get_logger(__name__)


class NewsCollector:
    """ニュース収集クラス."""

    def __init__(
        self, google_news_client: GoogleNewsClient, cache_manager: CacheManager
    ) -> None:
        """初期化.

        Args:
            google_news_client: Google Newsクライアント
            cache_manager: キャッシュマネージャー
        """
        self.google_news_client = google_news_client
        self.cache_manager = cache_manager

    def collect_news(self, keywords: List[str]) -> List[NewsArticle]:
        """キーワードに基づいてニュースを収集.

        Args:
            keywords: 検索キーワードのリスト

        Returns:
            収集したニュース記事のリスト（当日分のみ、未通知のみ）
        """
        logger.info(f"ニュース収集開始: keywords={keywords}")

        # Google Newsからニュースを取得
        all_articles = self.google_news_client.fetch_news_for_keywords(keywords)

        # 当日のニュースのみフィルタリング
        today_articles = self._filter_today_articles(all_articles)
        logger.info(f"当日のニュース: {len(today_articles)}件")

        # 未通知のニュースのみフィルタリング
        new_articles = self._filter_unnotified_articles(today_articles)
        logger.info(f"未通知のニュース: {len(new_articles)}件")

        return new_articles

    def _filter_today_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """当日のニュースのみフィルタリング.

        Args:
            articles: 記事のリスト

        Returns:
            当日の記事のみのリスト
        """
        today_articles = []
        for article in articles:
            if is_today_jst(article.published_date):
                today_articles.append(article)
            else:
                logger.debug(
                    f"当日以外の記事をスキップ: {article.title} ({article.published_date})"
                )
        return today_articles

    def _filter_unnotified_articles(
        self, articles: List[NewsArticle]
    ) -> List[NewsArticle]:
        """未通知のニュースのみフィルタリング.

        Args:
            articles: 記事のリスト

        Returns:
            未通知の記事のみのリスト
        """
        new_articles = []
        for article in articles:
            url = article.get_url_string()
            if not self.cache_manager.is_notified(url):
                new_articles.append(article)
            else:
                logger.debug(f"通知済みの記事をスキップ: {article.title}")
        return new_articles
