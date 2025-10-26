# -*- coding: utf-8 -*-
"""ニュース記事のデータモデル."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class NewsArticle(BaseModel):
    """ニュース記事を表すデータモデル.

    Attributes:
        title: 記事のタイトル
        url: 記事のURL
        published_date: 公開日時
        description: 記事の説明文
        summary: LLMによる要約文（オプション）
        relevance_score: キーワードとの関連性スコア（オプション）
    """

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            HttpUrl: lambda v: str(v),
        }
    )

    title: str = Field(..., description="記事のタイトル")
    url: HttpUrl = Field(..., description="記事のURL")
    published_date: datetime = Field(..., description="公開日時")
    description: str = Field(default="", description="記事の説明文")
    summary: Optional[str] = Field(default=None, description="LLMによる要約文")
    relevance_score: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="関連性スコア"
    )

    def has_summary(self) -> bool:
        """要約が生成されているかチェック.

        Returns:
            要約が存在する場合True
        """
        return self.summary is not None and len(self.summary) > 0

    def get_url_string(self) -> str:
        """URLを文字列として取得.

        Returns:
            URL文字列
        """
        return str(self.url)
