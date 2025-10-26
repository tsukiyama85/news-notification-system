# -*- coding: utf-8 -*-
"""ニュース収集・要約・LINE通知システムのメインエントリーポイント."""

import sys

import yaml

from config.settings import settings
from src.business.news_analyzer import NewsAnalyzer
from src.business.news_collector import NewsCollector
from src.business.notifier import Notifier
from src.business.summarizer import Summarizer
from src.infrastructure.cache_manager import CacheManager
from src.infrastructure.google_news_client import GoogleNewsClient
from src.infrastructure.line_client import LineClient
from src.infrastructure.llm_client import LLMClientFactory
from src.models.keyword_config import KeywordConfig
from src.utils.logger import get_logger, setup_logger

setup_logger("", log_file=settings.LOG_FILE, log_level=settings.LOG_LEVEL)
logger = get_logger(__name__)


def load_keyword_config() -> KeywordConfig:
    """キーワード設定ファイルを読み込み.

    Returns:
        キーワード設定

    Raises:
        Exception: 読み込みに失敗した場合
    """
    keywords_file_path = settings.get_absolute_path(settings.KEYWORDS_FILE)
    logger.info(f"キーワード設定ファイルを読み込み: {keywords_file_path}")

    try:
        with open(keywords_file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            config = KeywordConfig(**data)
            logger.info(f"通知先: {len(config.notification_targets)}件")
            return config
    except Exception as e:
        logger.error(f"キーワード設定ファイルの読み込みに失敗: {e}")
        raise


def main() -> None:
    """メイン処理."""
    logger.info("=" * 60)
    logger.info("ニュース収集・要約・LINE通知システム 開始")
    logger.info("=" * 60)

    try:
        # 設定の検証
        logger.info("設定を検証中...")
        settings.validate()
        logger.info("設定検証完了")

        # キーワード設定の読み込み
        keyword_config = load_keyword_config()

        # インフラ層の初期化
        google_news_client = GoogleNewsClient()
        cache_manager = CacheManager(
            cache_file=str(settings.get_absolute_path(settings.CACHE_FILE))
        )
        line_client = LineClient(channel_access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)

        # ビジネスロジック層の初期化
        news_collector = NewsCollector(google_news_client, cache_manager)
        news_analyzer = NewsAnalyzer()

        # 各通知先ごとに処理
        for target in keyword_config.notification_targets:
            logger.info(f"\n{'=' * 60}")
            logger.info(f"通知先処理開始: {target.name}")
            logger.info(f"{'=' * 60}")

            try:
                # 1. ニュース収集
                articles = news_collector.collect_news(target.keywords)

                if not articles:
                    logger.info("新しいニュースがありません")
                    continue

                # 2. 関連性分析
                analyzed_articles = news_analyzer.analyze_relevance(
                    articles, target.keywords
                )

                # 10件に制限（開発用）
                analyzed_articles = analyzed_articles[:10]

                # 3. LLMクライアントの作成
                llm_client = LLMClientFactory.create(
                    provider=target.llm_provider,
                    api_key=settings.GEMINI_API_KEY,
                    api_url=settings.OLLAMA_API_URL,
                    model=settings.DEFAULT_LLM_MODEL,
                )
                summarizer = Summarizer(llm_client)

                # 4. 要約生成
                summarized_articles = summarizer.summarize_articles(analyzed_articles)

                # 5. 通知
                notifier = Notifier(line_client, cache_manager)
                notifier.send_notification(
                    target_name=target.name,
                    line_user_id=target.line_user_id,
                    articles=summarized_articles,
                )

                logger.info(f"通知先処理完了: {target.name}")

            except Exception as e:
                logger.error(f"通知先 '{target.name}' の処理中にエラー発生: {e}")
                # エラー通知を送信
                try:
                    error_notifier = Notifier(line_client, cache_manager)
                    error_notifier.send_error_notification(
                        line_user_id=target.line_user_id,
                        error_message=f"通知先 '{target.name}' の処理中にエラーが発生しました。\n\n{str(e)}",
                    )
                except Exception as notify_error:
                    logger.error(f"エラー通知の送信にも失敗: {notify_error}")

        logger.info("\n" + "=" * 60)
        logger.info("ニュース収集・要約・LINE通知システム 正常終了")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"システムエラー: {e}", exc_info=True)
        logger.info("\n" + "=" * 60)
        logger.info("ニュース収集・要約・LINE通知システム 異常終了")
        logger.info("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
