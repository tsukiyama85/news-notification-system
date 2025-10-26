# -*- coding: utf-8 -*-
"""ニュース要約ビジネスロジック."""

from typing import List

from src.infrastructure.llm_client import LLMClient
from src.models.news_article import NewsArticle
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Summarizer:
    """ニュース要約クラス."""

    def __init__(self, llm_client: LLMClient) -> None:
        """初期化.

        Args:
            llm_client: LLMクライアント
        """
        self.llm_client = llm_client

    def summarize_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """記事のリストを要約.

        Args:
            articles: 記事のリスト

        Returns:
            要約付きの記事のリスト

        Note:
            要約に失敗した記事はsummaryがNoneのまま
        """
        logger.info(f"要約生成開始: articles={len(articles)}件")

        summarized_count = 0
        failed_count = 0

        for article in articles:
            try:
                # タイトルと説明文を結合して要約
                text = f"{article.title}\n\n{article.description}"
                summary = self.llm_client.summarize(text)
                article.summary = summary
                summarized_count += 1
                logger.debug(f"要約成功: {article.title[:30]}...")
            except Exception as e:
                logger.warning(f"要約失敗: {article.title[:30]}... - {e}")
                article.summary = None
                failed_count += 1

        logger.info(f"要約生成完了: 成功={summarized_count}件, 失敗={failed_count}件")
        return articles

    def summarize_article(self, article: NewsArticle) -> NewsArticle:
        """単一記事を要約.

        Args:
            article: ニュース記事

        Returns:
            要約付きの記事

        Raises:
            Exception: 要約に失敗した場合
        """
        logger.info(f"要約生成: {article.title[:50]}...")

        try:
            text = f"{article.title}\n\n{article.description}"
            summary = self.llm_client.summarize(text)
            article.summary = summary
            logger.info("要約生成成功")
            return article
        except Exception as e:
            logger.error(f"要約生成失敗: {e}")
            raise
