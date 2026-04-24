# Real Acceptance 20Q With Stage Telemetry

- Generated at: 2026-04-24 23:53:24
- Questions: 20
- Remote success: 20
- Fallback: 0
- Tool route: 1
- Runner errors: 0
- Avg provider first token: 3945.5 ms
- Avg provider total: 22540.5 ms
- Avg local first delta: 9115.9 ms
- Avg local total: 27721.7 ms
- Avg perceived gap: 5170.4 ms
- Avg pre-LLM total: 5159.2 ms
- Avg retrieval: 210.9 ms
- Avg coarse rerank: 0.0 ms
- Avg BGE rerank: 4948.2 ms
- Avg context build: 0.0 ms
- Avg chunk count: 1041.1
- Stage share of pre-LLM:
  - retrieval: 4.09%
  - coarse_rerank: 0.00%
  - bge_rerank: 95.91%
  - context_build: 0.00%
- Dominant pre-LLM stage counts:
  - retrieval: 0
  - coarse_rerank: 0
  - bge_rerank: 20
  - context_build: 0

| # | route | provider_first | local_first | gap | pre_llm | retrieval | coarse | bge | context | provider_total | dominant | preview |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | answer | 13598 | 23416 | 9818 | 9807 | 218 | 0 | 9589 | 0 | 36490 | bge_rerank | ## 1) 结论 Redis 出现 OOM（进程被杀/分配失败/写入被拒）时，**优先判断是哪一类“内存上限”触发**：   - **Re... |
| 2 | answer | 1433 | 2192 | 759 | 749 | 209 | 0 | 540 | 0 | 17330 | bge_rerank | 1) 结论   排查 MySQL 慢查询，优先从“慢查询日志 + 执行现场（进程列表/锁等待）+ InnoDB 引擎状态 + 错误日志 +... |
| 3 | answer | 6507 | 9570 | 3063 | 3053 | 204 | 0 | 2849 | 0 | 28686 | bge_rerank | ## 1) 结论 Pod 频繁重启（常见表现为 `CrashLoopBackOff`）第一轮排查的核心是：**先确认“为什么容器退出”（退... |
| 4 | answer | 1704 | 4094 | 2390 | 2380 | 210 | 0 | 2170 | 0 | 18880 | bge_rerank | ## 1. 结论 Redis 连接超时优先从三类方向排查：**服务是否在（进程/端口）**、**网络链路是否通（客户端到Redis）**、... |
| 5 | answer | 5397 | 15102 | 9705 | 9694 | 208 | 0 | 9486 | 0 | 24152 | bge_rerank | ## 1) 结论   MySQL 报 **too many connections** 时，优先确认两件事：**连接数是否真的打满了（Th... |
| 6 | answer | 1733 | 6124 | 4391 | 4382 | 209 | 0 | 4173 | 0 | 21012 | bge_rerank | ## 1) 结论 Nginx 出现 **502 Bad Gateway** 本质是：**Nginx 作为反向代理从上游（upstream：... |
| 7 | answer | 1792 | 7318 | 5526 | 5516 | 210 | 0 | 5306 | 0 | 13912 | bge_rerank | ### 1) 结论   磁盘“突然飙满”的第一步：**先定位到底是哪个挂载点/目录在增长、增长来自文件还是已删除但仍被进程占用的文件**。... |
| 8 | diagnose | 7128 | 10081 | 2953 | 2942 | 208 | 0 | 2734 | 0 | 20002 | bge_rerank | ## 1) 结论 Docker 容器启动失败，通常先看三类信息：**容器退出原因（ExitCode/OOM/信号）**、**容器标准输出日... |
| 9 | answer | 1584 | 4954 | 3370 | 3360 | 214 | 0 | 3146 | 0 | 33064 | bge_rerank | ## 1) 结论 Kubernetes「服务访问不通」建议按“入口层 → Service/Endpoint 资源 → Pod 就绪与端口 ... |
| 10 | answer | 1638 | 4148 | 2510 | 2501 | 212 | 0 | 2289 | 0 | 14411 | bge_rerank | ## 1) 结论 Redis 主从延迟（replication lag）较大时，优先盯住能直接解释“主库写入压力/网络与IO瓶颈/复制链路... |
| 11 | answer | 2359 | 3095 | 736 | 726 | 208 | 0 | 518 | 0 | 12279 | bge_rerank | 1) 结论   MySQL 主从同步异常时，建议先从“复制线程状态 + 主从位点/GTID一致性 + 网络与权限”三块做快速体检，优先确认... |
| 12 | answer | 3262 | 7579 | 4317 | 4307 | 207 | 0 | 4100 | 0 | 22594 | bge_rerank | ### 1. 结论 线上出现 **CPU 飙高但来源不明** 时，第一轮目标是：**先确认是“哪台机器/哪个进程/哪个容器/哪类内核或 K... |
| 13 | answer | 2698 | 12417 | 9719 | 9708 | 209 | 0 | 9499 | 0 | 25239 | bge_rerank | ## 1. 结论 应用日志里的 **timeout** 要区分“网络 / 数据库 / Redis”三类，核心思路是：**把超时拆成链路三段... |
| 14 | answer | 1649 | 11407 | 9758 | 9748 | 216 | 0 | 9532 | 0 | 20686 | bge_rerank | 1. 结论   怀疑集群 DNS 异常时，应从“Pod 内解析是否失败/变慢 → CoreDNS/kube-dns 组件是否健康 → Se... |
| 15 | tool | 9916 | 19606 | 9690 | 9661 | 211 | 0 | 9450 | 0 | 28651 | bge_rerank | ## 1) 结论 - Redis 服务当前状态为 **running**，说明进程在，但**仍可能存在间歇性超时**（例如短暂卡顿、网络抖... |
| 16 | answer | 2130 | 2914 | 784 | 774 | 215 | 0 | 559 | 0 | 22925 | bge_rerank | 1. 结论   - 目前没有提供任何 MySQL 检查结果/工具输出，无法确认连接是否正常、是否存在慢查询。需要先按步骤补齐连接与慢查询证... |
| 17 | answer | 1609 | 10760 | 9151 | 9141 | 211 | 0 | 8930 | 0 | 21461 | bge_rerank | ### 1. 结论   Redis 的 `maxmemory` 配置不合理，常见会带来两类问题：   - **maxmemory 设得过小... |
| 18 | answer | 2469 | 6782 | 4313 | 4302 | 210 | 0 | 4092 | 0 | 20571 | bge_rerank | ## 1) 结论 MySQL 日志里的 **“Aborted connection”** 通常不是单一原因，常见与以下几类问题相关：  -... |
| 19 | answer | 8092 | 17760 | 9668 | 9657 | 213 | 0 | 9444 | 0 | 28817 | bge_rerank | ## 1) 结论 Kubernetes 节点变为 **NotReady** 时，第一轮运维要先判定：**是“节点确实不可达/故障”还是“K... |
| 20 | diagnose | 2212 | 2998 | 786 | 776 | 217 | 0 | 559 | 0 | 19649 | bge_rerank | 1) 结论   接口“整体变慢但无明显报错”通常是系统资源瓶颈（CPU/内存/磁盘/网络）、下游依赖（数据库/Redis/第三方）性能退化... |