# Real Acceptance 20Q

- Generated at: 2026-04-24 23:14:14
- Questions: 20
- Remote success: 20
- Fallback: 0
- Tool route: 1
- Runner errors: 0
- Avg first token: 7068.1 ms
- Avg total: 28327.5 ms
- Avg local first delta: 16019.4 ms
- Avg chunk count: 979.0

| # | backend | provider | first_token_ms | total_ms | local_first_delta_ms | chunks | route | sources | preview |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| 1 | remote | success | 1681 | 26610 | 17465 | 1325 | answer | 4 | 1) 结论   Redis 发生 OOM（Out Of Memory）时，优先要分清是“Redis 触发 maxmemory 限制导致写入失败（OOM c... |
| 2 | remote | success | 2381 | 16712 | 3135 | 781 | answer | 2 | 1. 结论   MySQL 慢查询排查建议先从“能直接定位慢 SQL 的日志”和“反映当前压力与锁等待的运行状态信息”入手：优先看慢查询日志（slow l... |
| 3 | remote | success | 2236 | 21970 | 7633 | 1082 | answer | 5 | ## 1) 结论 Pod 频繁重启（常见为 `CrashLoopBackOff`）第一轮排查的核心是：**先确认“为什么退出”（退出码/Reason/最后... |
| 4 | remote | success | 2366 | 23695 | 5992 | 1160 | answer | 5 | ### 1) 结论   Redis 连接超时通常优先从三类方向排查：**服务是否存活/端口是否可达**、**宿主机资源是否不足导致响应变慢**、**链路/... |
| 5 | remote | success | 5833 | 18409 | 21224 | 802 | answer | 3 | ## 1) 结论 MySQL 报 **“too many connections”** 时，优先确认两件事：   - **连接是否真的打满了 `max_c... |
| 6 | remote | success | 2240 | 22691 | 11416 | 1119 | answer | 5 | ## 1. 结论 Nginx 出现 **502 Bad Gateway**，本质是 **Nginx 作为反向代理从上游（upstream）拿不到有效响应*... |
| 7 | remote | success | 3025 | 19381 | 18253 | 633 | answer | 5 | 1. 结论   磁盘空间“突然飙满”第一步先**定位是哪个挂载点/目录在增长**（是根分区、数据盘、日志盘还是容器/临时目录），再继续追到具体文件与进程；... |
| 8 | remote | success | 2496 | 16274 | 13028 | 754 | diagnose | 5 | 1) 结论   Docker 容器启动失败，通常优先看三类信息：**容器自身退出原因（日志/退出码）**、**Docker/宿主机层面的报错事件**、**... |
| 9 | remote | success | 1647 | 44527 | 7000 | 301 | answer | 5 | ## 1. 结论   Kubernetes 服务访问不通优先按“**客户端 → Service/Ingress → Endpoints/Pod → 网络/... |
| 10 | remote | success | 2041 | 17895 | 5752 | 864 | answer | 5 | ### 1) 结论   Redis 主从延迟较大时，优先关注能直接反映“复制积压、链路质量、主库写入压力、从库应用能力、资源瓶颈”的指标：**复制延迟（秒... |
| 11 | remote | success | 2482 | 14129 | 3206 | 633 | answer | 2 | 1. 结论   MySQL 主从同步异常时，建议先从“链路是否正常 + 复制线程是否在跑 + 当前报错原因”三件事入手：先确认主从网络/连通性，再看从库复... |
| 12 | remote | success | 12949 | 62189 | 19716 | 1128 | answer | 5 | ## 1. 结论 线上 CPU 飙高但来源不明，第一轮要**先把问题“定位到层”**：是**节点层**还是**某个容器/Pod**，是 **user%**... |
| 13 | remote | success | 2815 | 26686 | 19206 | 1283 | answer | 2 | ### 1) 结论 应用日志里的 `timeout` 需要按“发生在**连接建立**还是**命令/查询执行**阶段”来区分来源：   - **网络/链路问... |
| 14 | remote | success | 2128 | 29247 | 17525 | 1487 | answer | 3 | ### 1) 结论   怀疑 Kubernetes 集群 DNS 异常时，应从“现象复现（Pod 内解析）→ CoreDNS/kube-dns 组件健康→... |
| 15 | remote | success | 3474 | 23082 | 18734 | 1068 | tool | 3 | ### 1) 结论 - **当前 Redis 服务状态：running**，说明进程层面正常在运行，但不代表业务侧无超时（仍可能是连接/命令执行/IO 卡... |
| 16 | remote | success | 2447 | 20437 | 3236 | 980 | answer | 2 | ## 1) 结论   当前无工具输出/监控数据可用，无法直接判断 MySQL 连接是否异常或是否存在慢查询堆积。建议按“连接状态 → 慢查询线索 → 进一... |
| 17 | remote | success | 77755 | 95975 | 93030 | 1082 | answer | 4 | ## 1. 结论 Redis 的 `maxmemory` 配置不合理，常见会带来两类问题：  - **配得过小（尤其配合 `maxmemory-polic... |
| 18 | remote | success | 6275 | 27592 | 13707 | 1244 | answer | 5 | ## 1) 结论 MySQL 日志里的 **“Aborted connection”** 通常不是“数据库崩了”，而是 **连接在握手或读写过程中被中断/... |
| 19 | remote | success | 2511 | 22198 | 17759 | 1079 | answer | 2 | ### 1) 结论   节点变为 **NotReady** 的第一轮运维目标是：**快速判断是节点本身不可用（网络/资源/运行时/系统）还是 kubele... |
| 20 | remote | success | 2580 | 16852 | 3371 | 775 | diagnose | 2 | 1. 结论   接口“整体变慢但无明显报错”通常是系统资源、依赖组件（如 Redis）性能退化或连接/线程池耗尽导致的“慢响应”，需要按“从外到内、从系统... |