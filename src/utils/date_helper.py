# -*- coding: utf-8 -*-
"""日付処理のユーティリティモジュール."""

from datetime import datetime, timedelta, timezone
from typing import Optional


def get_jst_now() -> datetime:
    """現在のJST日時を取得.

    Returns:
        現在のJST日時（タイムゾーン情報付き）
    """
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst)


def get_today_start_jst() -> datetime:
    """今日の開始時刻（00:00:00）をJSTで取得.

    Returns:
        今日の00:00:00のJST日時
    """
    now = get_jst_now()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def is_today_jst(dt: datetime) -> bool:
    """指定された日時が今日（JST）かどうか判定.

    Args:
        dt: 判定する日時

    Returns:
        今日の場合True
    """
    today_start = get_today_start_jst()
    tomorrow_start = today_start + timedelta(days=1)

    # タイムゾーンを考慮して比較
    if dt.tzinfo is None:
        # タイムゾーン情報がない場合はUTCとみなす
        dt = dt.replace(tzinfo=timezone.utc)

    return today_start <= dt < tomorrow_start


def parse_rss_date(date_string: str) -> Optional[datetime]:
    """RSS日付文字列をdatetimeに変換.

    Args:
        date_string: RSS日付文字列（RFC 2822形式など）

    Returns:
        datetime、パースできない場合はNone
    """
    from email.utils import parsedate_to_datetime

    try:
        return parsedate_to_datetime(date_string)
    except (ValueError, TypeError):
        return None


def format_datetime_jst(dt: datetime) -> str:
    """日時をJST形式の文字列にフォーマット.

    Args:
        dt: フォーマットする日時

    Returns:
        フォーマット済み文字列（例: 2025-01-15 14:30:00 JST）
    """
    jst = timezone(timedelta(hours=9))
    dt_jst = dt.astimezone(jst)
    return dt_jst.strftime("%Y-%m-%d %H:%M:%S JST")
