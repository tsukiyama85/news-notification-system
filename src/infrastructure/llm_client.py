# -*- coding: utf-8 -*-
"""LLM API（Gemini/Ollama）を使用した要約生成クライアント."""

from abc import ABC, abstractmethod
from typing import Literal

import requests
from google import genai

from src.utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient(ABC):
    """LLMクライアントの抽象基底クラス."""

    @abstractmethod
    def summarize(self, text: str) -> str:
        """テキストを要約.

        Args:
            text: 要約対象のテキスト

        Returns:
            要約文

        Raises:
            Exception: 要約に失敗した場合
        """
        pass


class GeminiClient(LLMClient):
    """Google Gemini APIを使用した要約クライアント."""

    def __init__(self, api_key: str, model: str = "gemini-pro") -> None:
        """初期化.

        Args:
            api_key: Gemini APIキー
            model: 使用するモデル名
        """
        self.api_key = api_key
        self.model_name = model
        self.client = genai.Client(api_key=api_key)
        logger.info(f"Gemini Client初期化完了: model={model}")

    def summarize(self, text: str) -> str:
        """テキストを要約.

        Args:
            text: 要約対象のテキスト

        Returns:
            要約文

        Raises:
            Exception: 要約に失敗した場合
        """
        prompt = f"""以下のニュース記事を日本語で簡潔に要約してください。
        3〜5文程度で、重要なポイントを含めてまとめてください。

        記事:
        {text}

        要約:"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name, contents=prompt
            )
            summary = response.text.strip()
            logger.debug(f"Geminiで要約生成成功: length={len(summary)}")
            return summary
        except Exception as e:
            logger.error(f"Gemini要約生成エラー: {e}")
            raise


class OllamaClient(LLMClient):
    """Ollama APIを使用した要約クライアント."""

    def __init__(self, api_url: str, model: str = "llama2") -> None:
        """初期化.

        Args:
            api_url: Ollama APIのURL
            model: 使用するモデル名
        """
        self.api_url = api_url.rstrip("/")
        self.model_name = model
        logger.info(f"Ollama Client初期化完了: url={api_url}, model={model}")

    def summarize(self, text: str) -> str:
        """テキストを要約.

        Args:
            text: 要約対象のテキスト

        Returns:
            要約文

        Raises:
            Exception: 要約に失敗した場合
        """
        prompt = f"""以下のニュース記事を日本語で簡潔に要約してください。
3〜5文程度で、重要なポイントを含めてまとめてください。

記事:
{text}

要約:"""

        try:
            response = requests.post(
                f"{self.api_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            summary = result.get("response", "").strip()

            if not summary:
                raise ValueError("Ollamaからの応答が空です")

            logger.debug(f"Ollamaで要約生成成功: length={len(summary)}")
            return summary
        except Exception as e:
            logger.error(f"Ollama要約生成エラー: {e}")
            raise


class LLMClientFactory:
    """LLMクライアントのファクトリークラス."""

    @staticmethod
    def create(
        provider: Literal["gemini", "ollama"],
        api_key: str = "",
        api_url: str = "http://localhost:11434",
        model: str = "",
    ) -> LLMClient:
        """LLMクライアントを生成.

        Args:
            provider: LLMプロバイダー（gemini または ollama）
            api_key: APIキー（Gemini用）
            api_url: APIのURL（Ollama用）
            model: モデル名（オプション）

        Returns:
            LLMClient

        Raises:
            ValueError: 不正なプロバイダーが指定された場合
        """
        if provider == "gemini":
            if not api_key:
                raise ValueError("Gemini使用時はapi_keyが必須です")
            model_name = model or "gemini-2.5-flash"
            return GeminiClient(api_key=api_key, model=model_name)
        elif provider == "ollama":
            model_name = model or "llama2"
            return OllamaClient(api_url=api_url, model=model_name)
        else:
            raise ValueError(f"不正なLLMプロバイダー: {provider}")
