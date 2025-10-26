# -*- coding: utf-8 -*-
"""CacheManagerのテストコード."""

import json
import tempfile
from pathlib import Path

import pytest

from src.infrastructure.cache_manager import CacheManager


@pytest.fixture
def temp_cache_file() -> str:
    """一時キャッシュファイルのフィクスチャ."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        temp_file = f.name
    yield temp_file
    # クリーンアップ
    Path(temp_file).unlink(missing_ok=True)


def test_cache_manager_initialization(temp_cache_file: str) -> None:
    """CacheManagerの初期化テスト."""
    cache_manager = CacheManager(cache_file=temp_cache_file)
    assert cache_manager.get_cache_size() == 0


def test_cache_manager_add_url(temp_cache_file: str) -> None:
    """URLの追加テスト."""
    cache_manager = CacheManager(cache_file=temp_cache_file)
    url = "https://example.com/news/1"

    cache_manager.add_notified_url(url)

    assert cache_manager.is_notified(url) is True
    assert cache_manager.get_cache_size() == 1


def test_cache_manager_add_multiple_urls(temp_cache_file: str) -> None:
    """複数URLの追加テスト."""
    cache_manager = CacheManager(cache_file=temp_cache_file)
    urls = [
        "https://example.com/news/1",
        "https://example.com/news/2",
        "https://example.com/news/3",
    ]

    cache_manager.add_notified_urls(urls)

    assert cache_manager.get_cache_size() == 3
    for url in urls:
        assert cache_manager.is_notified(url) is True


def test_cache_manager_persistence(temp_cache_file: str) -> None:
    """キャッシュの永続化テスト."""
    url = "https://example.com/news/1"

    # 最初のインスタンスでURLを追加
    cache_manager1 = CacheManager(cache_file=temp_cache_file)
    cache_manager1.add_notified_url(url)

    # 新しいインスタンスでキャッシュが読み込まれることを確認
    cache_manager2 = CacheManager(cache_file=temp_cache_file)
    assert cache_manager2.is_notified(url) is True
    assert cache_manager2.get_cache_size() == 1


def test_cache_manager_clear(temp_cache_file: str) -> None:
    """キャッシュのクリアテスト."""
    cache_manager = CacheManager(cache_file=temp_cache_file)
    urls = ["https://example.com/news/1", "https://example.com/news/2"]

    cache_manager.add_notified_urls(urls)
    assert cache_manager.get_cache_size() == 2

    cache_manager.clear_cache()
    assert cache_manager.get_cache_size() == 0
    assert cache_manager.is_notified(urls[0]) is False
