# [BUG] Could not connect to Redis at 127.0.0.1:6379: Connection refused - Apple Silicon



## GitHub Provenance



- Repository: redis/redis

- Issue: #8177

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/8177



## Problem



Redis is failing when I try to, for example, ping redis-cli. I have tried reinstalling but it's not working. On the output of the terminal I got a message to report the issue "Please report the crash by opening an issue on github..."

To reproduce the error I execute redis-cli ping, redis-server /usr/local/etc/redis.conf, redis-server, etc. 

4325:M 13 Dec 2020 02:35:38.910 # Redis 6.0.9 crashed by signal: 11, si_code: 2
4325:M 13 Dec 2020 02:35:38.911 # Crashed running the instruction at: 0x7fff2039d430
4325:M 13 Dec 2020 02:35:38.911 # Accessing address: 0x3049c6000
4325:M 13 Dec 2020 02:35:38.911 # Killed by PID: 0, UID: 0
4325:M 13 Dec 2020 02:35:38.911 # Failed assertion: <no assertion failed> (<no file>:0)

------ STACK TRACE ------
EIP:
0   libsystem_platform.dylib            0x00007fff2039d430 _platform_memset$VARIANT$Rosetta + 108

Backtrace:
0   redis-server                        0x00000001003b8bb7 logStackTrace + 110
1   redis-server                        0x00000001003b8fd5 sigsegvHandler + 271
2   libsystem_platform.dylib            0x00007fff2039ad7d _sigtramp + 29
3   libsystem_malloc.dylib              0x00007fff201807aa tiny_free_no_lock + 1116
4   libsystem_c.dylib                   0x00007fff20263729 fopen + 116
5   redis-server                        0x000000010037d045 createPidFile + 53
6   redis-server                        0x000000010037df9d main + 1163
7   libdyld.dylib                       0x00007fff20371631 start + 1

------ INFO OUTPUT ------
# Server
redis_version:6.0.9
redis_git_sha1:00000000
redis_git_dirty:0
redis_build_id:ec508acaad782189
redis_mode:standalone
os:Darwin 20.1.0 x86_64
arch_bits:64
multiplexing_api:kqueue
atomicvar_api:atomic-builtin
gcc_version:4.2.1
process_id:4325
run_id:e7f0883bfeb16abaadb5c69bb6666e3a64044653
tcp_port:6379
uptime_in_seconds:0
uptime_in_days:0
hz:10
configured_hz:10
lru_clock:14002218
executable:/Users/gabo/redis-server
config_file:/usr/local/etc/redis.conf
io_threads_active:0

# Clients
connected_clients:0
client_recent_max_input_buffer:0
client_recent_max_output_buffer:0
blocked_clients:0
tracking_clients:0
clients_in_timeout_table:0

# Memory
used_memory:1019424
used_memory_human:995.53K
used_memory_rss:0
used_memory_rss_human:0B
used_memory_peak:1019424
used_memory_peak_human:995.53K
used_memory_peak_perc:inf%
used_memory_overhead:0
used_memory_startup:0
used_memory_dataset:1019424
used_memory_dataset_perc:100.00%
allocator_allocated:0
allocator_active:0
allocator_resident:0
total_system_memory:8589934592
total_system_memory_human:8.00G
used_memory_lua:37888
used_memory_lua_human:37.00K
used_memory_scripts:0
used_memory_scripts_human:0B
number_of_cached_scripts:0
maxmemory:0
maxmemory_human:0B
maxmemory_policy:noeviction
allocator_frag_ratio:nan
allocator_frag_bytes:0
allocator_rss_ratio:nan
allocator_rss_bytes:0
rss_overhead_ratio:nan
rss_overhead_bytes:0
mem_fragmentation_ratio:nan
mem_fragmentation_bytes:0
mem_not_counted_for_evict:0
mem_replication_backlog:0
mem_clients_slaves:0
mem_clients_normal:0
mem_aof_buffer:0
mem_allocator:libc
active_defrag_running:0
lazyfree_pending_objects:0

# Persistence
loading:0
rdb_changes_since_last_save:0
rdb_bgsave_in_progress:0
rdb_last_save_time:1607837738
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
master_replid:0746201791068712f7468292cc49f2a7e980ef64
master_replid2:0000000000000000000000000000000000000000
master_repl_offset:0
second_repl_offset:-1
repl_backlog_active:0
repl_backlog_size:1048576
repl_backlog_first_byte_offset:0
repl_backlog_histlen:0

