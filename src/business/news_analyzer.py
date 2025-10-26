# -*- coding: utf-8 -*-
"""ニュース関連性分析ビジネスロジック."""

from typing import List

from src.models.news_article import NewsArticle
from src.utils.logger import get_logger

logger = get_logger(__name__)


class NewsAnalyzer:
    """ニュース関連性分析クラス."""

    def __init__(self) -> None:
        """初期化."""
        pass

    def analyze_relevance(
        self, articles: List[NewsArticle], keywords: List[str]
    ) -> List[NewsArticle]:
        """記事の関連性を分析しスコアを付与.

        Args:
            articles: 記事のリスト
            keywords: キーワードのリスト

        Returns:
            関連性スコア付きの記事のリスト（スコア降順）
        """
        logger.info(f"関連性分析開始: articles={len(articles)}件, keywords={keywords}")

        for article in articles:
            score = self._calculate_relevance_score(article, keywords)
            article.relevance_score = score

        # スコア降順でソート
        sorted_articles = sorted(
            articles, key=lambda x: x.relevance_score or 0.0, reverse=True
        )

        logger.info("関連性分析完了")
        return sorted_articles

    def _calculate_relevance_score(
        self, article: NewsArticle, keywords: List[str]
    ) -> float:
        """記事の関連性スコアを計算.

        Args:
            article: ニュース記事
            keywords: キーワードのリスト

        Returns:
            関連性スコア（0.0〜1.0）
        """
        # タイトルと説明文を結合
        text = f"{article.title} {article.description}".lower()

        # キーワードマッチング
        matched_count = 0
        for keyword in keywords:
            if keyword.lower() in text:
                matched_count += 1

        # スコア計算（マッチしたキーワード数 / 総キーワード数）
        score = matched_count / len(keywords) if keywords else 0.0

        logger.debug(
            f"関連性スコア計算: title={article.title[:30]}..., score={score:.2f}"
        )
        return score

    def filter_by_threshold(
        self, articles: List[NewsArticle], threshold: float = 0.0
    ) -> List[NewsArticle]:
        """関連性スコアの閾値でフィルタリング.

        Args:
            articles: 記事のリスト
            threshold: 閾値（デフォルト: 0.0）

        Returns:
            閾値以上のスコアを持つ記事のリスト
        """
        filtered = [
            article
            for article in articles
            if article.relevance_score is not None
            and article.relevance_score >= threshold
        ]
        logger.info(
            f"閾値フィルタリング: threshold={threshold}, "
            f"before={len(articles)}件, after={len(filtered)}件"
        )
        return filtered
