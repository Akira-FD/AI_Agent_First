from __future__ import annotations

import json
import re
import time
import urllib.request
from dataclasses import dataclass
from http.client import RemoteDisconnected
from urllib.error import HTTPError, URLError


@dataclass(frozen=True)
class LLMStreamEvent:
    type: str
    delta: str = ""
    result: "LLMAnswerResult | None" = None


@dataclass(frozen=True)
class LLMAnswerResult:
    answer: str
    answer_backend: str
    provider_status: str = "not_used"
    provider_error: str = ""
    provider_attempts: int = 0
    first_token_latency_ms: int = 0
    total_latency_ms: int = 0
    provider_diagnostic: str = ""


class RuleBasedLLMService:
    def backend_label(self) -> str:
        return "local-rule-based-fallback"

    def generate_answer_result(self, user_query: str, context_text: str, tool_message: str | None = None) -> LLMAnswerResult:
        summary = self._summarize_context(context_text)
        if tool_message:
            return LLMAnswerResult(
                answer=f"已根据请求执行操作。{tool_message}\n\n建议：{summary or '暂无知识库上下文。'}",
                answer_backend="fallback",
                provider_status="not_used",
                provider_diagnostic=_build_provider_diagnostic(
                    provider_status="not_used",
                    provider_attempts=0,
                    first_token_latency_ms=0,
                    total_latency_ms=0,
                    provider_error="",
                ),
            )
        return LLMAnswerResult(
            answer=f"根据知识库，针对“{user_query}”的建议如下：\n{summary or '暂无可用上下文，请先导入文档。'}",
            answer_backend="fallback",
            provider_status="not_used",
            provider_diagnostic=_build_provider_diagnostic(
                provider_status="not_used",
                provider_attempts=0,
                first_token_latency_ms=0,
                total_latency_ms=0,
                provider_error="",
            ),
        )

    def generate_answer(self, user_query: str, context_text: str, tool_message: str | None = None) -> str:
        return self.generate_answer_result(
            user_query=user_query,
            context_text=context_text,
            tool_message=tool_message,
        ).answer

    def stream_answer_result(self, user_query: str, context_text: str, tool_message: str | None = None):
        result = self.generate_answer_result(
            user_query=user_query,
            context_text=context_text,
            tool_message=tool_message,
        )
        if result.answer:
            yield LLMStreamEvent(type="delta", delta=result.answer)
        yield LLMStreamEvent(type="done", result=result)

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
        stream_requester=None,
        fallback: RuleBasedLLMService | None = None,
        retry_attempts: int = 2,
        retry_backoff_seconds: float = 0.4,
        context_max_chars: int = 1400,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.requester = requester or self._default_requester
        self.stream_requester = stream_requester or self._default_stream_requester
        self.fallback = fallback or RuleBasedLLMService()
        self.retry_attempts = max(1, retry_attempts)
        self.retry_backoff_seconds = max(0.0, retry_backoff_seconds)
        self.context_max_chars = max(200, context_max_chars)
        self.context_line_max_chars = 180
        self.tool_message_max_chars = 360
        self._last_provider_status = "not_started"
        self._last_provider_error = ""
        self._last_provider_attempts = 0
        self._last_first_token_latency_ms = 0
        self._last_total_latency_ms = 0

    def backend_label(self) -> str:
        return f"openai-compatible:{self.model}"

    def generate_answer(self, user_query: str, context_text: str, tool_message: str | None = None) -> str:
        return self.generate_answer_result(
            user_query=user_query,
            context_text=context_text,
            tool_message=tool_message,
        ).answer

    def generate_answer_result(self, user_query: str, context_text: str, tool_message: str | None = None) -> LLMAnswerResult:
        started_at = time.monotonic()
        if not self.api_key:
            fallback_result = self.fallback.generate_answer_result(
                user_query=user_query,
                context_text=context_text,
                tool_message=tool_message,
            )
            return LLMAnswerResult(
                answer=fallback_result.answer,
                answer_backend="fallback",
                provider_status="missing_api_key",
                provider_error="AI_AGENT_FIRST_LLM_API_KEY/OPENAI_API_KEY missing",
                provider_attempts=0,
                first_token_latency_ms=0,
                total_latency_ms=0,
                provider_diagnostic=_build_provider_diagnostic(
                    provider_status="missing_api_key",
                    provider_attempts=0,
                    first_token_latency_ms=0,
                    total_latency_ms=0,
                    provider_error="AI_AGENT_FIRST_LLM_API_KEY/OPENAI_API_KEY missing",
                ),
            )

        payload = {
            "model": self.model,
            "messages": self._build_messages(
                user_query=user_query,
                context_text=context_text,
                tool_message=tool_message,
            ),
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
            content = self._extract_message_content(response)
            total_latency_ms = _elapsed_ms(started_at)
            if content:
                self._last_provider_status = "success"
                self._last_provider_error = ""
                self._last_first_token_latency_ms = total_latency_ms
                self._last_total_latency_ms = total_latency_ms
                return LLMAnswerResult(
                    answer=content,
                    answer_backend="remote",
                    provider_status="success",
                    provider_error="",
                    provider_attempts=self._last_provider_attempts,
                    first_token_latency_ms=total_latency_ms,
                    total_latency_ms=total_latency_ms,
                    provider_diagnostic=_build_provider_diagnostic(
                        provider_status="success",
                        provider_attempts=self._last_provider_attempts,
                        first_token_latency_ms=total_latency_ms,
                        total_latency_ms=total_latency_ms,
                        provider_error="",
                    ),
                )
            fallback_result = self.fallback.generate_answer_result(
                user_query=user_query,
                context_text=context_text,
                tool_message=tool_message,
            )
            self._last_first_token_latency_ms = 0
            self._last_total_latency_ms = total_latency_ms
            return LLMAnswerResult(
                answer=fallback_result.answer,
                answer_backend="fallback",
                provider_status="empty_response",
                provider_error="provider returned empty content",
                provider_attempts=self._last_provider_attempts,
                first_token_latency_ms=0,
                total_latency_ms=total_latency_ms,
                provider_diagnostic=_build_provider_diagnostic(
                    provider_status="empty_response",
                    provider_attempts=self._last_provider_attempts,
                    first_token_latency_ms=0,
                    total_latency_ms=total_latency_ms,
                    provider_error="provider returned empty content",
                ),
            )
        except Exception:
            fallback_result = self.fallback.generate_answer_result(
                user_query=user_query,
                context_text=context_text,
                tool_message=tool_message,
            )
            total_latency_ms = _elapsed_ms(started_at)
            self._last_first_token_latency_ms = 0
            self._last_total_latency_ms = total_latency_ms
            return LLMAnswerResult(
                answer=fallback_result.answer,
                answer_backend="fallback",
                provider_status=self._last_provider_status,
                provider_error=self._last_provider_error,
                provider_attempts=self._last_provider_attempts,
                first_token_latency_ms=0,
                total_latency_ms=total_latency_ms,
                provider_diagnostic=_build_provider_diagnostic(
                    provider_status=self._last_provider_status,
                    provider_attempts=self._last_provider_attempts,
                    first_token_latency_ms=0,
                    total_latency_ms=total_latency_ms,
                    provider_error=self._last_provider_error,
                ),
            )

    def stream_answer_result(self, user_query: str, context_text: str, tool_message: str | None = None):
        started_at = time.monotonic()
        if not self.api_key:
            fallback_result = self.fallback.generate_answer_result(
                user_query=user_query,
                context_text=context_text,
                tool_message=tool_message,
            )
            if fallback_result.answer:
                yield LLMStreamEvent(type="delta", delta=fallback_result.answer)
            yield LLMStreamEvent(
                type="done",
                result=LLMAnswerResult(
                    answer=fallback_result.answer,
                    answer_backend="fallback",
                    provider_status="missing_api_key",
                    provider_error="AI_AGENT_FIRST_LLM_API_KEY/OPENAI_API_KEY missing",
                    provider_attempts=0,
                    first_token_latency_ms=0,
                    total_latency_ms=0,
                    provider_diagnostic=_build_provider_diagnostic(
                        provider_status="missing_api_key",
                        provider_attempts=0,
                        first_token_latency_ms=0,
                        total_latency_ms=0,
                        provider_error="AI_AGENT_FIRST_LLM_API_KEY/OPENAI_API_KEY missing",
                    ),
                ),
            )
            return

        payload = {
            "model": self.model,
            "messages": self._build_messages(
                user_query=user_query,
                context_text=context_text,
                tool_message=tool_message,
            ),
            "temperature": 0.2,
            "stream": True,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        collected_parts: list[str] = []
        first_token_latency_ms = 0
        try:
            for delta in self._stream_request_with_retry(
                url=f"{self.base_url}/chat/completions",
                headers=headers,
                payload=payload,
                timeout=self.timeout_seconds,
            ):
                if not delta:
                    continue
                if first_token_latency_ms == 0:
                    first_token_latency_ms = _elapsed_ms(started_at)
                collected_parts.append(delta)
                yield LLMStreamEvent(type="delta", delta=delta)
            content = "".join(collected_parts).strip()
            total_latency_ms = _elapsed_ms(started_at)
            if content:
                self._last_first_token_latency_ms = first_token_latency_ms
                self._last_total_latency_ms = total_latency_ms
                yield LLMStreamEvent(
                    type="done",
                    result=LLMAnswerResult(
                        answer=content,
                        answer_backend="remote",
                        provider_status="success",
                        provider_error="",
                        provider_attempts=self._last_provider_attempts,
                        first_token_latency_ms=first_token_latency_ms,
                        total_latency_ms=total_latency_ms,
                        provider_diagnostic=_build_provider_diagnostic(
                            provider_status="success",
                            provider_attempts=self._last_provider_attempts,
                            first_token_latency_ms=first_token_latency_ms,
                            total_latency_ms=total_latency_ms,
                            provider_error="",
                        ),
                    ),
                )
                return
            fallback_result = self.fallback.generate_answer_result(
                user_query=user_query,
                context_text=context_text,
                tool_message=tool_message,
            )
            self._last_first_token_latency_ms = first_token_latency_ms
            self._last_total_latency_ms = total_latency_ms
            yield LLMStreamEvent(
                type="done",
                result=LLMAnswerResult(
                    answer=fallback_result.answer,
                    answer_backend="fallback",
                    provider_status="empty_response",
                    provider_error="provider returned empty content",
                    provider_attempts=self._last_provider_attempts,
                    first_token_latency_ms=first_token_latency_ms,
                    total_latency_ms=total_latency_ms,
                    provider_diagnostic=_build_provider_diagnostic(
                        provider_status="empty_response",
                        provider_attempts=self._last_provider_attempts,
                        first_token_latency_ms=first_token_latency_ms,
                        total_latency_ms=total_latency_ms,
                        provider_error="provider returned empty content",
                    ),
                ),
            )
        except Exception:
            fallback_result = self.fallback.generate_answer_result(
                user_query=user_query,
                context_text=context_text,
                tool_message=tool_message,
            )
            total_latency_ms = _elapsed_ms(started_at)
            self._last_first_token_latency_ms = first_token_latency_ms
            self._last_total_latency_ms = total_latency_ms
            if fallback_result.answer:
                yield LLMStreamEvent(type="delta", delta=fallback_result.answer)
            yield LLMStreamEvent(
                type="done",
                result=LLMAnswerResult(
                    answer=fallback_result.answer,
                    answer_backend="fallback",
                    provider_status=self._last_provider_status,
                    provider_error=self._last_provider_error,
                    provider_attempts=self._last_provider_attempts,
                    first_token_latency_ms=first_token_latency_ms,
                    total_latency_ms=total_latency_ms,
                    provider_diagnostic=_build_provider_diagnostic(
                        provider_status=self._last_provider_status,
                        provider_attempts=self._last_provider_attempts,
                        first_token_latency_ms=first_token_latency_ms,
                        total_latency_ms=total_latency_ms,
                        provider_error=self._last_provider_error,
                    ),
                ),
            )

    def _request_with_retry(self, *, url: str, headers: dict[str, str], payload: dict[str, object], timeout: int) -> dict:
        last_error: Exception | None = None
        self._last_provider_status = "not_started"
        self._last_provider_error = ""
        self._last_provider_attempts = 0
        self._last_first_token_latency_ms = 0
        self._last_total_latency_ms = 0
        for attempt in range(1, self.retry_attempts + 1):
            self._last_provider_attempts = attempt
            try:
                response = self.requester(url=url, headers=headers, payload=payload, timeout=timeout)
                return response
            except Exception as exc:
                last_error = exc
                self._last_provider_status = self._classify_provider_error(exc)
                self._last_provider_error = str(exc)
                if not self._is_retryable_error(exc) or attempt >= self.retry_attempts:
                    raise
                if self.retry_backoff_seconds:
                    time.sleep(self.retry_backoff_seconds * attempt)
        if last_error:
            raise last_error
        raise RuntimeError("LLM request failed before any attempt was made")

    def _stream_request_with_retry(self, *, url: str, headers: dict[str, str], payload: dict[str, object], timeout: int):
        last_error: Exception | None = None
        self._last_provider_status = "not_started"
        self._last_provider_error = ""
        self._last_provider_attempts = 0
        self._last_first_token_latency_ms = 0
        self._last_total_latency_ms = 0
        for attempt in range(1, self.retry_attempts + 1):
            self._last_provider_attempts = attempt
            try:
                stream = self.stream_requester(url=url, headers=headers, payload=payload, timeout=timeout)
                for delta in self._iter_sse_content(stream):
                    yield delta
                self._last_provider_status = "success"
                self._last_provider_error = ""
                return
            except Exception as exc:
                last_error = exc
                self._last_provider_status = self._classify_provider_error(exc)
                self._last_provider_error = str(exc)
                if not self._is_retryable_error(exc) or attempt >= self.retry_attempts:
                    raise
                if self.retry_backoff_seconds:
                    time.sleep(self.retry_backoff_seconds * attempt)
        if last_error:
            raise last_error
        raise RuntimeError("LLM stream request failed before any attempt was made")

    def _iter_sse_content(self, stream):
        for raw_chunk in stream:
            if isinstance(raw_chunk, bytes):
                text = raw_chunk.decode("utf-8")
            else:
                text = str(raw_chunk)
            for line in text.splitlines():
                stripped = line.strip()
                if not stripped.startswith("data:"):
                    continue
                data = stripped[5:].strip()
                if data == "[DONE]":
                    return
                if not data:
                    continue
                payload = json.loads(data)
                choices = payload.get("choices")
                if not isinstance(choices, list) or not choices:
                    continue
                first_choice = choices[0]
                if not isinstance(first_choice, dict):
                    continue
                delta_payload = first_choice.get("delta")
                if not isinstance(delta_payload, dict):
                    continue
                delta = delta_payload.get("content", "")
                if delta:
                    yield delta

    def _extract_message_content(self, response: dict[str, object]) -> str:
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices:
            return ""
        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            return ""
        message = first_choice.get("message")
        if not isinstance(message, dict):
            return ""
        content = message.get("content", "")
        if not isinstance(content, str):
            return ""
        return content.strip()

    def _build_messages(self, *, user_query: str, context_text: str, tool_message: str | None) -> list[dict[str, str]]:
        system_prompt = (
            "你是企业研发与运维知识助手。请基于上下文，用中文给出简洁、可执行回答。"
            "优先输出结论、步骤和风险提醒，不要大段复述原文。"
        )
        prompt_parts = [f"问题：{user_query.strip()}"]
        compact_tool_message = self._compact_tool_message(tool_message or "")
        if compact_tool_message:
            prompt_parts.append(f"工具结果：\n{compact_tool_message}")
        compact_context = self._compact_context_text(context_text)
        prompt_parts.append(f"参考上下文：\n{compact_context or '暂无上下文'}")
        prompt_parts.append("回答格式：先给结论，再给 3 到 5 条步骤，最后补充风险提醒。")
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "\n\n".join(prompt_parts)},
        ]

    def _compact_tool_message(self, tool_message: str) -> str:
        return self._compact_text_block(
            tool_message,
            max_chars=self.tool_message_max_chars,
            drop_provenance=False,
        )

    def _compact_context_text(self, context_text: str) -> str:
        return self._compact_text_block(
            context_text,
            max_chars=self.context_max_chars,
            drop_provenance=True,
        )

    def _compact_text_block(self, text: str, *, max_chars: int, drop_provenance: bool) -> str:
        if not text.strip():
            return ""
        prioritized: list[str] = []
        secondary: list[str] = []
        seen: set[str] = set()
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if drop_provenance and self._should_drop_context_line(line):
                continue
            compact = re.sub(r"\s+", " ", line)
            compact = re.sub(r"^\[[^\]]+\]\s*", "", compact)
            if len(compact) > self.context_line_max_chars:
                compact = compact[: self.context_line_max_chars - 3].rstrip() + "..."
            if compact in seen:
                continue
            seen.add(compact)
            if self._is_priority_line(compact):
                prioritized.append(compact)
            else:
                secondary.append(compact)

        selected_lines: list[str] = []
        used_chars = 0
        for line in prioritized + secondary:
            projected = used_chars + len(line) + (1 if selected_lines else 0)
            if projected > max_chars:
                break
            selected_lines.append(line)
            used_chars = projected
        if selected_lines:
            return "\n".join(selected_lines)
        compact = re.sub(r"\s+", " ", text.strip())
        if len(compact) <= max_chars:
            return compact
        return compact[: max_chars - 3].rstrip() + "..."

    def _should_drop_context_line(self, line: str) -> bool:
        lowered = line.lower()
        return (
            "github provenance" in lowered
            or lowered.startswith("- repository:")
            or lowered.startswith("- issue:")
            or lowered.startswith("- url:")
            or line.startswith("```")
        )

    def _is_priority_line(self, line: str) -> bool:
        lowered = line.lower()
        priority_keywords = (
            "建议",
            "检查",
            "先看",
            "结论",
            "风险",
            "maxmemory",
            "slowlog",
            "wait_timeout",
            "error log",
            "kubectl",
            "oom",
            "timeout",
            "慢查询",
            "连接",
        )
        return any(keyword in lowered for keyword in priority_keywords)

    def _is_retryable_error(self, exc: Exception) -> bool:
        if self._classify_provider_error(exc) in {"timeout", "disconnect", "http_5xx"}:
            return True
        return False

    def _classify_provider_error(self, exc: Exception) -> str:
        if isinstance(exc, TimeoutError):
            return "timeout"
        if isinstance(exc, RemoteDisconnected):
            return "disconnect"
        message = str(exc)
        if "timed out" in message.lower():
            return "timeout"
        if "Remote end closed connection" in message:
            return "disconnect"
        http_match = re.search(r"HTTP\s+(\d{3})", message)
        if http_match:
            code = http_match.group(1)
            if code.startswith("5"):
                return "http_5xx"
            return f"http_{code}"
        if "HTTP 5" in message:
            return "http_5xx"
        return "error"

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

    def _default_stream_requester(self, *, url: str, headers: dict[str, str], payload: dict[str, object], timeout: int):
        request = urllib.request.Request(
            url=url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={**headers, "Accept": "text/event-stream"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                for line in response:
                    yield line
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
            retry_attempts=getattr(settings, "llm_retry_attempts", 2),
            retry_backoff_seconds=getattr(settings, "llm_retry_backoff_seconds", 0.4),
            context_max_chars=getattr(settings, "llm_context_max_chars", 1400),
        )
    return fallback


def _elapsed_ms(started_at: float) -> int:
    return max(0, int(round((time.monotonic() - started_at) * 1000)))


def _build_provider_diagnostic(
    *,
    provider_status: str,
    provider_attempts: int,
    first_token_latency_ms: int,
    total_latency_ms: int,
    provider_error: str,
) -> str:
    parts = [
        f"provider={provider_status}",
        f"attempts={provider_attempts}",
    ]
    if first_token_latency_ms > 0:
        parts.append(f"first_token={first_token_latency_ms}ms")
    if total_latency_ms > 0:
        parts.append(f"total={total_latency_ms}ms")
    if provider_error:
        parts.append(f"error={provider_error}")
    return " | ".join(parts)
