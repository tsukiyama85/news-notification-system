# -*- coding: utf-8 -*-
"""Google News RSSからニュースを取得するクライアント."""

from datetime import datetime
from typing import List
from urllib.parse import quote

import feedparser
from pydantic import HttpUrl

from src.models.news_article import NewsArticle
from src.utils.date_helper import parse_rss_date
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GoogleNewsClient:
    """Google News RSSからニュースを取得するクライアント."""

    BASE_URL = "https://news.google.com/rss/search"

    def __init__(self) -> None:
        """初期化."""
        pass

    def _build_search_url(self, keyword: str, lang: str = "ja", country: str = "JP") -> str:
        """検索URLを構築.

        Args:
            keyword: 検索キーワード
            lang: 言語コード（デフォルト: ja）
            country: 国コード（デフォルト: JP）

        Returns:
            検索URL
        """
        encoded_keyword = quote(keyword)
        return f"{self.BASE_URL}?q={encoded_keyword}&hl={lang}&gl={country}&ceid={country}:{lang}"

    def fetch_news(self, keyword: str) -> List[NewsArticle]:
        """指定キーワードでニュースを取得.

        Args:
            keyword: 検索キーワード

        Returns:
            ニュース記事のリスト
        """
        url = self._build_search_url(keyword)
        logger.info(f"Google Newsからニュースを取得: keyword={keyword}")

        try:
            feed = feedparser.parse(url)

            if feed.bozo:
                logger.warning(f"RSSフィードのパースで問題が発生: {feed.bozo_exception}")

            articles = []
            for entry in feed.entries:
                try:
                    article = self._parse_entry(entry)
                    articles.append(article)
                except Exception as e:
                    logger.warning(f"記事のパースに失敗: {e}, entry={entry.get('title', 'N/A')}")
                    continue

            logger.info(f"{len(articles)}件のニュースを取得しました")
            return articles

        except Exception as e:
            logger.error(f"Google Newsからのニュース取得に失敗: {e}")
            raise

    def _parse_entry(self, entry: feedparser.FeedParserDict) -> NewsArticle:  # type: ignore
        """RSSエントリーをNewsArticleに変換.

        Args:
            entry: feedparserのエントリー

        Returns:
            NewsArticle

        Raises:
            ValueError: 必須フィールドが不足している場合
        """
        title = entry.get("title", "")
        link = entry.get("link", "")
        description = entry.get("summary", "")
        published = entry.get("published", "")

        if not title or not link:
            raise ValueError("titleまたはlinkが不足しています")

        # 日付をパース
        published_date = parse_rss_date(published)
        if published_date is None:
            # パースできない場合は現在時刻を使用
            published_date = datetime.now()
            logger.warning(f"日付のパースに失敗したため現在時刻を使用: {published}")

        return NewsArticle(
            title=title,
            url=HttpUrl(link),
            published_date=published_date,
            description=description,
        )

    def fetch_news_for_keywords(self, keywords: List[str]) -> List[NewsArticle]:
        """複数のキーワードでニュースを取得.

        Args:
            keywords: 検索キーワードのリスト

        Returns:
            ニュース記事のリスト（重複除去済み）
        """
        all_articles = []
        seen_urls = set()

        for keyword in keywords:
            try:
                articles = self.fetch_news(keyword)
                for article in articles:
                    url = article.get_url_string()
                    if url not in seen_urls:
                        all_articles.append(article)
                        seen_urls.add(url)
            except Exception as e:
                logger.error(f"キーワード '{keyword}' のニュース取得に失敗: {e}")
                continue

        logger.info(f"合計{len(all_articles)}件のニュースを取得しました（重複除去済み）")
        return all_articles
