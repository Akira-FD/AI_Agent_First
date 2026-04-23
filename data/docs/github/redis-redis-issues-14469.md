# [CRASH] RedisSearch module crash: Redis 8.2.1 segfault in raxGenericInsert (signal 11)



## GitHub Provenance



- Repository: redis/redis

- Issue: #14469

- State: closed

- Labels: crash report

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/14469



## Problem



## Summary
Redis crashed with SIGSEGV (segmentation fault) while running with the RedisSearch module (redisearch.so) on Redis 8.2.1 (Bitnami container). The crash occurred in core Redis's radix tree code (`raxGenericInsert`), called from within the RedisSearch module. This appears to be a module bug, module/core incompatibility, or a rare concurrency/memory issue.

## Key Log Excerpts
```
1:M 26 Oct 2025 07:45:51.549 # Redis 8.2.1 crashed by signal: 11, si_code: 1
1:M 26 Oct 2025 07:45:51.549 # Accessing address: (nil)
1:M 26 Oct 2025 07:45:51.549 # Crashed running the instruction at: 0x55b3f56a8817
------ STACK TRACE ------
EIP:
redis-server *:6379(raxGenericInsert+0xb7)[0x55b3f56a8817]
1 redis-server
/usr/lib/libc.so.6(epoll_wait+0x56)[0x7f348e40a7f6]
redis-server *:6379(+0x9d364)[0x55b3f5548364]
redis-server *:6379(aeMain+0xd0)[0x55b3f5548a60]
redis-server *:6379(main+0x4c2)[0x55b3f5542942]
/usr/lib/libc.so.6(+0x2724a)[0x7f348e32924a]
/usr/lib/libc.so.6(__libc_start_main+0x85)[0x7f348e329305]
redis-server *:6379(_start+0x21)[0x55b3f5544321]

17 io_thd_2
/usr/lib/libc.so.6(epoll_wait+0x56)[0x7f348e40a7f6]
redis-server *:6379(+0x9d364)[0x55b3f5548364]
redis-server *:6379(aeMain+0xd0)[0x55b3f5548a60]
redis-server *:6379(IOThreadMain+0x95)[0x55b3f5559ec5]
/usr/lib/libc.so.6(+0x890c4)[0x7f348e38b0c4]
/usr/lib/libc.so.6(__clone+0x40)[0x7f348e40a410]

18 io_thd_3
/usr/lib/libc.so.6(epoll_wait+0x56)[0x7f348e40a7f6]
redis-server *:6379(+0x9d364)[0x55b3f5548364]
redis-server *:6379(aeMain+0xd0)[0x55b3f5548a60]
redis-server *:6379(IOThreadMain+0x95)[0x55b3f5559ec5]
/usr/lib/libc.so.6(+0x890c4)[0x7f348e38b0c4]
/usr/lib/libc.so.6(__clone+0x40)[0x7f348e40a410]

23 cleanPool-8028
/usr/lib/libc.so.6(+0x85e26)[0x7f348e387e26]
/usr/lib/libc.so.6(pthread_cond_wait+0x1e8)[0x7f348e38a4e8]
/opt/bitnami/redis/lib/redis/modules/redisearch.so(+0x3363db)[0x7f348c8253db]
/opt/bitnami/redis/lib/redis/modules/redisearch.so(+0x3362b9)[0x7f348c8252b9]
/usr/lib/libc.so.6(+0x890c4)[0x7f348e38b0c4]
/usr/lib/libc.so.6(__clone+0x40)[0x7f348e40a410]

16 io_thd_1
/usr/lib/libc.so.6(epoll_wait+0x56)[0x7f348e40a7f6]
redis-server *:6379(+0x9d364)[0x55b3f5548364]
redis-server *:6379(aeMain+0xd0)[0x55b3f5548a60]
redis-server *:6379(IOThreadMain+0x95)[0x55b3f5559ec5]
/usr/lib/libc.so.6(+0x890c4)[0x7f348e38b0c4]
/usr/lib/libc.so.6(__clone+0x40)[0x7f348e40a410]

13 bio_close_file
/usr/lib/libc.so.6(+0x85e26)[0x7f348e387e26]
/usr/lib/libc.so.6(pthread_cond_wait+0x1e8)[0x7f348e38a4e8]
redis-server *:6379(bioProcessBackgroundJobs+0x30b)[0x55b3f56486ab]
/usr/lib/libc.so.6(+0x890c4)[0x7f348e38b0c4]
/usr/lib/libc.so.6(__clone+0x40)[0x7f348e40a410]

15 bio_lazy_free
/usr/lib/libc.so.6(+0x85e26)[0x7f348e387e26]
/usr/lib/libc.so.6(pthread_cond_wait+0x1e8)[0x7f348e38a4e8]
redis-server *:6379(bioProcessBackgroundJobs+0x30b)[0x55b3f56486ab]
/usr/lib/libc.so.6(+0x890c4)[0x7f348e38b0c4]
/usr/lib/libc.so.6(__clone+0x40)[0x7f348e40a410]

24 gc-0214 *
/usr/lib/libc.so.6(+0x3c050)[0x7f348e33e050]
redis-server *:6379(raxGenericInsert+0xb7)[0x55b3f56a8817]
redis-server *:6379(RM_GetServerInfo+0x1ec)[0x55b3f5690aec]
/opt/bitnami/redis/lib/redis/modules/redisearch.so(+0x36f55d)[0x7f348c85e55d]
/opt/bitnami/redis/lib/redis/modules/redisearch.so(+0x371e6a)[0x7f348c860e6a]
/opt/bitnami/redis/lib/redis/modules/redisearch.so(+0x3362e8)[0x7f348c8252e8]
/usr/lib/libc.so.6(+0x890c4)[0x7f348e38b0c4]
/usr/lib/libc.so.6(__clone+0x40)[0x7f348e40a410]

14 bio_aof
/usr/lib/libc.so.6(+0x85e26)[0x7f348e387e26]
/usr/lib/libc.so.6(pthread_cond_wait+0x1e8)[0x7f348e38a4e8]
redis-server *:6379(bioProcessBackgroundJobs+0x30b)[0x55b3f56486ab]
/usr/lib/libc.so.6(+0x890c4)[0x7f348e38b0c4]
/usr/lib/libc.so.6(__clone+0x40)[0x7f348e40a410]

9/9 expected stacktraces.

1:M 26 Oct 2025 07:45:51.557 # 
RAX:0000000000000156 RBX:0000000000000075
RCX:00007f33b3aa7b58 RDX:000000000f17221c
RDI:00000000000000d0 RSI:00007f33a4934e8c
RBP:00007f3461dfe0a0 RSP:00007f3461dfdfe0
R8 :0000000000000000 R9 :0000000000000000
R10:00007f3478b910d0 R11:000000000f17221a
R12:0000000000000001 R13:000000000000000b
R14:00007f3478a322f1 R15:0000000000000000
RIP:000055b3f56a8817 EFL:0000000000010212
CSGSFS:002b000000000033
1:M 26 Oct 2025 07:45:51.557 # (00007f3461dfdfef) -> 00007f3478a322fd
1:M 26 Oct 2025 07:45:51.557 # (00007f3461dfdfee) -> 000000000000000a
1:M 26 Oct 2025 07:45:51.557 # (00007f3461dfdfed) -> af983bef272f8600
1:M 26 Oct 2025 07:45:51.557 # (00007f3461dfdfec) -> 0000000000000010
1:M 26 Oct 2025 07:45:51.557 # (00007f3461dfdfeb) -> 000055b3f5578961
1:M 26 Oct 2025 07:45:51.557 # (00007f3461dfdfea) -> 00007f3461dfe0f4
1:M 26 Oct 2025 07:45:51.557 # (00007f3461dfdfe9) -> 00007f33a1cac671
1:M 26 Oct 2025 07:45:51.557 # (00007f3461dfdfe8) -> 00007f3461dfe0a0
1:M 26 Oct 2025 07:45:51.557 # (00007f3461dfdfe7) -> 000000000000060e
1:M 26 Oct 2025 07:45:51.557 # (00007f3461dfdfe6) -> 0000000000000038
1:M 26 Oct 2025 07:45:51.557 # (00007f3461dfdfe5) -> 0000000000000038
1:M 26 Oct 2025 07:45:51.557 # (00007f3461dfdfe4) -> 000000000000060e
1:M 26 Oct 2025 07:45:51.557 # (00007f3461dfdfe3) -> af983bef272f8600
1:M 26 Oct 2025 07:45:51.557 # (00007f3461dfdfe2) -> 0000000000000008
1:M 26 Oct 2025 07:45:51.557 # (00007f3461dfdfe1) -> 000055b3f570d4e7
1:M 26 Oct 2025 07:45:51.557 # (00007f3461dfdfe0) -> 00007f3461dfe020

------ INFO OUTPUT ------
# Server
redis_version:8.2.1
redis_mode:standalone
[...]
# Modules
module:name=ReJSON,ver=80200,api=1,filters=0,usedby=[search],using=[],options=[handle-io-errors]
module:name=vectorset,ver=1,api=1,filters=0,usedby=[],using=[],options=[handle-io-errors|handle-repl-async-load]
module:name=search,ver=80201,api=1,filters=0,usedby=[],using=[ReJSON],options=[handle-io-errors]

# search_version
search_version:8.2.1
search_redis_version:8.2.1 - oss
[...]
------ FAST MEMORY TEST ------
1:M 26 Oct 2025 07:45:51.577 # main thread terminated
[...]
=== REDIS BUG REPORT END. Make sure to include from START to END. ===
```

