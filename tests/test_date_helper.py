# -*- coding: utf-8 -*-
"""date_helperのテストコード."""

from datetime import datetime, timedelta, timezone

import pytest

from src.utils.date_helper import (
    format_datetime_jst,
    get_jst_now,
    get_today_start_jst,
    is_today_jst,
    parse_rss_date,
)


def test_get_jst_now() -> None:
    """get_jst_nowのテスト."""
    now = get_jst_now()

    # タイムゾーンがJST（UTC+9）であることを確認
    assert now.tzinfo is not None
    assert now.utcoffset() == timedelta(hours=9)


def test_get_today_start_jst() -> None:
    """get_today_start_jstのテスト."""
    today_start = get_today_start_jst()

    # 時刻が00:00:00であることを確認
    assert today_start.hour == 0
    assert today_start.minute == 0
    assert today_start.second == 0
    assert today_start.microsecond == 0

    # タイムゾーンがJSTであることを確認
    assert today_start.tzinfo is not None
    assert today_start.utcoffset() == timedelta(hours=9)


def test_is_today_jst() -> None:
    """is_today_jstのテスト."""
    # 今日の日時
    now = get_jst_now()
    assert is_today_jst(now) is True

    # 昨日の日時
    yesterday = now - timedelta(days=1)
    assert is_today_jst(yesterday) is False

    # 明日の日時
    tomorrow = now + timedelta(days=1)
    assert is_today_jst(tomorrow) is False


def test_parse_rss_date() -> None:
    """parse_rss_dateのテスト."""
    # RFC 2822形式
    date_string = "Wed, 15 Jan 2025 12:00:00 +0000"
    parsed = parse_rss_date(date_string)

    assert parsed is not None
    assert parsed.year == 2025
    assert parsed.month == 1
    assert parsed.day == 15
    assert parsed.hour == 12


def test_parse_rss_date_invalid() -> None:
    """parse_rss_dateの不正な入力テスト."""
    # 不正な形式
    invalid_string = "invalid date"
    parsed = parse_rss_date(invalid_string)

    assert parsed is None


def test_format_datetime_jst() -> None:
    """format_datetime_jstのテスト."""
    dt = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    formatted = format_datetime_jst(dt)

    # JST（UTC+9）に変換されているはず
    assert "2025-01-15 21:00:00 JST" == formatted
