# -*- coding: utf-8 -*-
"""NewsArticleモデルのテストコード."""

from datetime import datetime, timezone

import pytest
from pydantic import HttpUrl

from src.models.news_article import NewsArticle


def test_news_article_creation() -> None:
    """NewsArticleの作成テスト."""
    article = NewsArticle(
        title="テストニュース",
        url=HttpUrl("https://example.com/news/1"),
        published_date=datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        description="テスト説明文",
    )

    assert article.title == "テストニュース"
    assert str(article.url) == "https://example.com/news/1"
    assert article.description == "テスト説明文"
    assert article.summary is None
    assert article.relevance_score is None


def test_news_article_with_summary() -> None:
    """要約付きNewsArticleのテスト."""
    article = NewsArticle(
        title="テストニュース",
        url=HttpUrl("https://example.com/news/1"),
        published_date=datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        description="テスト説明文",
        summary="テスト要約",
        relevance_score=0.8,
    )

    assert article.has_summary() is True
    assert article.summary == "テスト要約"
    assert article.relevance_score == 0.8


def test_news_article_no_summary() -> None:
    """要約なしNewsArticleのテスト."""
    article = NewsArticle(
        title="テストニュース",
        url=HttpUrl("https://example.com/news/1"),
        published_date=datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
    )

    assert article.has_summary() is False


def test_get_url_string() -> None:
    """get_url_stringメソッドのテスト."""
    article = NewsArticle(
        title="テストニュース",
        url=HttpUrl("https://example.com/news/1"),
        published_date=datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
    )

    assert article.get_url_string() == "https://example.com/news/1"