# CPU
used_cpu_sys:0.006207
used_cpu_user:0.016609
used_cpu_sys_children:0.000000
used_cpu_user_children:0.000000

# Modules

# Commandstats

# Cluster
cluster_enabled:0

# Keyspace

------ CLIENT LIST OUTPUT ------

------ REGISTERS ------
4325:M 13 Dec 2020 02:35:38.912 #
RAX:00000003049c5b80 RBX:000000000000001b
RCX:00000003049c6000 RDX:00007fc04c23f8be
RDI:00000003049c5b30 RSI:0000000000000000
RBP:00000003049c58f0 RSP:00000003049c5708
R8 :0000000000000000 R9 :00000003049c57c0
R10:00000001004247b3 R11:ffffffffffffffff
R12:00000003049c5998 R13:00000000000000ff
R14:0000000100425127 R15:0000000100455740
RIP:00007fff2039d430 EFL:0000000000000206
CS :000000000000002b FS:0000000000000000  GS:0000000000000000
4325:M 13 Dec 2020 02:35:38.912 # (00000003049c5717) -> 0000000108f0aa00
4325:M 13 Dec 2020 02:35:38.912 # (00000003049c5716) -> 0000000000000006
4325:M 13 Dec 2020 02:35:38.912 # (00000003049c5715) -> 0000000000000000
4325:M 13 Dec 2020 02:35:38.912 # (00000003049c5714) -> 0000000000003c00
4325:M 13 Dec 2020 02:35:38.912 # (00000003049c5713) -> 0000000000000000
4325:M 13 Dec 2020 02:35:38.912 # (00000003049c5712) -> 00007fff2017e020
4325:M 13 Dec 2020 02:35:38.912 # (00000003049c5711) -> 00000003049c5790
4325:M 13 Dec 2020 02:35:38.912 # (00000003049c5710) -> 0000000108f0e600
4325:M 13 Dec 2020 02:35:38.912 # (00000003049c570f) -> 0000000000000006
4325:M 13 Dec 2020 02:35:38.912 # (00000003049c570e) -> ffffffff00000000
4325:M 13 Dec 2020 02:35:38.912 # (00000003049c570d) -> 0000000100426d38
4325:M 13 Dec 2020 02:35:38.912 # (00000003049c570c) -> 00000000000018eb
4325:M 13 Dec 2020 02:35:38.912 # (00000003049c570b) -> 00007fc350c47520
4325:M 13 Dec 2020 02:35:38.912 # (00000003049c570a) -> 00000003049c5b30
4325:M 13 Dec 2020 02:35:38.912 # (00000003049c5709) -> 00007fc350c5a5d0
4325:M 13 Dec 2020 02:35:38.912 # (00000003049c5708) -> 00000001003d7ebb

------ MODULES INFO OUTPUT ------

------ DUMPING CODE AROUND EIP ------
Symbol: _platform_memset$VARIANT$Rosetta (base: 0x7fff2039d3c4)
Module: /usr/lib/system/libsystem_platform.dylib (base 0x7fff20397000)
$ xxd -r -p /tmp/dump.hex /tmp/dump.bin
$ objdump --adjust-vma=0x7fff2039d3c4 -D -b binary -m i386:x86-64 /tmp/dump.bin
------
4325:M 13 Dec 2020 02:35:38.912 # dump of function (hexdump of 236 bytes):
81e6ff00000048b90101010101010101480faff14889f94883fa400f82360100004881fa008000000f82a00000000faef0480fc337480fc37708480fc37710480fc37718480fc37720480fc37728480fc37730480fc37738488d4f404883e1c04801fa488d41404829c27631480fc331480fc37108480fc37110480fc37118480fc37120480fc37128480fc37130480fc371384883c1404883ea4077cf4801d1480fc331480fc37108480fc37110480fc37118480fc37120480fc37128480fc37130480fc371380faef84889f8c3488937488977084889771048897718488977204889772848897730488977



## Curated Answers



### High Signal Answer 1

@GFPdu this reminds me a stack trace i've seen in #8062
Are you by any chance using Apple Silicon?
Can you try to build redis from the `unstable` branch?

- Author: oranagra
- Quality score: 4
- URL: https://github.com/redis/redis/issues/8177#issuecomment-743969255
