# -*- coding: utf-8 -*-
"""NewsAnalyzerのテストコード."""

from datetime import datetime, timezone

import pytest
from pydantic import HttpUrl

from src.business.news_analyzer import NewsAnalyzer
from src.models.news_article import NewsArticle


@pytest.fixture
def news_analyzer() -> NewsAnalyzer:
    """NewsAnalyzerのフィクスチャ."""
    return NewsAnalyzer()


@pytest.fixture
def sample_articles() -> list[NewsArticle]:
    """サンプル記事のフィクスチャ."""
    return [
        NewsArticle(
            title="Python機械学習の最新動向",
            url=HttpUrl("https://example.com/news/1"),
            published_date=datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
            description="Pythonを使った機械学習の最新技術について",
        ),
        NewsArticle(
            title="AI技術の未来",
            url=HttpUrl("https://example.com/news/2"),
            published_date=datetime(2025, 1, 15, 13, 0, 0, tzinfo=timezone.utc),
            description="AIが社会に与える影響について考察",
        ),
        NewsArticle(
            title="スポーツニュース",
            url=HttpUrl("https://example.com/news/3"),
            published_date=datetime(2025, 1, 15, 14, 0, 0, tzinfo=timezone.utc),
            description="サッカーの試合結果",
        ),
    ]


def test_analyze_relevance(
    news_analyzer: NewsAnalyzer, sample_articles: list[NewsArticle]
) -> None:
    """関連性分析のテスト."""
    keywords = ["AI", "機械学習", "Python"]

    analyzed = news_analyzer.analyze_relevance(sample_articles, keywords)

    # すべての記事にスコアが付与されている
    for article in analyzed:
        assert article.relevance_score is not None

    # スコア降順でソートされている
    assert analyzed[0].relevance_score >= analyzed[1].relevance_score  # type: ignore
    assert analyzed[1].relevance_score >= analyzed[2].relevance_score  # type: ignore


def test_calculate_relevance_score(
    news_analyzer: NewsAnalyzer, sample_articles: list[NewsArticle]
) -> None:
    """関連性スコア計算のテスト."""
    keywords = ["Python", "機械学習"]

    # 最初の記事はPythonと機械学習の両方を含む
    score1 = news_analyzer._calculate_relevance_score(sample_articles[0], keywords)
    assert score1 == 1.0  # 2/2

    # 2番目の記事はどちらも含まない
    score2 = news_analyzer._calculate_relevance_score(sample_articles[1], keywords)
    assert score2 == 0.0  # 0/2

    # 3番目の記事もどちらも含まない
    score3 = news_analyzer._calculate_relevance_score(sample_articles[2], keywords)
    assert score3 == 0.0


def test_filter_by_threshold(
    news_analyzer: NewsAnalyzer, sample_articles: list[NewsArticle]
) -> None:
    """閾値フィルタリングのテスト."""
    keywords = ["AI", "機械学習"]

    # 関連性スコアを付与
    analyzed = news_analyzer.analyze_relevance(sample_articles, keywords)

    # 閾値0.5でフィルタリング
    filtered = news_analyzer.filter_by_threshold(analyzed, threshold=0.5)

    # スコア0.5以上のものだけが残る
    for article in filtered:
        assert article.relevance_score is not None
        assert article.relevance_score >= 0.5