## Observations
- Crash occurs in Redis core radix tree (rax) logic, called from RedisSearch module code.
- Repeated `ForkGC - got timeout while reading from pipe (Success)` messages prior to crash—appears related to RedisSearch index GC.
- Heavy usage of FT.SEARCH and JSON commands (high call counts, high p99 latency).
- IO threads enabled (io-threads 4), both RedisSearch and ReJSON loaded.
- No OOM or maxmemory reached; RSS and fragmentation normal.

## Environment
- Redis: 8.2.1 (Bitnami container)
- RedisSearch: 8.2.1 (as per module info)
- ReJSON: 8.2.0
- vectorset: 1
- OS: Linux 5.14.0-427.85.1.el9_4.x86_64 x86_64
- Memory: ~3GB used, 31GB total
- Workload: High concurrency, heavy FT.SEARCH and JSON.GET/SET, pubsub activity

## Steps to Reproduce
1. Run Redis 8.2.1 with RedisSearch 8.2.1 & ReJSON 8.2.0 modules loaded (Bitnami container)
2. Enable IO threads (io-threads 4)
3. Heavy usage of FT.SEARCH and JSON commands
4. Observe repeated ForkGC timeouts, then eventual segfault

## Attachments
- Full crash log (START to END) available upon request

## Additional Diagnostics
- Fast memory test: PASSED
- RDB persistence (AOF disabled)
- No maxmemory set
- No recent OOM/killer events in dmesg

