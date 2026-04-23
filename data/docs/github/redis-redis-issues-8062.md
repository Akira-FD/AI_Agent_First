# [CRASH] Unable to start redis-server on Apple Silicon M1 as non-root



## GitHub Provenance



- Repository: redis/redis

- Issue: #8062

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/8062



## Problem



**Crash report**

Paste the complete crash log between the quotes below. Please include a few lines from the log preceding the crash report to provide some context.

```
nick@nicks-mba bin % redis-server
4428:C 17 Nov 2020 21:38:11.216 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
4428:C 17 Nov 2020 21:38:11.216 # Redis version=6.0.9, bits=64, commit=00000000, modified=0, pid=4428, just started
4428:C 17 Nov 2020 21:38:11.216 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
4428:M 17 Nov 2020 21:38:11.218 * Increased maximum number of open files to 10032 (it was originally set to 256).

=== REDIS BUG REPORT START: Cut & paste starting from here ===
4428:M 17 Nov 2020 21:38:11.221 # Redis 6.0.9 crashed by signal: 11, si_code: 2
4428:M 17 Nov 2020 21:38:11.221 # Crashed running the instruction at: 0x7fff203b9430
4428:M 17 Nov 2020 21:38:11.221 # Accessing address: 0x306018000
4428:M 17 Nov 2020 21:38:11.221 # Killed by PID: 0, UID: 0
4428:M 17 Nov 2020 21:38:11.221 # Failed assertion: <no assertion failed> (<no file>:0)

------ STACK TRACE ------
EIP:
0   libsystem_platform.dylib            0x00007fff203b9430 _platform_memset$VARIANT$Rosetta + 108

Backtrace:
0   redis-server                        0x0000000100eecbb7 logStackTrace + 110
1   redis-server                        0x0000000100eecfd5 sigsegvHandler + 271
2   libsystem_platform.dylib            0x00007fff203b6d7d _sigtramp + 29
3   libsystem_malloc.dylib              0x00007fff2019c7aa tiny_free_no_lock + 1116
4   redis-server                        0x0000000100f3d0c3 luaD_call + 97
5   ???                                 0x0000000032aaaba2 0x0 + 850045858

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
process_id:4428
run_id:fc5670f4b55a97402bd9c0257ddf857c0f4879c7
tcp_port:6379
uptime_in_seconds:0
uptime_in_days:0
hz:10
configured_hz:10
lru_clock:11831571
executable:/usr/local/Cellar/redis/6.0.9/bin/redis-server
config_file:
io_threads_active:0

# Clients
connected_clients:0
client_recent_max_input_buffer:0
client_recent_max_output_buffer:0
blocked_clients:0
tracking_clients:0
clients_in_timeout_table:0

# Memory
used_memory:1018304
used_memory_human:994.44K
used_memory_rss:0
used_memory_rss_human:0B
used_memory_peak:1018304
used_memory_peak_human:994.44K
used_memory_peak_perc:inf%
used_memory_overhead:0
used_memory_startup:0
used_memory_dataset:1018304
used_memory_dataset_perc:100.00%
allocator_allocated:0
allocator_active:0
allocator_resident:0
total_system_memory:17179869184
total_system_memory_human:16.00G
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
rdb_last_save_time:1605667091
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
master_replid:46fd7b1f73d20d31809d463ca9fa6e83dd8544ff
master_replid2:0000000000000000000000000000000000000000
master_repl_offset:0
second_repl_offset:-1
repl_backlog_active:0
repl_backlog_size:1048576
repl_backlog_first_byte_offset:0
repl_backlog_histlen:0

# CPU
used_cpu_sys:0.007195
used_cpu_user:0.014509
used_cpu_sys_children:0.000000
used_cpu_user_children:0.000000

# Modules

# Commandstats

# Cluster
cluster_enabled:0

# Keyspace

------ CLIENT LIST OUTPUT ------

------ REGISTERS ------
4428:M 17 Nov 2020 21:38:11.222 #
RAX:0000000306017b80 RBX:0000000000000013
RCX:0000000306018000 RDX:00007fd6be3ed8ce
RDI:0000000306017b38 RSI:0000000000000000
RBP:0000000306017910 RSP:0000000306017728
R8 :0000000000000000 R9 :00000003060177e0
R10:0000000100f587b3 R11:ffffffffffffffff
R12:00000003060179b8 R13:00000000000000ff
R14:0000000100f59127 R15:0000000100f89740
RIP:00007fff203b9430 EFL:0000000000000202
CS :000000000000002b FS:0000000000000000  GS:0000000000000000
4428:M 17 Nov 2020 21:38:11.222 # (0000000306017737) -> 0000000109a3ea00
4428:M 17 Nov 2020 21:38:11.222 # (0000000306017736) -> 0000000000000006
4428:M 17 Nov 2020 21:38:11.222 # (0000000306017735) -> 0000000000000000
4428:M 17 Nov 2020 21:38:11.222 # (0000000306017734) -> 0000000000002800
4428:M 17 Nov 2020 21:38:11.222 # (0000000306017733) -> 0000000000000000
4428:M 17 Nov 2020 21:38:11.222 # (0000000306017732) -> 00007fff2019a020
4428:M 17 Nov 2020 21:38:11.222 # (0000000306017731) -> 0000000100f67bca
4428:M 17 Nov 2020 21:38:11.222 # (0000000306017730) -> 0000000100efb4d6
4428:M 17 Nov 2020 21:38:11.222 # (000000030601772f) -> 00000003060178a0
4428:M 17 Nov 2020 21:38:11.222 # (000000030601772e) -> 00007fd9c4400000
4428:M 17 Nov 2020 21:38:11.222 # (000000030601772d) -> 0000000100f5ad38
4428:M 17 Nov 2020 21:38:11.222 # (000000030601772c) -> 00000000000018eb
4428:M 17 Nov 2020 21:38:11.222 # (000000030601772b) -> 0000000100f55bcd
4428:M 17 Nov 2020 21:38:11.222 # (000000030601772a) -> 0000000306017b38
4428:M 17 Nov 2020 21:38:11.223 # (0000000306017729) -> 00007fd9c445a3b0
4428:M 17 Nov 2020 21:38:11.223 # (0000000306017728) -> 0000000100f0bebb

------ MODULES INFO OUTPUT ------

------ DUMPING CODE AROUND EIP ------
Symbol: _platform_memset$VARIANT$Rosetta (base: 0x7fff203b93c4)
Module: /usr/lib/system/libsystem_platform.dylib (base 0x7fff203b3000)
$ xxd -r -p /tmp/dump.hex /tmp/dump.bin
$ objdump --adjust-vma=0x7fff203b93c4 -D -b binary -m i386:x86-64 /tmp/dump.bin
------
4428:M 17 Nov 2020 21:38:11.223 # dump of function (hexdump of 236 bytes):
81e6ff00000048b90101010101010101480faff14889f94883fa400f82360100004881fa008000000f82a00000000faef0480fc337480fc37708480fc37710480fc37718480fc37720480fc37728480fc37730480fc37738488d4f404883e1c04801fa488d41404829c27631480fc331480fc37108480fc37110480fc37118480fc37120480fc37128480fc37130480fc371384883c1404883ea4077cf4801d1480fc331480fc37108480fc37110480fc37118480fc37120480fc37128480fc37130480fc371380faef84889f8c3488937488977084889771048897718488977204889772848897730488977

=== REDIS BUG REPORT END. Make sure to include from START to END. ===
```

