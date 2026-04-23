import unittest

from app.services.llm_service import RuleBasedLLMService


RAW_CONTEXT = """[Redis 运维 Runbook > 状态检查] 当 Redis 服务响应异常时，优先检查进程、端口和资源占用情况。
[redis issue > GitHub Provenance] - Repository: redis/redis
- Issue: #11204
- URL: https://github.com/redis/redis/issues/11204
[used_memory_peak keep growing > Problem] ```
bind 0.0.0.0
port 6379
timeout 0
maxmemory 1GB
slowlog-log-slower-than 10000
```
[used_memory_peak keep growing > Curated Answers > High Signal Answer 1] 建议先检查 maxmemory、slowlog、内存碎片率和连接数，再确认是否存在大 key 或慢查询。
"""


class AnswerSummarizationTests(unittest.TestCase):
    def test_summarizes_context_instead_of_dumping_provenance_and_raw_config(self) -> None:
        answer = RuleBasedLLMService().generate_answer(
            user_query="Redis 出现 OOM 和 timeout 时，通常先看哪些指标或日志？",
            context_text=RAW_CONTEXT,
        )

        self.assertIn("maxmemory", answer.lower())
        self.assertIn("slowlog", answer.lower())
        self.assertNotIn("GitHub Provenance", answer)
        self.assertNotIn("bind 0.0.0.0", answer)
        self.assertLess(len(answer), 400)

    def test_tool_response_still_includes_compact_action_summary(self) -> None:
        answer = RuleBasedLLMService().generate_answer(
            user_query="请重启 redis 服务",
            context_text=RAW_CONTEXT,
            tool_message="已执行模拟工具，redis 服务重启成功。",
        )

        self.assertIn("redis 服务重启成功", answer)
        self.assertIn("建议", answer)
        self.assertLess(len(answer), 420)


if __name__ == "__main__":
    unittest.main()