## Recommendation
This appears to be a bug in the RedisSearch module or a module/core compatibility issue. Please advise on:
- Known issues with RedisSearch 8.2.1 and Redis 8.2.1
- Safe upgrade path or workaround
- Further debugging steps (can provide core dump if needed)

---
Let me know if further logs or configs are needed. This is a production-impacting crash with RedisSearch.
[](url)



## Curated Answers



### High Signal Answer 1

please also create a issue in https://github.com/RediSearch/RediSearch/issues, thx.

- Author: sundb
- Quality score: 4
- URL: https://github.com/redis/redis/issues/14469#issuecomment-3449501757

### High Signal Answer 2

sorry, reopen it, i thought it is a search module issue

- Author: ShooterIT
- Quality score: 4
- URL: https://github.com/redis/redis/issues/14469#issuecomment-3451999491

### High Signal Answer 3

i wonder what could the module do wrongly to cause a crash in that flow.
i.e. the rax we insert into is a freshly created one (not long living), the strings we insert into it, are freshly allocated, the key is a pointer to an sds we just compared to `#` so it must not be NULL, and the value is a new sds we just allocated.
the only thing i can think of is a double free somewhere, which is added to the thread cache and then used by two threads in parallel.

- Author: oranagra
- Quality score: 4
- URL: https://github.com/redis/redis/issues/14469#issuecomment-3549105403
