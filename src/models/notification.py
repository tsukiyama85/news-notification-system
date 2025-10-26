# -*- coding: utf-8 -*-
"""通知のデータモデル."""

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from .news_article import NewsArticle


class Notification(BaseModel):
    """通知データを表すモデル.

    Attributes:
        target_name: 通知先の名前
        line_user_id: LINE User ID
        articles: 通知する記事のリスト
        created_at: 通知作成日時
    """

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )

    target_name: str = Field(..., description="通知先の名前")
    line_user_id: str = Field(..., description="LINE User ID")
    articles: List[NewsArticle] = Field(
        default_factory=list, description="通知する記事のリスト"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="通知作成日時"
    )

    def has_articles(self) -> bool:
        """記事が存在するかチェック.

        Returns:
            記事が1件以上存在する場合True
        """
        return len(self.articles) > 0

    def get_article_count(self) -> int:
        """記事の件数を取得.

        Returns:
            記事の件数
        """
        return len(self.articles)

    def add_article(self, article: NewsArticle) -> None:
        """記事を追加.

        Args:
            article: 追加する記事
        """
        self.articles.append(article)
