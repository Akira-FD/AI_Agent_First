from __future__ import annotations

import json
import re
import time
import urllib.request
from http.client import RemoteDisconnected
from urllib.error import HTTPError, URLError


class RuleBasedLLMService:
    def backend_label(self) -> str:
        return "local-rule-based-fallback"

    def generate_answer(self, user_query: str, context_text: str, tool_message: str | None = None) -> str:
        summary = self._summarize_context(context_text)
        if tool_message:
            return f"已根据请求执行操作。{tool_message}\n\n建议：{summary or '暂无知识库上下文。'}"
        return f"根据知识库，针对“{user_query}”的建议如下：\n{summary or '暂无可用上下文，请先导入文档。'}"

    def _summarize_context(self, context_text: str) -> str:
        if not context_text.strip():
            return ""

        cleaned_blocks = []
        for block in context_text.split("\n"):
            stripped = block.strip()
            if not stripped:
                continue
            if "GitHub Provenance" in stripped:
                continue
            if stripped.startswith("- Repository:") or stripped.startswith("- Issue:") or stripped.startswith("- URL:"):
                continue
            if stripped.startswith("```") or stripped.startswith("bind ") or stripped.startswith("port ") or stripped.startswith("timeout "):
                continue
            cleaned_blocks.append(stripped)

        prioritized = []
        for block in cleaned_blocks:
            normalized = re.sub(r"^\[[^\]]+\]\s*", "", block)
            if any(keyword in normalized.lower() for keyword in ("建议", "检查", "先看", "maxmemory", "slowlog", "explain", "kubectl", "日志", "连接", "端口", "健康状态")):
                prioritized.append(normalized)

        if not prioritized:
            prioritized = [re.sub(r"^\[[^\]]+\]\s*", "", block) for block in cleaned_blocks]

        unique_lines: list[str] = []
        seen: set[str] = set()
        for line in prioritized:
            compact = re.sub(r"\s+", " ", line).strip()
            if not compact or compact in seen:
                continue
            if len(compact) > 160:
                compact = compact[:157].rstrip() + "..."
            seen.add(compact)
            unique_lines.append(compact)
            if len(unique_lines) >= 3:
                break

        return "；".join(unique_lines)


class OpenAICompatibleLLMService:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        timeout_seconds: int = 30,
        requester=None,
        fallback: RuleBasedLLMService | None = None,
        retry_attempts: int = 2,
        retry_backoff_seconds: float = 0.4,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.requester = requester or self._default_requester
        self.fallback = fallback or RuleBasedLLMService()
        self.retry_attempts = max(1, retry_attempts)
        self.retry_backoff_seconds = max(0.0, retry_backoff_seconds)

    def backend_label(self) -> str:
        return f"openai-compatible:{self.model}"

    def generate_answer(self, user_query: str, context_text: str, tool_message: str | None = None) -> str:
        if not self.api_key:
            return self.fallback.generate_answer(user_query=user_query, context_text=context_text, tool_message=tool_message)

        system_prompt = (
            "你是一个企业研发与运维知识助手。请结合给定上下文，输出简洁、可执行、中文回答。"
            "优先总结关键检查步骤、风险点和建议，不要原样抄录 provenance、长日志或大段配置。"
        )
        user_prompt = (
            f"用户问题：{user_query}\n\n"
            f"工具执行结果：{tool_message or '无'}\n\n"
            f"知识库上下文：\n{context_text or '暂无上下文'}\n\n"
            "请输出：1. 结论 2. 建议步骤 3. 如有必要给出风险提醒。"
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        try:
            response = self._request_with_retry(
                url=f"{self.base_url}/chat/completions",
                headers=headers,
                payload=payload,
                timeout=self.timeout_seconds,
            )
            content = response["choices"][0]["message"]["content"].strip()
            return content or self.fallback.generate_answer(user_query=user_query, context_text=context_text, tool_message=tool_message)
        except Exception:
            return self.fallback.generate_answer(user_query=user_query, context_text=context_text, tool_message=tool_message)

    def _request_with_retry(self, *, url: str, headers: dict[str, str], payload: dict[str, object], timeout: int) -> dict:
        last_error: Exception | None = None
        for attempt in range(1, self.retry_attempts + 1):
            try:
                return self.requester(url=url, headers=headers, payload=payload, timeout=timeout)
            except Exception as exc:
                last_error = exc
                if not self._is_retryable_error(exc) or attempt >= self.retry_attempts:
                    raise
                if self.retry_backoff_seconds:
                    time.sleep(self.retry_backoff_seconds * attempt)
        if last_error:
            raise last_error
        raise RuntimeError("LLM request failed before any attempt was made")

    def _is_retryable_error(self, exc: Exception) -> bool:
        if isinstance(exc, (TimeoutError, RemoteDisconnected)):
            return True
        message = str(exc)
        if "timed out" in message.lower():
            return True
        if "Remote end closed connection" in message:
            return True
        if "HTTP 401" in message or "HTTP 403" in message or "HTTP 404" in message or "HTTP 429" in message:
            return False
        if "HTTP 5" in message:
            return True
        return False

    def _default_requester(self, *, url: str, headers: dict[str, str], payload: dict[str, object], timeout: int) -> dict:
        request = urllib.request.Request(
            url=url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"LLM request failed with HTTP {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError("LLM network request failed") from exc


def build_llm_service(settings, requester=None):
    fallback = RuleBasedLLMService()
    if getattr(settings, "llm_api_key", ""):
        return OpenAICompatibleLLMService(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            timeout_seconds=settings.llm_timeout_seconds,
            requester=requester,
            fallback=fallback,
        )
    return fallback