**Aditional information**

*OS distribution and version:* macOS Big Sur 11.0.1, MacBook Air M1 (8-core, 7-core GPU)
*Steps to reproduce (if any)*
1. Installed via Rosetta-run Homebrew `arch -x86_64 brew install redis`.
2. Run `redis-server` or `arch -x86_64 redis-server` as a normal user.
3. Crash. 

Runs without issue with `sudo`.



## Curated Answers



### High Signal Answer 1

I also noticed this when trying to use Redis with homebrew on an M1 Mac. Homebrew reports that it started the server correctly, but it does not. 

Running `redis-server` fails, but running `sudo redis-server` works. This is running x86_64 binary after being translated.

For folks who might be finding this thread, a "workaround" in the meantime is to start the Redis server like this manually:
```
sudo redis-server --daemonize yes
```

- Author: austenc
- Quality score: 53
- URL: https://github.com/redis/redis/issues/8062#issuecomment-731768818

### High Signal Answer 2

> As for why _sudo_ works around the issue, it changes the env variables!

Aha! That helped me find this simple workaround:

```
env -i /usr/local/bin/redis-server --daemonize yes
```

(Yep, I just got a new M1 mac.)

- Author: anamba
- Quality score: 28
- URL: https://github.com/redis/redis/issues/8062#issuecomment-749311875

### High Signal Answer 3

It does succeed with sudo

- Author: tf-ddanilyuk
- Quality score: 25
- URL: https://github.com/redis/redis/issues/8062#issuecomment-730201975
