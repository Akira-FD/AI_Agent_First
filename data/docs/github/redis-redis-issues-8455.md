# Redis 6.0.9 crashed by signal: 11, si_code: 1



## GitHub Provenance



- Repository: redis/redis

- Issue: #8455

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/8455



## Problem



Hi,
Till now, I've been running Redis 3.2.6 from Debian 9 (AMD64) with no problems. Some time ago, I upgraded to Debian 10 (Redis 5.0.3) and it began to crash with this message:
`Redis 5.0.3 crashed by signal: 11`

So now I've tried upgrading to Debian 11 (testing) that comes with Redis 6.0.9 giving the same result than Redis 5.0.3. 

I do not suspect from RAM problems since I've run memtest86+ several hours with no errors and I can reproduce the signal 11 crash in two different computers. Furthermore, Redis has always worked fine with version 3.2.6.

The database is managed by Nodebb.

This is the report:

=== REDIS BUG REPORT START: Cut & paste starting from here ===
1660:M 05 Feb 2021 22:33:44.283 # Redis 6.0.9 crashed by signal: 11, si_code: 1
1660:M 05 Feb 2021 22:33:44.283 # Crashed running the instruction at: 0x559cbde51e40
1660:M 05 Feb 2021 22:33:44.283 # Accessing address: 0x7f9a7e800000
1660:M 05 Feb 2021 22:33:44.283 # Killed by PID: 2122317824, UID: 32666
1660:M 05 Feb 2021 22:33:44.283 # Failed assertion: <no assertion failed> (<no file>:0)

------ STACK TRACE ------
EIP:
/usr/bin/redis-server 127.0.0.1:6379(siphash+0x60)[0x559cbde51e40]

Backtrace:
/usr/bin/redis-server 127.0.0.1:6379(logStackTrace+0x4f)[0x559cbde13b2f]
/usr/bin/redis-server 127.0.0.1:6379(sigsegvHandler+0xd5)[0x559cbde14325]
/lib/x86_64-linux-gnu/libpthread.so.0(+0x14140)[0x7f9a87285140]
/usr/bin/redis-server 127.0.0.1:6379(siphash+0x60)[0x559cbde51e40]
/usr/bin/redis-server 127.0.0.1:6379(dictAddRaw+0x2a)[0x559cbddc27fa]
/usr/bin/redis-server 127.0.0.1:6379(dictAdd+0x11)[0x559cbddc29c1]
/usr/bin/redis-server 127.0.0.1:6379(+0x683e1)[0x559cbddf13e1]
/usr/bin/redis-server 127.0.0.1:6379(rdbLoadRio+0x282)[0x559cbddf28a2]
/usr/bin/redis-server 127.0.0.1:6379(rdbLoad+0xd2)[0x559cbddf3462]
/usr/bin/redis-server 127.0.0.1:6379(loadDataFromDisk+0x9e)[0x559cbddcbe7e]
/usr/bin/redis-server 127.0.0.1:6379(main+0x3bd)[0x559cbddba07d]
/lib/x86_64-linux-gnu/libc.so.6(__libc_start_main+0xea)[0x7f9a870d2d0a]
/usr/bin/redis-server 127.0.0.1:6379(_start+0x2a)[0x559cbddba43a]

------ INFO OUTPUT ------
# Server
redis_version:6.0.9
redis_git_sha1:00000000
redis_git_dirty:0
redis_build_id:74d695619ee2c9cb
redis_mode:standalone
os:Linux 4.19.0-14-amd64 x86_64
arch_bits:64
multiplexing_api:epoll
atomicvar_api:atomic-builtin
gcc_version:10.2.1
process_id:1660
run_id:82eb5b7f8ace6fe0e3a532c2dbe9ffc2b1ddbd50
tcp_port:6379
uptime_in_seconds:25
uptime_in_days:0
hz:10
configured_hz:10
lru_clock:1948057
executable:/usr/bin/redis-server
config_file:/etc/redis/redis.conf
io_threads_active:0

# Clients
connected_clients:0
client_recent_max_input_buffer:0
client_recent_max_output_buffer:0
blocked_clients:0
tracking_clients:0
clients_in_timeout_table:0

