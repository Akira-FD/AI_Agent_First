# [BUG] Docker image fails redis/redis-stack:latest on MacOs



## GitHub Provenance



- Repository: redis/redis

- Issue: #14894

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/14894



## Problem



**Describe the bug**

**To reproduce**

docker compose -f compose.yaml up redis
Code of `compose.yaml`:
```yaml
services:
  redis:
    image: "redis/redis-stack:latest"
    env_file: "docker/redis/env"
    ports:
      - "6379:6379"
      - "8001:8001"
```
Creating index via llama_index & inserting a nodes (example are below)

Machine
Chip: Apple M4 Pro
Memory: 24 GB
MacOs 15.7.4 (24G517)

**Expected behavior**
The latest version llama-index works is "redis/redis-stack:6.2.6-v20".

**Additional information**

Full log:
```
redis-1  | === REDIS BUG REPORT START: Cut & paste starting from here ===
redis-1  | 9:M 16 Mar 2026 16:55:56.492 # Redis 7.4.7 crashed by signal: 4, si_code: 1
redis-1  | 9:M 16 Mar 2026 16:55:56.492 # Crashed running the instruction at: 0xffff89d5a9d0
redis-1  | 
redis-1  | ------ STACK TRACE ------
redis-1  | EIP:
redis-1  | /opt/redis-stack/lib/redisearch.so(_ZN6spaces34Choose_FP32_IP_implementation_SVE2Em+0x0)[0xffff89d5a9d0]
redis-1  | 
redis-1  | 17 bio_close_file
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0x7cb7c)[0xffff8a2ccb7c]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(pthread_cond_wait+0x210)[0xffff8a2cf694]
redis-1  | /opt/redis-stack/bin/redis-server *:6379(bioProcessBackgroundJobs+0x1e4)[0xaaaae2afe814]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0x80398)[0xffff8a2d0398]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0xe9e9c)[0xffff8a339e9c]
redis-1  | 
redis-1  | 16 V8 DefaultWorke
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0x7cb7c)[0xffff8a2ccb7c]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(pthread_cond_wait+0x210)[0xffff8a2cf694]
redis-1  | /opt/redis-stack/lib/libredisgears_v8_plugin.so(+0x1cce24)[0xffff873cce24]
redis-1  | /opt/redis-stack/lib/libredisgears_v8_plugin.so(+0xa1ec98)[0xffff87c1ec98]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0x80398)[0xffff8a2d0398]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0xe9e9c)[0xffff8a339e9c]
redis-1  | 
redis-1  | 28 gc-6235
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0x7cb7c)[0xffff8a2ccb7c]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(pthread_cond_wait+0x210)[0xffff8a2cf694]
redis-1  | /opt/redis-stack/lib/redisearch.so(+0x181648)[0xffff89b81648]
redis-1  | /opt/redis-stack/lib/redisearch.so(+0x1814bc)[0xffff89b814bc]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0x80398)[0xffff8a2d0398]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0xe9e9c)[0xffff8a339e9c]
redis-1  | 
redis-1  | 18 bio_aof
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0x7cb7c)[0xffff8a2ccb7c]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(pthread_cond_wait+0x210)[0xffff8a2cf694]
redis-1  | /opt/redis-stack/bin/redis-server *:6379(bioProcessBackgroundJobs+0x1e4)[0xaaaae2afe814]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0x80398)[0xffff8a2d0398]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0xe9e9c)[0xffff8a339e9c]
redis-1  | 
redis-1  | 21 cleanPool-6837
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0x7cb7c)[0xffff8a2ccb7c]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(pthread_cond_wait+0x210)[0xffff8a2cf694]
redis-1  | /opt/redis-stack/lib/redisearch.so(+0x181648)[0xffff89b81648]
redis-1  | /opt/redis-stack/lib/redisearch.so(+0x1814bc)[0xffff89b814bc]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0x80398)[0xffff8a2d0398]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0xe9e9c)[0xffff8a339e9c]
redis-1  | 
redis-1  | 19 bio_lazy_free
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0x7cb7c)[0xffff8a2ccb7c]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(pthread_cond_wait+0x210)[0xffff8a2cf694]
redis-1  | /opt/redis-stack/bin/redis-server *:6379(bioProcessBackgroundJobs+0x1e4)[0xaaaae2afe814]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0x80398)[0xffff8a2d0398]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0xe9e9c)[0xffff8a339e9c]
redis-1  | 
redis-1  | 20 reindex-4736
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0x7cb7c)[0xffff8a2ccb7c]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(pthread_cond_wait+0x210)[0xffff8a2cf694]
redis-1  | /opt/redis-stack/lib/redisearch.so(+0x181648)[0xffff89b81648]
redis-1  | /opt/redis-stack/lib/redisearch.so(+0x1814bc)[0xffff89b814bc]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0x80398)[0xffff8a2d0398]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0xe9e9c)[0xffff8a339e9c]
redis-1  | 
redis-1  | 9 redis-server *
redis-1  | linux-vdso.so.1(__kernel_rt_sigreturn+0x0)[0xffff8a9dc7a0]
redis-1  | /opt/redis-stack/bin/redis-server *:6379(invalidFunctionWasCalled+0x0)[0xaaaae2ad32f0]
redis-1  | /opt/redis-stack/lib/redisearch.so(_ZN9HNSWIndexIffEC1EPK10HNSWParamsRK23AbstractIndexInitParamsmm+0x11c)[0xffff89d1da2c]
redis-1  | /opt/redis-stack/lib/redisearch.so(_ZN11HNSWFactory8NewIndexEPK12VecSimParams+0x104)[0xffff89cea4e8]
redis-1  | /opt/redis-stack/lib/redisearch.so(_ZN13TieredFactory17TieredHNSWFactory8NewIndexEPK17TieredIndexParams+0x8c)[0xffff89d21e7c]
redis-1  | /opt/redis-stack/lib/redisearch.so(_ZN13VecSimFactory8NewIndexEPK12VecSimParams+0xcc)[0xffff89cc68dc]
redis-1  | /opt/redis-stack/lib/redisearch.so(openVectorIndex+0xe4)[0xffff89c1c7d4]
redis-1  | /opt/redis-stack/lib/redisearch.so(IndexerBulkAdd+0x2b0)[0xffff89bb0b10]
redis-1  | /opt/redis-stack/lib/redisearch.so(Indexer_Add+0x53c)[0xffff89bc8ce0]
redis-1  | /opt/redis-stack/lib/redisearch.so(Document_AddToIndexes+0x10c)[0xffff89bb0d2c]
redis-1  | /opt/redis-stack/lib/redisearch.so(IndexSpec_UpdateDoc+0x200)[0xffff89c04414]
redis-1  | /opt/redis-stack/lib/redisearch.so(Indexes_UpdateMatchingWithSchemaRules+0xc4)[0xffff89c04b28]
redis-1  | /opt/redis-stack/lib/redisearch.so(HashNotificationCallback+0x134)[0xffff89bd6944]
redis-1  | /opt/redis-stack/bin/redis-server *:6379(+0x19ab30)[0xaaaae2b4ab30]
redis-1  | /opt/redis-stack/bin/redis-server *:6379(notifyKeyspaceEvent+0x34)[0xaaaae2b158c4]
redis-1  | /opt/redis-stack/bin/redis-server *:6379(hsetCommand+0x148)[0xaaaae2ab7edc]
redis-1  | /opt/redis-stack/bin/redis-server *:6379(call+0x170)[0xaaaae2a44c54]
redis-1  | /opt/redis-stack/bin/redis-server *:6379(processCommand+0x410)[0xaaaae2a468b0]
redis-1  | /opt/redis-stack/bin/redis-server *:6379(processInputBuffer+0xe0)[0xaaaae2a664b4]
redis-1  | /opt/redis-stack/bin/redis-server *:6379(readQueryFromClient+0x3a4)[0xaaaae2a66a24]
redis-1  | /opt/redis-stack/bin/redis-server *:6379(+0x1bf590)[0xaaaae2b6f590]
redis-1  | /opt/redis-stack/bin/redis-server *:6379(aeMain+0x12c)[0xaaaae2a31f7c]
redis-1  | /opt/redis-stack/bin/redis-server *:6379(main+0x568)[0xaaaae2a274a8]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(+0x27400)[0xffff8a277400]
redis-1  | /lib/aarch64-linux-gnu/libc.so.6(__libc_start_main+0x98)[0xffff8a2774d8]
redis-1  | /opt/redis-stack/bin/redis-server *:6379(_start+0x30)[0xaaaae2a27b70]
redis-1  | 
redis-1  | 8/8 expected stacktraces.
redis-1  | 
redis-1  | ------ STACK TRACE DONE ------
redis-1  | 
redis-1  | ------ REGISTERS ------
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # 
redis-1  | X18:0000000000000000 X19:0000aaab1001a878
redis-1  | X20:0000aaab1001a880 X21:0000000000000064
redis-1  | X22:0000ffff8a089c80 X23:0000ffffd70585a0
redis-1  | X24:0000000000001000 X25:0000ffffd7058510
redis-1  | X26:0000aaab0ffac958 X27:0000aaab0ff82f98
redis-1  | X28:0000000000000001 X29:0000ffffd70584a0
redis-1  | X30:0000ffff89d1da2c
redis-1  | pc:0000ffff89d5a9d0 sp:0000ffffd70584a0
redis-1  | pstate:0000000060000000 fault_address:0000000000000000
redis-1  | 
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # (0000ffffd70584af) -> 0000aaab1001a830
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # (0000ffffd70584ae) -> 0000aaab1001a850
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # (0000ffffd70584ad) -> 0000aaab1001a830
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # (0000ffffd70584ac) -> 0000ffffd7058530
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # (0000ffffd70584ab) -> 0000aaab0ff84070
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # (0000ffffd70584aa) -> 0000aaab0ffaa990
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # (0000ffffd70584a9) -> 0000aaab0ffac958
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # (0000ffffd70584a8) -> 0000000000000001
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # (0000ffffd70584a7) -> 0000aaab0ffabd50
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # (0000ffffd70584a6) -> 0000aaab0ffabd63
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # (0000ffffd70584a5) -> 0000ffffd7058570
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # (0000ffffd70584a4) -> 0000ffffd70585a0
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # (0000ffffd70584a3) -> 0000aaab0ff82f98
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # (0000ffffd70584a2) -> 0000aaab1001a878
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # (0000ffffd70584a1) -> 0000ffff89cea4e8
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # (0000ffffd70584a0) -> 0000ffffd7058530
redis-1  | 
redis-1  | ------ INFO OUTPUT ------
redis-1  | # Server
redis-1  | redis_version:7.4.7
redis-1  | redis_git_sha1:00000000
redis-1  | redis_git_dirty:0
redis-1  | redis_build_id:35af8276b891a7b7
redis-1  | redis_mode:standalone
redis-1  | os:Linux 6.10.14-linuxkit aarch64
redis-1  | arch_bits:64
redis-1  | monotonic_clock:POSIX clock_gettime
redis-1  | multiplexing_api:epoll
redis-1  | atomicvar_api:c11-builtin
redis-1  | gcc_version:11.4.0
redis-1  | process_id:9
redis-1  | process_supervised:no
redis-1  | run_id:130c21c22f24b177baa92e7d5a73fec6d4e5c127
redis-1  | tcp_port:6379
redis-1  | server_time_usec:1773680156491387
redis-1  | uptime_in_seconds:54
redis-1  | uptime_in_days:0
redis-1  | hz:10
redis-1  | configured_hz:10
redis-1  | lru_clock:12072476
redis-1  | executable:/opt/redis-stack/bin/redis-server
redis-1  | config_file:
redis-1  | io_threads_active:0
redis-1  | listener0:name=tcp,bind=*,bind=-::*,port=6379
redis-1  | 
redis-1  | # Clients
redis-1  | connected_clients:4
redis-1  | cluster_connections:0
redis-1  | maxclients:10000
redis-1  | client_recent_max_input_buffer:16408
redis-1  | client_recent_max_output_buffer:0
redis-1  | blocked_clients:0
redis-1  | tracking_clients:0
redis-1  | pubsub_clients:0
redis-1  | watching_clients:0
redis-1  | clients_in_timeout_table:0
redis-1  | total_watched_keys:0
redis-1  | total_blocking_keys:0
redis-1  | total_blocking_keys_on_nokey:0
redis-1  | 
redis-1  | # Memory
redis-1  | used_memory:2117488
redis-1  | used_memory_human:2.02M
redis-1  | used_memory_rss:21168128
redis-1  | used_memory_rss_human:20.19M
redis-1  | used_memory_peak:2117488
redis-1  | used_memory_peak_human:2.02M
redis-1  | used_memory_peak_perc:103.70%
redis-1  | used_memory_overhead:1425616
redis-1  | used_memory_startup:1368280
redis-1  | used_memory_dataset:691872
redis-1  | used_memory_dataset_perc:92.35%
redis-1  | allocator_allocated:2041016
redis-1  | allocator_active:21168128
redis-1  | allocator_resident:21168128
redis-1  | allocator_muzzy:0
redis-1  | total_system_memory:8217407488
redis-1  | total_system_memory_human:7.65G
redis-1  | used_memory_lua:32768
redis-1  | used_memory_vm_eval:32768
redis-1  | used_memory_lua_human:32.00K
redis-1  | used_memory_scripts_eval:0
redis-1  | number_of_cached_scripts:0
redis-1  | number_of_functions:0
redis-1  | number_of_libraries:0
redis-1  | used_memory_vm_functions:33792
redis-1  | used_memory_vm_total:66560
redis-1  | used_memory_vm_total_human:65.00K
redis-1  | used_memory_functions:232
redis-1  | used_memory_scripts:232
redis-1  | used_memory_scripts_human:232B
redis-1  | maxmemory:0
redis-1  | maxmemory_human:0B
redis-1  | maxmemory_policy:noeviction
redis-1  | allocator_frag_ratio:1.00
redis-1  | allocator_frag_bytes:0
redis-1  | allocator_rss_ratio:1.00
redis-1  | allocator_rss_bytes:0
redis-1  | rss_overhead_ratio:1.00
redis-1  | rss_overhead_bytes:0
redis-1  | mem_fragmentation_ratio:10.37
redis-1  | mem_fragmentation_bytes:19127112
redis-1  | mem_not_counted_for_evict:920
redis-1  | mem_replication_backlog:0
redis-1  | mem_total_replication_buffers:0
redis-1  | mem_clients_slaves:0
redis-1  | mem_clients_normal:55616
redis-1  | mem_cluster_links:0
redis-1  | mem_aof_buffer:920
redis-1  | mem_allocator:libc
redis-1  | mem_overhead_db_hashtable_rehashing:0
redis-1  | active_defrag_running:0
redis-1  | lazyfree_pending_objects:0
redis-1  | lazyfreed_objects:0
redis-1  | 
redis-1  | # Persistence
redis-1  | loading:0
redis-1  | async_loading:0
redis-1  | current_cow_peak:0
redis-1  | current_cow_size:0
redis-1  | current_cow_size_age:0
redis-1  | current_fork_perc:0.00
redis-1  | current_save_keys_processed:0
redis-1  | current_save_keys_total:0
redis-1  | rdb_changes_since_last_save:27
redis-1  | rdb_bgsave_in_progress:0
redis-1  | rdb_last_save_time:1773680102
redis-1  | rdb_last_bgsave_status:ok
redis-1  | rdb_last_bgsave_time_sec:-1
redis-1  | rdb_current_bgsave_time_sec:-1
redis-1  | rdb_saves:0
redis-1  | rdb_last_cow_size:0
redis-1  | rdb_last_load_keys_expired:0
redis-1  | rdb_last_load_keys_loaded:0
redis-1  | aof_enabled:1
redis-1  | aof_rewrite_in_progress:0
redis-1  | aof_rewrite_scheduled:0
redis-1  | aof_last_rewrite_time_sec:-1
redis-1  | aof_current_rewrite_time_sec:-1
redis-1  | aof_last_bgrewrite_status:ok
redis-1  | aof_rewrites:0
redis-1  | aof_rewrites_consecutive_failures:0
redis-1  | aof_last_write_status:ok
redis-1  | aof_last_cow_size:0
redis-1  | module_fork_in_progress:0
redis-1  | module_fork_last_cow_size:0
redis-1  | aof_current_size:24565
redis-1  | aof_base_size:131
redis-1  | aof_pending_rewrite:0
redis-1  | aof_buffer_length:0
redis-1  | aof_pending_bio_fsync:0
redis-1  | aof_delayed_fsync:0
redis-1  | 
redis-1  | # Stats
redis-1  | total_connections_received:5
redis-1  | total_commands_processed:69
redis-1  | instantaneous_ops_per_sec:1
redis-1  | total_net_input_bytes:12462
redis-1  | total_net_output_bytes:100622
redis-1  | total_net_repl_input_bytes:0
redis-1  | total_net_repl_output_bytes:0
redis-1  | instantaneous_input_kbps:0.33
redis-1  | instantaneous_output_kbps:0.01
redis-1  | instantaneous_input_repl_kbps:0.00
redis-1  | instantaneous_output_repl_kbps:0.00
redis-1  | rejected_connections:0
redis-1  | sync_full:0
redis-1  | sync_partial_ok:0
redis-1  | sync_partial_err:0
redis-1  | expired_subkeys:0
redis-1  | expired_keys:0
redis-1  | expired_stale_perc:0.00
redis-1  | expired_time_cap_reached_count:0
redis-1  | expire_cycle_cpu_milliseconds:1
redis-1  | evicted_keys:0
redis-1  | evicted_clients:0
redis-1  | evicted_scripts:0
redis-1  | total_eviction_exceeded_time:0
redis-1  | current_eviction_exceeded_time:0
redis-1  | keyspace_hits:16
redis-1  | keyspace_misses:0
redis-1  | pubsub_channels:0
redis-1  | pubsub_patterns:0
redis-1  | pubsubshard_channels:0
redis-1  | latest_fork_usec:0
redis-1  | total_forks:0
redis-1  | migrate_cached_sockets:0
redis-1  | slave_expires_tracked_keys:0
redis-1  | active_defrag_hits:0
redis-1  | active_defrag_misses:0
redis-1  | active_defrag_key_hits:0
redis-1  | active_defrag_key_misses:0
redis-1  | total_active_defrag_time:0
redis-1  | current_active_defrag_time:0
redis-1  | tracking_total_keys:0
redis-1  | tracking_total_items:0
redis-1  | tracking_total_prefixes:0
redis-1  | unexpected_error_replies:0
redis-1  | total_error_replies:0
redis-1  | dump_payload_sanitizations:0
redis-1  | total_reads_processed:58
redis-1  | total_writes_processed:56
redis-1  | io_threaded_reads_processed:0
redis-1  | io_threaded_writes_processed:0
redis-1  | client_query_buffer_limit_disconnections:0
redis-1  | client_output_buffer_limit_disconnections:0
redis-1  | reply_buffer_shrinks:11
redis-1  | reply_buffer_expands:7
redis-1  | eventloop_cycles:585
redis-1  | eventloop_duration_sum:87201
redis-1  | eventloop_duration_cmd_sum:2105
redis-1  | instantaneous_eventloop_cycles_per_sec:11
redis-1  | instantaneous_eventloop_duration_usec:135
redis-1  | acl_access_denied_auth:0
redis-1  | acl_access_denied_cmd:0
redis-1  | acl_access_denied_key:0
redis-1  | acl_access_denied_channel:0
redis-1  | 
redis-1  | # Replication
redis-1  | role:master
redis-1  | connected_slaves:0
redis-1  | master_failover_state:no-failover
redis-1  | master_replid:08cb7e3b5af99079eeb6416c35387886106cd502
redis-1  | master_replid2:0000000000000000000000000000000000000000
redis-1  | master_repl_offset:5
redis-1  | second_repl_offset:-1
redis-1  | repl_backlog_active:0
redis-1  | repl_backlog_size:1048576
redis-1  | repl_backlog_first_byte_offset:0
redis-1  | repl_backlog_histlen:0
redis-1  | 
redis-1  | # CPU
redis-1  | used_cpu_sys:0.087386
redis-1  | used_cpu_user:0.067330
redis-1  | used_cpu_sys_children:0.000000
redis-1  | used_cpu_user_children:0.000614
redis-1  | used_cpu_sys_main_thread:0.076015
redis-1  | used_cpu_user_main_thread:0.065976
redis-1  | 
redis-1  | # Modules
redis-1  | module:name=search,ver=21020,api=1,filters=0,usedby=[],using=[ReJSON],options=[handle-io-errors]
redis-1  | module:name=RedisCompat,ver=1,api=1,filters=0,usedby=[],using=[],options=[]
redis-1  | module:name=bf,ver=20816,api=1,filters=0,usedby=[],using=[],options=[handle-io-errors]
redis-1  | module:name=redisgears_2,ver=20020,api=1,filters=0,usedby=[],using=[],options=[]
redis-1  | module:name=timeseries,ver=11206,api=1,filters=0,usedby=[],using=[],options=[]
redis-1  | module:name=ReJSON,ver=20809,api=1,filters=0,usedby=[search],using=[],options=[handle-io-errors]
redis-1  | 
redis-1  | # Commandstats
redis-1  | cmdstat_FT.DROPINDEX:calls=1,usec=30,usec_per_call=30.00,rejected_calls=0,failed_calls=0
redis-1  | cmdstat_del:calls=2,usec=121,usec_per_call=60.50,rejected_calls=0,failed_calls=0
redis-1  | cmdstat_FT._LIST:calls=3,usec=54,usec_per_call=18.00,rejected_calls=0,failed_calls=0
redis-1  | cmdstat_httl:calls=2,usec=12,usec_per_call=6.00,rejected_calls=0,failed_calls=0
redis-1  | cmdstat_type:calls=4,usec=10,usec_per_call=2.50,rejected_calls=0,failed_calls=0
redis-1  | cmdstat_config|get:calls=6,usec=23,usec_per_call=3.83,rejected_calls=0,failed_calls=0
redis-1  | cmdstat_ttl:calls=4,usec=19,usec_per_call=4.75,rejected_calls=0,failed_calls=0
redis-1  | cmdstat_hlen:calls=4,usec=26,usec_per_call=6.50,rejected_calls=0,failed_calls=0
redis-1  | cmdstat_dbsize:calls=2,usec=3,usec_per_call=1.50,rejected_calls=0,failed_calls=0
redis-1  | cmdstat_client|setname:calls=3,usec=17,usec_per_call=5.67,rejected_calls=0,failed_calls=0
redis-1  | cmdstat_client|setinfo:calls=4,usec=8,usec_per_call=2.00,rejected_calls=0,failed_calls=0
redis-1  | cmdstat_client|list:calls=1,usec=8,usec_per_call=8.00,rejected_calls=0,failed_calls=0
redis-1  | cmdstat_hscan:calls=2,usec=28,usec_per_call=14.00,rejected_calls=0,failed_calls=0
redis-1  | cmdstat_info:calls=22,usec=1293,usec_per_call=58.77,rejected_calls=0,failed_calls=0
redis-1  | cmdstat_FT.CREATE:calls=1,usec=397,usec_per_call=397.00,rejected_calls=0,failed_calls=0
redis-1  | cmdstat_memory|usage:calls=4,usec=22,usec_per_call=5.50,rejected_calls=0,failed_calls=0
redis-1  | cmdstat_module|list:calls=1,usec=8,usec_per_call=8.00,rejected_calls=0,failed_calls=0
redis-1  | cmdstat_hset:calls=1,usec=87,usec_per_call=87.00,rejected_calls=0,failed_calls=0
redis-1  | cmdstat_scan:calls=2,usec=30,usec_per_call=15.00,rejected_calls=0,failed_calls=0
redis-1  | 
redis-1  | # Errorstats
redis-1  | 
redis-1  | # Latencystats
redis-1  | latency_percentiles_usec_FT.DROPINDEX:p50=30.079,p99=30.079,p99.9=30.079
redis-1  | latency_percentiles_usec_del:p50=40.191,p99=81.407,p99.9=81.407
redis-1  | latency_percentiles_usec_FT._LIST:p50=16.063,p99=30.079,p99.9=30.079
redis-1  | latency_percentiles_usec_httl:p50=3.007,p99=9.023,p99.9=9.023
redis-1  | latency_percentiles_usec_type:p50=2.007,p99=4.015,p99.9=4.015
redis-1  | latency_percentiles_usec_config|get:p50=3.007,p99=8.031,p99.9=8.031
redis-1  | latency_percentiles_usec_ttl:p50=2.007,p99=14.015,p99.9=14.015
redis-1  | latency_percentiles_usec_hlen:p50=3.007,p99=17.023,p99.9=17.023
redis-1  | latency_percentiles_usec_dbsize:p50=1.003,p99=2.007,p99.9=2.007
redis-1  | latency_percentiles_usec_client|setname:p50=2.007,p99=14.015,p99.9=14.015
redis-1  | latency_percentiles_usec_client|setinfo:p50=1.003,p99=3.007,p99.9=3.007
redis-1  | latency_percentiles_usec_client|list:p50=8.031,p99=8.031,p99.9=8.031
redis-1  | latency_percentiles_usec_hscan:p50=6.015,p99=22.015,p99.9=22.015
redis-1  | latency_percentiles_usec_info:p50=54.015,p99=149.503,p99.9=149.503
redis-1  | latency_percentiles_usec_FT.CREATE:p50=397.311,p99=397.311,p99.9=397.311
redis-1  | latency_percentiles_usec_memory|usage:p50=4.015,p99=9.023,p99.9=9.023
redis-1  | latency_percentiles_usec_module|list:p50=8.031,p99=8.031,p99.9=8.031
redis-1  | latency_percentiles_usec_hset:p50=87.039,p99=87.039,p99.9=87.039
redis-1  | latency_percentiles_usec_scan:p50=9.023,p99=21.119,p99.9=21.119
redis-1  | 
redis-1  | # Cluster
redis-1  | cluster_enabled:0
redis-1  | 
redis-1  | # Keyspace
redis-1  | db0:keys=1,expires=0,avg_ttl=0,subexpiry=0
redis-1  | 
redis-1  | ------ CLIENT LIST OUTPUT ------
redis-1  | id=25 addr=127.0.0.1:57936 laddr=127.0.0.1:6379 fd=21 name=redisinsight-common-redis-stack---1-1- age=52 idle=2 flags=N db=0 sub=0 psub=0 ssub=0 multi=-1 watch=0 qbuf=0 qbuf-free=16386 argv-mem=0 multi-mem=0 rbs=1128 rbp=0 obl=0 oll=0 omem=0 tot-mem=18312 events=r cmd=info user=default redir=-1 resp=2 lib-name= lib-ver=
redis-1  | id=26 addr=127.0.0.1:57952 laddr=127.0.0.1:6379 fd=22 name=redisinsight-browser-redis-stack---1-1- age=51 idle=9 flags=N db=0 sub=0 psub=0 ssub=0 multi=-1 watch=0 qbuf=0 qbuf-free=0 argv-mem=0 multi-mem=0 rbs=1048 rbp=0 obl=0 oll=0 omem=0 tot-mem=1864 events=r cmd=FT._LIST user=default redir=-1 resp=2 lib-name= lib-ver=
redis-1  | id=27 addr=127.0.0.1:36756 laddr=127.0.0.1:6379 fd=23 name=redisinsight-workbench-redis-stack---1-1- age=38 idle=4 flags=N db=0 sub=0 psub=0 ssub=0 multi=-1 watch=0 qbuf=0 qbuf-free=0 argv-mem=0 multi-mem=0 rbs=1032 rbp=0 obl=0 oll=0 omem=0 tot-mem=1848 events=r cmd=FT._LIST user=default redir=-1 resp=2 lib-name= lib-ver=
redis-1  | id=29 addr=172.22.0.1:60606 laddr=172.22.0.2:6379 fd=24 name= age=0 idle=0 flags=N db=0 sub=0 psub=0 ssub=0 multi=-1 watch=0 qbuf=4299 qbuf-free=12087 argv-mem=4228 multi-mem=0 rbs=16408 rbp=4 obl=4 oll=0 omem=0 tot-mem=37900 events=r cmd=hset user=default redir=-1 resp=2 lib-name=redis-py lib-ver=5.3.1
redis-1  | 
redis-1  | ------ CURRENT CLIENT INFO ------
redis-1  | id=29 addr=172.22.0.1:60606 laddr=172.22.0.2:6379 fd=24 name= age=0 idle=0 flags=N db=0 sub=0 psub=0 ssub=0 multi=-1 watch=0 qbuf=4299 qbuf-free=12087 argv-mem=4228 multi-mem=0 rbs=16408 rbp=4 obl=4 oll=0 omem=0 tot-mem=37900 events=r cmd=hset user=default redir=-1 resp=2 lib-name=redis-py lib-ver=5.3.1
redis-1  | argc: '10'
redis-1  | argv[0]: '"HSET"'
redis-1  | argv[1]: '"owner:test-user:unique_id:docs:1"'
redis-1  | argv[2]: '"id"'
redis-1  | argv[3]: '"node_1"'
redis-1  | argv[4]: '"doc_id"'
redis-1  | argv[5]: '"document_1"'
redis-1  | argv[6]: '"text"'
redis-1  | argv[7]: '"Redis is an in-memory data structure store used as a database."'
redis-1  | argv[8]: '"vector"'
redis-1  | argv[9]: '"\xd8\xa5\x95;\x05\xb6\xc8>\xb8\xab\x7f?0\xef{?U\xaf\x17=\xcd\xcc\x8c>\x10\x99\x8b>w+\xad>\xff\xcaU>f:\x11?\x90\xeef>\xb04O?\xc2]\\?\xfb\nM>\xe1\xe6\x19>\xa3\x01\x93=\xc0Ua?w2\x8d>W\x8e\xa1>\xb0}\xd9>\xa5\x8c\r?\x12\xd5\n>\xba\xee(>Q\xcbO?\x02\xbe\xf9=\x13\xc5K>\xfd\xda~?!\x94w?\x8e\x0cE?d!+?F\xda\xb4>+\xf6\xcb<\x8f\x9c/?Y$\r?\xc6\x80g?\xb5\xf8v?\xa8\xfdI?\xc0T\x16?\x01\xafe?\xb6v\n>\x99'o>\xcb\xf81?\xfa6\xca>i\xe20?\xc9\xe7P?\x94f >\x94\xc8G>\xe8\x8a\xa5>\xb3$??\xa7N\xae>\x88n\xfd>\x82g\n?\xdeJa=\xb3\xce\x9e<\x83Vh?\x05\x1b&>\xf7\xad\xd7>\x984\x9d>\x88^\xc3>\x8d\xc1\xf8=\xe8^J?\x02\xd8Y?\xb9X7?\xcf\xeey?\xe8\x9c\xfa>\xccpV?\xd1\xa3a>`\xe6N?b\xc2B>\xdf\x0b\x9e=\x92\xa3P?\xb5\xc9K?\xac~\xf9>\xb3+<=\x96\x81\x11?}bO?\xa6\xa8\xbf>\x95T\xe9>\x1d\xd2\xa2=f\x04h?\xf8e&?`tE?\x84\xd0\x11?\t\x01\xd8=B\xf6R?\xe9\x1ey?\x1a\xc7j>d\xaa\x1e?\x1c\x86\xa0=0\x89$>i\xcd\xab>\xd5\x01\x0e?\xbc\xc3\xc5>\x8d\xa8G?P\x83Y>\xd3\x02\x01?\xa0/m?/\x10/?\x0c\xd7=?\xa9\xebZ>\xb1'3?\n\xdc%?I\x8a=?\xa0\xf0\x1f>\xa4\xeb!?\x18\x0b+?9:M 16 Mar 2026 16:55:56.501 # key 'owner:test-user:unique_id:docs:1' found in DB containing the following object:
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # Object type: 4
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # Object encoding: 2
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # Object refcount: 1
redis-1  | 
redis-1  | ------ EXECUTING CLIENT INFO ------
redis-1  | id=29 addr=172.22.0.1:60606 laddr=172.22.0.2:6379 fd=24 name= age=0 idle=0 flags=N db=0 sub=0 psub=0 ssub=0 multi=-1 watch=0 qbuf=4299 qbuf-free=12087 argv-mem=4228 multi-mem=0 rbs=16408 rbp=4 obl=4 oll=0 omem=0 tot-mem=37900 events=r cmd=hset user=default redir=-1 resp=2 lib-name=redis-py lib-ver=5.3.1
redis-1  | argc: '10'
redis-1  | argv[0]: '"HSET"'
redis-1  | argv[1]: '"owner:test-user:unique_id:docs:1"'
redis-1  | argv[2]: '"id"'
redis-1  | argv[3]: '"node_1"'
redis-1  | argv[4]: '"doc_id"'
redis-1  | argv[5]: '"document_1"'
redis-1  | argv[6]: '"text"'
redis-1  | argv[7]: '"Redis is an in-memory data structure store used as a database."'
redis-1  | argv[8]: '"vector"'
redis-1  | argv[9]: '"\xd8\xa5\x95;\x05\xb6\xc8>\xb8\xab\x7f?0\xef{?U\xaf\x17=\xcd\xcc\x8c>\x10\x99\x8b>w+\xad>\xff\xcaU>f:\x11?\x90\xeef>\xb04O?\xc2]\\?\xfb\nM>\xe1\xe6\x19>\xa3\x01\x93=\xc0Ua?w2\x8d>W\x8e\xa1>\xb0}\xd9>\xa5\x8c\r?\x12\xd5\n>\xba\xee(>Q\xcbO?\x02\xbe\xf9=\x13\xc5K>\xfd\xda~?!\x94w?\x8e\x0cE?d!+?F\xda\xb4>+\xf6\xcb<\x8f\x9c/?Y$\r?\xc6\x80g?\xb5\xf8v?\xa8\xfdI?\xc0T\x16?\x01\xafe?\xb6v\n>\x99'o>\xcb\xf81?\xfa6\xca>i\xe20?\xc9\xe7P?\x94f >\x94\xc8G>\xe8\x8a\xa5>\xb3$??\xa7N\xae>\x88n\xfd>\x82g\n?\xdeJa=\xb3\xce\x9e<\x83Vh?\x05\x1b&>\xf7\xad\xd7>\x984\x9d>\x88^\xc3>\x8d\xc1\xf8=\xe8^J?\x02\xd8Y?\xb9X7?\xcf\xeey?\xe8\x9c\xfa>\xccpV?\xd1\xa3a>`\xe6N?b\xc2B>\xdf\x0b\x9e=\x92\xa3P?\xb5\xc9K?\xac~\xf9>\xb3+<=\x96\x81\x11?}bO?\xa6\xa8\xbf>\x95T\xe9>\x1d\xd2\xa2=f\x04h?\xf8e&?`tE?\x84\xd0\x11?\t\x01\xd8=B\xf6R?\xe9\x1ey?\x1a\xc7j>d\xaa\x1e?\x1c\x86\xa0=0\x89$>i\xcd\xab>\xd5\x01\x0e?\xbc\xc3\xc5>\x8d\xa8G?P\x83Y>\xd3\x02\x01?\xa0/m?/\x10/?\x0c\xd7=?\xa9\xebZ>\xb1'3?\n\xdc%?I\x8a=?\xa0\xf0\x1f>\xa4\xeb!?\x18\x0b+?9:M 16 Mar 2026 16:55:56.501 # key 'owner:test-user:unique_id:docs:1' found in DB containing the following object:
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # Object type: 4
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # Object encoding: 2
redis-1  | 9:M 16 Mar 2026 16:55:56.501 # Object refcount: 1
redis-1  | 
redis-1  | ------ MODULES INFO OUTPUT ------
redis-1  | # search_version
redis-1  | search_version:2.10.20
redis-1  | search_redis_version:7.4.7 - oss
redis-1  | 
redis-1  | # search_index
redis-1  | search_number_of_indexes:2
redis-1  | search_number_of_active_indexes:1
redis-1  | search_number_of_active_indexes_running_queries:0
redis-1  | search_number_of_active_indexes_indexing:1
redis-1  | search_total_active_write_threads:1
redis-1  | 
redis-1  | # search_fields_statistics
redis-1  | search_fields_text:Text=2,IndexErrors=0
redis-1  | search_fields_tag:Tag=4,IndexErrors=0
redis-1  | search_fields_vector:Vector=2,HNSW=2,IndexErrors=0
redis-1  | 
redis-1  | # search_memory
redis-1  | search_used_memory_indexes:34217
redis-1  | search_used_memory_indexes_human:0.032631874084472656
redis-1  | search_smallest_memory_index:16064
redis-1  | search_smallest_memory_index_human:0.01531982421875
redis-1  | search_largest_memory_index:18153
redis-1  | search_largest_memory_index_human:0.017312049865722656
redis-1  | search_total_indexing_time:0
redis-1  | search_used_memory_vector_index:0
redis-1  | 
redis-1  | # search_cursors
redis-1  | search_global_idle:0
redis-1  | search_global_total:0
redis-1  | 
redis-1  | # search_gc
redis-1  | search_bytes_collected:0
redis-1  | search_total_cycles:0
redis-1  | search_total_ms_run:0
redis-1  | search_total_docs_not_collected_by_gc:0
redis-1  | search_marked_deleted_vectors:0
redis-1  | 
redis-1  | # search_queries
redis-1  | search_total_queries_processed:0
redis-1  | search_total_query_commands:0
redis-1  | search_total_query_execution_time_ms:0
redis-1  | search_total_active_queries:0
redis-1  | 
redis-1  | # search_warnings_and_errors
redis-1  | search_errors_indexing_failures:0
redis-1  | search_errors_for_index_with_max_failures:0
redis-1  | search_OOM_indexing_failures_indexes_count:0
redis-1  | 
redis-1  | # search_dialect_statistics
redis-1  | search_dialect_1:0
redis-1  | search_dialect_2:0
redis-1  | search_dialect_3:0
redis-1  | search_dialect_4:0
redis-1  | 
redis-1  | # search_runtime_configurations
redis-1  | search_enableGC:ON
redis-1  | search_minimal_term_prefix:2
redis-1  | search_minimal_stem_length:4
redis-1  | search_maximal_prefix_expansions:200
redis-1  | search_query_timeout_ms:500
redis-1  | search_timeout_policy:return
redis-1  | search_cursor_read_size:1000
redis-1  | search_cursor_max_idle_time:300000
redis-1  | search_max_doc_table_size:1000000
redis-1  | search_max_search_results:10000
redis-1  | search_max_aggregate_results:10000
redis-1  | search_gc_scan_size:100
redis-1  | search_min_phonetic_term_length:3
redis-1  | search_bm25std_tanh_factor:4
redis-1  | 
redis-1  | # redisgears_2_trace
redis-1  | redisgears_2_backtrace:   0: redis_module::basic_info_command_handler
redis-1  |    1: redisgears::gears_module::__info_func
redis-1  |    2: modulesCollectInfo
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/module.c:10410:9
redis-1  |    3: logModulesInfo
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/debug.c:2048:22
redis-1  |       printCrashReport
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/debug.c:2401:5
redis-1  |    4: sigsegvHandler
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/debug.c:2328:32
redis-1  |    5: <unknown>
redis-1  |    6: <unknown>
redis-1  |    7: _ZN9HNSWIndexIffEC2EPK10HNSWParamsRK23AbstractIndexInitParamsmm
redis-1  |    8: _ZN11HNSWFactory8NewIndexEPK12VecSimParams
redis-1  |    9: _ZN13TieredFactory17TieredHNSWFactory8NewIndexEPK17TieredIndexParams
redis-1  |   10: _ZN13VecSimFactory8NewIndexEPK12VecSimParams
redis-1  |   11: openVectorIndex
redis-1  |   12: IndexerBulkAdd
redis-1  |   13: Indexer_Add
redis-1  |   14: Document_AddToIndexes
redis-1  |   15: IndexSpec_UpdateDoc
redis-1  |   16: Indexes_UpdateMatchingWithSchemaRules
redis-1  |   17: HashNotificationCallback
redis-1  |   18: moduleNotifyKeyspaceEvent
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/module.c:8846:13
redis-1  |   19: moduleNotifyKeyspaceEvent
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/module.c:8802:8
redis-1  |       notifyKeyspaceEvent
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/notify.c:93:6
redis-1  |   20: hsetCommand
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/t_hash.c:2188:5
redis-1  |   21: call
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/server.c:3571:5
redis-1  |   22: processCommand
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/server.c:4198:9
redis-1  |   23: processCommandAndResetClient
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/networking.c:2505:9
redis-1  |       processInputBuffer
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/networking.c:2613:17
redis-1  |   24: readQueryFromClient
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/networking.c:2759:9
redis-1  |   25: callHandler
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/connhelpers.h:58:18
redis-1  |       connSocketEventHandler
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/socket.c:277:14
redis-1  |   26: aeProcessEvents
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/ae.c:417:17
redis-1  |       aeMain
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/ae.c:477:9
redis-1  |   27: main
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/server.c:7243:5
redis-1  |   28: <unknown>
redis-1  |   29: __libc_start_main
redis-1  |   30: _start
redis-1  | 
redis-1  | 
redis-1  | # redisgears_2_UninitialisedBackends
redis-1  | redisgears_2_backend_name:js
redis-1  | 
redis-1  | # ReJSON_trace
redis-1  | ReJSON_backtrace:   0: redis_module::add_trace_info
redis-1  |              at /github/home/.cargo/git/checkouts/redismodule-rs-05912e108a25d1e2/bce557d/src/lib.rs:71:29
redis-1  |       redis_module::basic_info_command_handler
redis-1  |              at /github/home/.cargo/git/checkouts/redismodule-rs-05912e108a25d1e2/bce557d/src/lib.rs:95:25
redis-1  |    1: rejson::__info_func
redis-1  |              at /github/home/.cargo/git/checkouts/redismodule-rs-05912e108a25d1e2/bce557d/src/macros.rs:183:13
redis-1  |    2: modulesCollectInfo
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/module.c:10410:9
redis-1  |    3: logModulesInfo
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/debug.c:2048:22
redis-1  |       printCrashReport
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/debug.c:2401:5
redis-1  |    4: sigsegvHandler
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/debug.c:2328:32
redis-1  |    5: <unknown>
redis-1  |    6: <unknown>
redis-1  |    7: _ZN9HNSWIndexIffEC1EPK10HNSWParamsRK23AbstractIndexInitParamsmm
redis-1  |    8: _ZN11HNSWFactory8NewIndexEPK12VecSimParams
redis-1  |    9: _ZN13TieredFactory17TieredHNSWFactory8NewIndexEPK17TieredIndexParams
redis-1  |   10: _ZN13VecSimFactory8NewIndexEPK12VecSimParams
redis-1  |   11: openVectorIndex
redis-1  |   12: IndexerBulkAdd
redis-1  |   13: Indexer_Add
redis-1  |   14: Document_AddToIndexes
redis-1  |   15: IndexSpec_UpdateDoc
redis-1  |   16: Indexes_UpdateMatchingWithSchemaRules
redis-1  |   17: HashNotificationCallback
redis-1  |   18: moduleNotifyKeyspaceEvent
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/module.c:8846:13
redis-1  |   19: moduleNotifyKeyspaceEvent
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/module.c:8802:8
redis-1  |       notifyKeyspaceEvent
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/notify.c:93:6
redis-1  |   20: hsetCommand
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/t_hash.c:2188:5
redis-1  |   21: call
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/server.c:3571:5
redis-1  |   22: processCommand
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/server.c:4198:9
redis-1  |   23: processCommandAndResetClient
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/networking.c:2505:9
redis-1  |       processInputBuffer
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/networking.c:2613:17
redis-1  |   24: readQueryFromClient
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/networking.c:2759:9
redis-1  |   25: callHandler
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/connhelpers.h:58:18
redis-1  |       connSocketEventHandler
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/socket.c:277:14
redis-1  |   26: aeProcessEvents
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/ae.c:417:17
redis-1  |       aeMain
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/ae.c:477:9
redis-1  |   27: main
redis-1  |              at /home/runner/work/redis-stack/redis-stack/redis/src/server.c:7243:5
redis-1  |   28: <unknown>
redis-1  |   29: __libc_start_main
redis-1  |   30: _start
redis-1  | 
redis-1  | 
redis-1  | ------ CONFIG DEBUG OUTPUT ------
redis-1  | proto-max-bulk-len 512mb
redis-1  | io-threads 1
redis-1  | slave-read-only yes
redis-1  | activedefrag no
redis-1  | repl-diskless-sync yes
redis-1  | lazyfree-lazy-user-del no
redis-1  | lazyfree-lazy-server-del no
redis-1  | io-threads-do-reads no
redis-1  | sanitize-dump-payload no
redis-1  | lazyfree-lazy-expire no
redis-1  | list-compress-depth 0
redis-1  | lazyfree-lazy-user-flush no
redis-1  | repl-diskless-load disabled
redis-1  | client-query-buffer-limit 1gb
redis-1  | replica-read-only yes
redis-1  | lazyfree-lazy-eviction no
redis-1  | 
redis-1  | ------ FAST MEMORY TEST ------
redis-1  | 9:M 16 Mar 2026 16:55:56.532 # Bio worker thread #0 terminated
redis-1  | 9:M 16 Mar 2026 16:55:56.532 # Bio worker thread #1 terminated
redis-1  | 9:M 16 Mar 2026 16:55:56.532 # Bio worker thread #2 terminated
redis-1  | *** Preparing to test memory region aaaae2cb5000 (135168 bytes)
redis-1  | *** Preparing to test memory region aaab0fe0b000 (31285248 bytes)
redis-1  | *** Preparing to test memory region ffff64000000 (135168 bytes)
redis-1  | *** Preparing to test memory region ffff6c000000 (135168 bytes)
redis-1  | *** Preparing to test memory region ffff70000000 (135168 bytes)
redis-1  | *** Preparing to test memory region ffff78000000 (135168 bytes)
redis-1  | *** Preparing to test memory region ffff7e210000 (8388608 bytes)
redis-1  | *** Preparing to test memory region ffff7ec10000 (8388608 bytes)
redis-1  | *** Preparing to test memory region ffff7f610000 (8388608 bytes)
redis-1  | *** Preparing to test memory region ffff80000000 (135168 bytes)
redis-1  | *** Preparing to test memory region ffff84a10000 (8388608 bytes)
redis-1  | *** Preparing to test memory region ffff85410000 (8388608 bytes)
redis-1  | *** Preparing to test memory region ffff85e10000 (8388608 bytes)
redis-1  | *** Preparing to test memory region ffff86810000 (8388608 bytes)
redis-1  | *** Preparing to test memory region ffff88c7d000 (147456 bytes)
redis-1  | *** Preparing to test memory region ffff88d3f000 (790528 bytes)
redis-1  | *** Preparing to test memory region ffff8913f000 (8192 bytes)
redis-1  | *** Preparing to test memory region ffff8957c000 (4096 bytes)
redis-1  | *** Preparing to test memory region ffff89829000 (12288 bytes)
redis-1  | *** Preparing to test memory region ffff8988e000 (1114112 bytes)
redis-1  | *** Preparing to test memory region ffff899cf000 (4096 bytes)
redis-1  | *** Preparing to test memory region ffff8a09d000 (20480 bytes)
redis-1  | *** Preparing to test memory region ffff8a0af000 (4096 bytes)
redis-1  | *** Preparing to test memory region ffff8a1c5000 (8192 bytes)
redis-1  | *** Preparing to test memory region ffff8a228000 (163840 bytes)
redis-1  | *** Preparing to test memory region ffff8a3f3000 (49152 bytes)
redis-1  | *** Preparing to test memory region ffff8a7f2000 (12288 bytes)
redis-1  | *** Preparing to test memory region ffff8a800000 (327680 bytes)
redis-1  | *** Preparing to test memory region ffff8a9d4000 (8192 bytes)
redis-1  | *** Preparing to test memory region ffff8a9d8000 (8192 bytes)
redis-1  | .O.O.O.O.O.O.O.O.O.O.O.O.O.O.O.O.O.O.O.O.O.O.O.O.O.O.O.O.O.O
redis-1  | Fast memory test PASSED, however your memory can still be broken. Please run a memory test for several hours if possible.
redis-1  | 
redis-1  | ------ DUMPING CODE AROUND EIP ------
redis-1  | Symbol: _ZN6spaces34Choose_FP32_IP_implementation_SVE2Em (base: 0xffff89d5a9d0)
redis-1  | Module: /opt/redis-stack/lib/redisearch.so (base 0xffff89a00000)
redis-1  | $ xxd -r -p /tmp/dump.hex /tmp/dump.bin
redis-1  | $ objdump --adjust-vma=0xffff89d5a9d0 -D -b binary -m i386:x86-64 /tmp/dump.bin
redis-1  | ------
redis-1  | 9:M 16 Mar 2026 16:55:56.870 # dump of function (hexdump of 128 bytes):
redis-1  | e3e3a0040108c39a220400122180039b5f080071800100545f0c0071000300545f040071e00100543f0000f1e019009000c446f9e11900b021a843f90000819ac0035fd63f0000f1c01900f0001047f9e11900b0211046f90000819ac0035fd63f0000f1e01900b0001443f9e11900b021b843f90000819ac0035fd63f0000f1
redis-1  | 
redis-1  | === REDIS BUG REPORT END. Make sure to include from START to END. ===
redis-1  | 
redis-1  |        Please report the crash by opening an issue on github:
redis-1  | 
redis-1  |            http://github.com/redis/redis/issues
redis-1  | 
redis-1  |   If a Redis module was involved, please open in the module's repo instead.
redis-1  | 
redis-1  |   Suspect RAM error? Use redis-server --test-memory to verify it.
redis-1  | 
redis-1  |   Some other issues could be detected by redis-server --check-system
redis-1  | Illegal instruction
redis-1 exited with code 132
```



## Curated Answers



### High Signal Answer 1

similar issues: https://github.com/redis/redis/issues/14617 https://github.com/redis/redis/issues/14248
@oleslav thx, can you create an issue in https://github.com/RediSearch/RediSearch/issues?

- Author: sundb
- Quality score: 4
- URL: https://github.com/redis/redis/issues/14894#issuecomment-4072783608
