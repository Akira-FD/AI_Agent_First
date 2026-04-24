from __future__ import annotations


def validate_runtime_capabilities(*, settings, llm_service) -> dict[str, object]:
    backend = "unknown"
    if llm_service and hasattr(llm_service, "backend_label"):
        backend = llm_service.backend_label()

    llm_remote_configured = bool(getattr(settings, "llm_api_key", "") or getattr(llm_service, "api_key", ""))
    llm_sse_supported = hasattr(llm_service, "stream_answer_result") and backend.startswith("openai-compatible:")

    return {
        "app_name": getattr(settings, "app_name", "unknown"),
        "docs_dir_ready": bool(getattr(settings, "docs_dir", None) and settings.docs_dir.exists()),
        "sqlite_dir_ready": bool(getattr(settings, "sqlite_path", None) and settings.sqlite_path.parent.exists()),
        "retrieval_backend": getattr(settings, "retrieval_backend", "unknown"),
        "embedding_backend": getattr(settings, "embedding_backend", "unknown"),
        "reranker_backend": getattr(settings, "reranker_backend", "unknown"),
        "llm_backend": backend,
        "llm_remote_configured": llm_remote_configured,
        "llm_sse_supported": llm_sse_supported,
    }