# Memory
used_memory:5487903672
used_memory_human:5.11G
used_memory_rss:0
used_memory_rss_human:0B
used_memory_peak:6427426232
used_memory_peak_human:5.99G
used_memory_peak_perc:85.38%
used_memory_overhead:119385272
used_memory_startup:809672
used_memory_dataset:5368518400
used_memory_dataset_perc:97.84%
allocator_allocated:0
allocator_active:0
allocator_resident:0
total_system_memory:16506609664
total_system_memory_human:15.37G
used_memory_lua:41984
used_memory_lua_human:41.00K
used_memory_scripts:0
used_memory_scripts_human:0B
number_of_cached_scripts:0
maxmemory:0
maxmemory_human:0B
maxmemory_policy:noeviction
allocator_frag_ratio:-nan
allocator_frag_bytes:0
allocator_rss_ratio:-nan
allocator_rss_bytes:0
rss_overhead_ratio:-nan
rss_overhead_bytes:0
mem_fragmentation_ratio:-nan
mem_fragmentation_bytes:0
mem_not_counted_for_evict:0
mem_replication_backlog:0
mem_clients_slaves:0
mem_clients_normal:0
mem_aof_buffer:0
mem_allocator:jemalloc-5.2.1
active_defrag_running:0
lazyfree_pending_objects:0

# Persistence
loading:1
rdb_changes_since_last_save:0
rdb_bgsave_in_progress:0
rdb_last_save_time:1612560793
rdb_last_bgsave_status:ok
rdb_last_bgsave_time_sec:-1
rdb_current_bgsave_time_sec:-1
rdb_last_cow_size:0
aof_enabled:0
aof_rewrite_in_progress:0
aof_rewrite_scheduled:0
aof_last_rewrite_time_sec:-1
aof_current_rewrite_time_sec:-1
aof_last_bgrewrite_status:ok
aof_last_write_status:ok
aof_last_cow_size:0
module_fork_in_progress:0
module_fork_last_cow_size:0
loading_start_time:1612560793
loading_total_bytes:1527837039
loading_loaded_bytes:1409850180
loading_loaded_perc:92.28
loading_eta_seconds:2

# Stats
total_connections_received:0
total_commands_processed:0
instantaneous_ops_per_sec:0
total_net_input_bytes:0
total_net_output_bytes:0
instantaneous_input_kbps:0.00
instantaneous_output_kbps:0.00
rejected_connections:0
sync_full:0
sync_partial_ok:0
sync_partial_err:0
expired_keys:0
expired_stale_perc:0.00
expired_time_cap_reached_count:0
expire_cycle_cpu_milliseconds:0
evicted_keys:0
keyspace_hits:0
keyspace_misses:0
pubsub_channels:0
pubsub_patterns:0
latest_fork_usec:0
migrate_cached_sockets:0
slave_expires_tracked_keys:0
active_defrag_hits:0
active_defrag_misses:0
active_defrag_key_hits:0
active_defrag_key_misses:0
tracking_total_keys:0
tracking_total_items:0
tracking_total_prefixes:0
unexpected_error_replies:0
total_reads_processed:0
total_writes_processed:0
io_threaded_reads_processed:0
io_threaded_writes_processed:0

# Replication
role:master
connected_slaves:0
master_replid:ad06260eea9256ff5545b692a75f91e39ede3b55
master_replid2:0000000000000000000000000000000000000000
master_repl_offset:0
second_repl_offset:-1
repl_backlog_active:0
repl_backlog_size:1048576
repl_backlog_first_byte_offset:0
repl_backlog_histlen:0

# CPU
used_cpu_sys:0.964259
used_cpu_user:30.028085
used_cpu_sys_children:0.000000
used_cpu_user_children:0.000000

# Modules

# Commandstats

# Cluster
cluster_enabled:0

# Keyspace
db0:keys=2116880,expires=8954,avg_ttl=0

------ CLIENT LIST OUTPUT ------

