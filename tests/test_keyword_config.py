# -*- coding: utf-8 -*-
"""KeywordConfigモデルのテストコード."""

import pytest

from src.models.keyword_config import KeywordConfig, NotificationTarget


def test_notification_target_creation() -> None:
    """NotificationTargetの作成テスト."""
    target = NotificationTarget(
        name="test_channel",
        line_user_id="U1234567890",
        keywords=["AI", "Python"],
        llm_provider="gemini",
    )

    assert target.name == "test_channel"
    assert target.line_user_id == "U1234567890"
    assert target.keywords == ["AI", "Python"]
    assert target.llm_provider == "gemini"


def test_get_keywords_for_search() -> None:
    """get_keywords_for_searchメソッドのテスト."""
    target = NotificationTarget(
        name="test_channel",
        line_user_id="U1234567890",
        keywords=["AI", "機械学習", "Python"],
        llm_provider="gemini",
    )

    keywords = target.get_keywords_for_search()
    assert keywords == ["AI", "機械学習", "Python"]


def test_keyword_config_creation() -> None:
    """KeywordConfigの作成テスト."""
    config = KeywordConfig(
        notification_targets=[
            NotificationTarget(
                name="channel1",
                line_user_id="U1234567890",
                keywords=["AI", "Python"],
                llm_provider="gemini",
            ),
            NotificationTarget(
                name="channel2",
                line_user_id="U0987654321",
                keywords=["機械学習", "ChatGPT"],
                llm_provider="ollama",
            ),
        ]
    )

    assert len(config.notification_targets) == 2


def test_get_all_keywords() -> None:
    """get_all_keywordsメソッドのテスト."""
    config = KeywordConfig(
        notification_targets=[
            NotificationTarget(
                name="channel1",
                line_user_id="U1234567890",
                keywords=["AI", "Python"],
                llm_provider="gemini",
            ),
            NotificationTarget(
                name="channel2",
                line_user_id="U0987654321",
                keywords=["Python", "機械学習"],
                llm_provider="ollama",
            ),
        ]
    )

    all_keywords = config.get_all_keywords()

    # 重複が除去されている
    assert len(all_keywords) == 3
    assert set(all_keywords) == {"AI", "Python", "機械学習"}


def test_get_target_by_name() -> None:
    """get_target_by_nameメソッドのテスト."""
    config = KeywordConfig(
        notification_targets=[
            NotificationTarget(
                name="channel1",
                line_user_id="U1234567890",
                keywords=["AI", "Python"],
                llm_provider="gemini",
            ),
            NotificationTarget(
                name="channel2",
                line_user_id="U0987654321",
                keywords=["機械学習"],
                llm_provider="ollama",
            ),
        ]
    )

    target = config.get_target_by_name("channel1")
    assert target is not None
    assert target.name == "channel1"
    assert target.line_user_id == "U1234567890"

    # 存在しない名前
    target_none = config.get_target_by_name("channel3")
    assert target_none is None
