# -*- coding: utf-8 -*-
"""LINE Messaging APIを使用した通知クライアント."""

from typing import List

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    FlexBubble,
    FlexButton,
    FlexCarousel,
    FlexContainer,
    FlexMessage,
    MessagingApi,
    PushMessageRequest,
    URIAction,
)
from linebot.v3.messaging.models import FlexBox, FlexText

from src.models.news_article import NewsArticle
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LineClient:
    """LINE Messaging APIクライアント."""

    def __init__(self, channel_access_token: str) -> None:
        """初期化.

        Args:
            channel_access_token: LINEチャンネルアクセストークン
        """
        self.channel_access_token = channel_access_token
        configuration = Configuration(access_token=channel_access_token)
        self.api_client = ApiClient(configuration)
        self.messaging_api = MessagingApi(self.api_client)
        logger.info("LINE Client初期化完了")

    def send_news_notification(
        self, user_id: str, articles: List[NewsArticle], target_name: str
    ) -> None:
        """ニュース記事をFlex Messageで通知.

        Args:
            user_id: LINE User ID
            articles: 通知する記事のリスト
            target_name: 通知先の名前

        Raises:
            Exception: 通知に失敗した場合
        """
        if not articles:
            logger.warning("通知する記事がありません")
            return

        try:
            flex_message = self._create_flex_message(articles, target_name)
            request = PushMessageRequest(to=user_id, messages=[flex_message])
            self.messaging_api.push_message(request)
            logger.info(f"LINE通知送信成功: user_id={user_id}, articles={len(articles)}件")
        except Exception as e:
            logger.error(f"LINE通知送信エラー: {e}")
            raise

    def send_error_notification(self, user_id: str, error_message: str) -> None:
        """エラーメッセージを通知.

        Args:
            user_id: LINE User ID
            error_message: エラーメッセージ

        Raises:
            Exception: 通知に失敗した場合
        """
        try:
            from linebot.v3.messaging import TextMessage

            request = PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=f"❌ エラーが発生しました\n\n{error_message}")],
            )
            self.messaging_api.push_message(request)
            logger.info(f"エラー通知送信成功: user_id={user_id}")
        except Exception as e:
            logger.error(f"エラー通知送信失敗: {e}")
            raise

    def _create_flex_message(
        self, articles: List[NewsArticle], target_name: str
    ) -> FlexMessage:
        """Flex Messageを作成.

        Args:
            articles: 記事のリスト
            target_name: 通知先の名前

        Returns:
            FlexMessage
        """
        # カルーセル形式で最大10件まで
        bubbles = []
        for i, article in enumerate(articles[:10]):
            bubble = self._create_bubble(article, i + 1)
            bubbles.append(bubble)

        carousel = FlexCarousel(contents=bubbles)

        return FlexMessage(
            alt_text=f"{target_name}: {len(articles)}件の新着ニュース", contents=carousel
        )

    def _create_bubble(self, article: NewsArticle, index: int) -> FlexBubble:
        """1記事分のFlex Bubbleを作成.

        Args:
            article: ニュース記事
            index: 記事番号

        Returns:
            FlexBubble
        """
        # タイトル（最大60文字）
        title = article.title[:60] + "..." if len(article.title) > 60 else article.title

        # 要約（最大150文字）
        summary = article.summary or article.description
        summary = summary[:150] + "..." if len(summary) > 150 else summary

        # 公開日時
        from src.utils.date_helper import format_datetime_jst

        published = format_datetime_jst(article.published_date)

        header = FlexBox(
            layout="vertical",
            contents=[
                FlexText(text=f"📰 ニュース #{index}", size="sm", color="#1DB446")
            ],
        )

        body = FlexBox(
            layout="vertical",
            contents=[
                FlexText(text=title, size="lg", weight="bold", wrap=True),
                FlexBox(
                    layout="vertical",
                    margin="md",
                    spacing="sm",
                    contents=[
                        FlexText(text=summary, size="sm", color="#666666", wrap=True),
                        FlexText(text=published, size="xs", color="#999999", margin="md"),
                    ],
                ),
            ],
        )

        footer = FlexBox(
            layout="vertical",
            spacing="sm",
            contents=[
                FlexButton(
                    style="primary",
                    action=URIAction(label="記事を読む", uri=article.get_url_string()),
                )
            ],
        )

        return FlexBubble(header=header, body=body, footer=footer)