------ REGISTERS ------
1660:M 05 Feb 2021 22:33:44.284 # 
RAX:7b141380806422bc RBX:00007f99c1499a40
RCX:cbe48136d6963abe RDX:067953052d48968a
RDI:d5daaff3e5ee034b RSI:4000000000000000
RBP:0000000000000000 RSP:00007fffa0d6c7e8
R8 :00007f9a7e7ffff9 R9 :00007f984e174f89
R10:0000000000000000 R11:736f6d6570736575
R12:0000000000000000 R13:00007fffa0d6c8e0
R14:00007f99c1499a40 R15:00007f98bba00149
RIP:0000559cbde51e40 EFL:0000000000010287
CSGSFS:002b000000000033
1660:M 05 Feb 2021 22:33:44.284 # (00007fffa0d6c7f7) -> 00007f99c14c9a40
1660:M 05 Feb 2021 22:33:44.284 # (00007fffa0d6c7f6) -> 0000000000000003
1660:M 05 Feb 2021 22:33:44.284 # (00007fffa0d6c7f5) -> 0000000000000002
1660:M 05 Feb 2021 22:33:44.284 # (00007fffa0d6c7f4) -> 0000559cbddc29c1
1660:M 05 Feb 2021 22:33:44.284 # (00007fffa0d6c7f3) -> 00007fffa0d6ce60
1660:M 05 Feb 2021 22:33:44.284 # (00007fffa0d6c7f2) -> 00007f98bba00149
1660:M 05 Feb 2021 22:33:44.284 # (00007fffa0d6c7f1) -> 00007fffa0d6c8e0
1660:M 05 Feb 2021 22:33:44.284 # (00007fffa0d6c7f0) -> 0000000000000000
1660:M 05 Feb 2021 22:33:44.284 # (00007fffa0d6c7ef) -> 0000000000000003
1660:M 05 Feb 2021 22:33:44.284 # (00007fffa0d6c7ee) -> 00007f99c1499a40
1660:M 05 Feb 2021 22:33:44.284 # (00007fffa0d6c7ed) -> 00007f99c14c9a40
1660:M 05 Feb 2021 22:33:44.284 # (00007fffa0d6c7ec) -> 0000559cbddee4c8
1660:M 05 Feb 2021 22:33:44.284 # (00007fffa0d6c7eb) -> 0000000000000000
1660:M 05 Feb 2021 22:33:44.284 # (00007fffa0d6c7ea) -> 00007f99c14d3021
1660:M 05 Feb 2021 22:33:44.284 # (00007fffa0d6c7e9) -> 0000000000000004
1660:M 05 Feb 2021 22:33:44.284 # (00007fffa0d6c7e8) -> 0000559cbddc27fa

------ MODULES INFO OUTPUT ------

------ FAST MEMORY TEST ------
1660:M 05 Feb 2021 22:33:44.285 # Bio thread for job type #0 terminated
1660:M 05 Feb 2021 22:33:44.285 # Bio thread for job type #1 terminated
1660:M 05 Feb 2021 22:33:44.285 # Bio thread for job type #2 terminated
*** Preparing to test memory region 559cbdec5000 (118784 bytes)
*** Preparing to test memory region 7f98bba00000 (7564427264 bytes)
*** Preparing to test memory region 7f9a7e915000 (92274688 bytes)
*** Preparing to test memory region 7f9a84116000 (8388608 bytes)
*** Preparing to test memory region 7f9a84917000 (8388608 bytes)
*** Preparing to test memory region 7f9a85118000 (8388608 bytes)
*** Preparing to test memory region 7f9a85919000 (8388608 bytes)
*** Preparing to test memory region 7f9a86400000 (8388608 bytes)
*** Preparing to test memory region 7f9a86d2a000 (32768 bytes)
*** Preparing to test memory region 7f9a86e9b000 (8192 bytes)
*** Preparing to test memory region 7f9a870a9000 (12288 bytes)
*** Preparing to test memory region 7f9a8726d000 (16384 bytes)
*** Preparing to test memory region 7f9a8728f000 (24576 bytes)
*** Preparing to test memory region 7f9a87585000 (16384 bytes)
*** Preparing to test memory region 7f9a876bb000 (4096 bytes)
*** Preparing to test memory region 7f9a878aa000 (2236416 bytes)
*** Preparing to test memory region 7f9a87f16000 (4096 bytes)
*** Preparing to test memory region 7f9a87f1d000 (8192 bytes)
*** Preparing to test memory region 7f9a87f59000 (4096 bytes)
.O.




Thanks.



## Curated Answers



### High Signal Answer 1

@yoav-steinberg `clen` may not be the compressed length of `nodebbpostsearch:id:329783:indices`, I have tested that it is not compressed successfully by `lzf_compress`.
The `clen` may be the length of the last string that was compressed.

- Author: sundb
- Quality score: 4
- URL: https://github.com/redis/redis/issues/8455#issuecomment-986364592
