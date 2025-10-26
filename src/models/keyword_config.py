# -*- coding: utf-8 -*-
"""キーワード設定のデータモデル."""

from typing import List, Literal

from pydantic import BaseModel, Field


class NotificationTarget(BaseModel):
    """通知先の設定を表すデータモデル.

    Attributes:
        name: 通知先の名前
        line_user_id: LINE User ID
        keywords: 検索キーワードのリスト
        llm_provider: 使用するLLMプロバイダー（gemini または ollama）
    """

    name: str = Field(..., description="通知先の名前")
    line_user_id: str = Field(..., description="LINE User ID")
    keywords: List[str] = Field(..., min_length=1, description="検索キーワードリスト")
    llm_provider: Literal["gemini", "ollama"] = Field(
        default="gemini", description="LLMプロバイダー"
    )

    def get_keywords_for_search(self) -> List[str]:
        """検索用のキーワードリストを取得.

        Returns:
            キーワードのリスト
        """
        return self.keywords


class KeywordConfig(BaseModel):
    """キーワード設定全体を表すデータモデル.

    Attributes:
        notification_targets: 通知先のリスト
    """

    notification_targets: List[NotificationTarget] = Field(
        ..., min_length=1, description="通知先のリスト"
    )

    def get_all_keywords(self) -> List[str]:
        """すべての通知先からキーワードを取得.

        Returns:
            重複を除いたキーワードのリスト
        """
        all_keywords = []
        for target in self.notification_targets:
            all_keywords.extend(target.keywords)
        return list(set(all_keywords))

    def get_target_by_name(self, name: str) -> NotificationTarget | None:
        """名前で通知先を取得.

        Args:
            name: 通知先の名前

        Returns:
            通知先、存在しない場合はNone
        """
        for target in self.notification_targets:
            if target.name == name:
                return target
        return None
