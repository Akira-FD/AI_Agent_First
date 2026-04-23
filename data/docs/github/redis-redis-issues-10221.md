# [CRASH] c->cmd nullified within `cmd->proc` call.



## GitHub Provenance



- Repository: redis/redis

- Issue: #10221

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/10221



## Problem



**Crash report**
There was a crash in the cluster tests in GH actions.
https://github.com/redis/redis/runs/5001700579?check_suite_focus=true#step:10:630

it looks like the crash is due to a NULL `cmd` member in the client struct here:
```
    if (!(c->cmd->flags & (CMD_SKIP_MONITOR|CMD_ADMIN))) {
```

in the prints below we see `Cluster nodes are reachable` completes successfully, so it must be one of the commands in `Cluster nodes hard reset` that called `freeClientArgv` (or maybe even `freeClient`) from within `call()`,

Note that it might be that the crash exists for a long time, but only now being reported due to the change in #10207

```
Testing unit: 06-slave-stop-cond.tcl
05:44:02> (init) Restart killed instances: redis/0 redis/3 redis/6 redis/12 redis/15 OK
05:44:02> Cluster nodes are reachable: OK
05:44:02> Cluster nodes hard reset: FAILED: caught an error in the test I/O error reading reply
I/O error reading reply
    while executing
"foreach_redis_id id {
        if {$::valgrind} {
            set node_timeout 10000
        } else {
            set node_timeout 3000
        }
     ..."
    ("uplevel" body line 2)
    invoked from within
"uplevel 1 $code"
    (procedure "test" line 6)
    invoked from within
"test "Cluster nodes hard reset" {
    foreach_redis_id id {
        if {$::valgrind} {
            set node_timeout 10000
        } else {
           ..."
    (file "../tests/includes/init-tests.tcl" line 28)
    invoked from within
"source "../tests/includes/init-tests.tcl""
```

```
=== REDIS BUG REPORT START: Cut & paste starting from here ===
6077:M 31 Jan 2022 05:44:02.861 # Redis 255.255.255 crashed by signal: 11, si_code: 1
6077:M 31 Jan 2022 05:44:02.861 # Accessing address: 0x60
6077:M 31 Jan 2022 05:44:02.861 # Crashed running the instruction at: 0x44a490

------ STACK TRACE ------
EIP:
../../../src/redis-server *:30009 [cluster](call+0x170)[0x44a490]

Backtrace:
/lib64/libpthread.so.0(+0xf630)[0x7fc378620630]
../../../src/redis-server *:30009 [cluster](call+0x170)[0x44a490]
../../../src/redis-server *:30009 [cluster](processCommand+0x990)[0x44c470]
../../../src/redis-server *:30009 [cluster](processCommandAndResetClient+0x1c)[0x46177c]
../../../src/redis-server *:30009 [cluster](processInputBuffer+0xd1)[0x464111]
../../../src/redis-server *:30009 [cluster](readQueryFromClient+0x238)[0x467028]
../../../src/redis-server *:30009 [cluster][0x4f93f3]
../../../src/redis-server *:30009 [cluster](aeProcessEvents+0x235)[0x442ed5]
../../../src/redis-server *:30009 [cluster](aeMain+0x1d)[0x44321d]
../../../src/redis-server *:30009 [cluster](main+0x406)[0x43f5b6]
/lib64/libc.so.6(__libc_start_main+0xf5)[0x7fc378265555]
../../../src/redis-server *:30009 [cluster][0x43f96a]

------ REGISTERS ------
6077:M 31 Jan 2022 05:44:02.862 # 
RAX:0000000000000000 RBX:00007fc37794a1c0
RCX:000000000000007d RDX:0000000000000000
RDI:00007fc377e1c530 RSI:0000000000000000
RBP:000000000000000f RSP:00007ffd129f59f0
R8 :000000000002823c R9 :000000000000007d
R10:0000000000000002 R11:00007ffd129fa000
R12:0000000000000001 R13:0000000000000000
R14:000000000000c360 R15:00000000008203e0
RIP:000000000044a490 EFL:0000000000010206
CSGSFS:002b000000000033
6077:M 31 Jan 2022 05:44:02.862 # (00007ffd129f59ff) -> 00007fc37794a1c0
6077:M 31 Jan 2022 05:44:02.862 # (00007ffd129f59fe) -> 000000000000001b
6077:M 31 Jan 2022 05:44:02.862 # (00007ffd129f59fd) -> 00007fc377950de0
6077:M 31 Jan 2022 05:44:02.862 # (00007ffd129f59fc) -> 00007fc377e507c8
6077:M 31 Jan 2022 05:44:02.862 # (00007ffd129f59fb) -> 00007fc300000000
6077:M 31 Jan 2022 05:44:02.862 # (00007ffd129f59fa) -> 0000000000000000
6077:M 31 Jan 2022 05:44:02.862 # (00007ffd129f59f9) -> 000000000044c470
6077:M 31 Jan 2022 05:44:02.862 # (00007ffd129f59f8) -> 0000000000000000
6077:M 31 Jan 2022 05:44:02.862 # (00007ffd129f59f7) -> 0000000000000000
6077:M 31 Jan 2022 05:44:02.862 # (00007ffd129f59f6) -> 0000000000000000
6077:M 31 Jan 2022 05:44:02.862 # (00007ffd129f59f5) -> 0000000000000000
6077:M 31 Jan 2022 05:44:02.862 # (00007ffd129f59f4) -> 0000000000000000
6077:M 31 Jan 2022 05:44:02.862 # (00007ffd129f59f3) -> 00007fc37794a1c0
6077:M 31 Jan 2022 05:44:02.862 # (00007ffd129f59f2) -> 0000000000000000
6077:M 31 Jan 2022 05:44:02.862 # (00007ffd129f59f1) -> 000000000000007d
6077:M 31 Jan 2022 05:44:02.862 # (00007ffd129f59f0) -> 000000000000c360

------ INFO OUTPUT ------
# Server
redis_version:255.255.255
redis_git_sha1:00000000
redis_git_dirty:0
redis_build_id:4233af117fee7f3d
redis_mode:cluster
os:Linux 5.11.0-1027-azure x86_64
arch_bits:64
multiplexing_api:epoll
atomicvar_api:atomic-builtin
gcc_version:4.8.5
process_id:6077
process_supervised:no
run_id:c8b4aa2843acf6ded37aa05c165a239d8b15166a
tcp_port:30009
server_time_usec:1643607842861736
uptime_in_seconds:66
uptime_in_days:0
hz:10
configured_hz:10
lru_clock:16217890
executable:/__w/redis/redis/src/redis-server
config_file:/__w/redis/redis/tests/cluster/tmp/redis_9/redis.conf
io_threads_active:0

# Clients
connected_clients:3
cluster_connections:38
maxclients:10000
client_recent_max_input_buffer:20480
client_recent_max_output_buffer:0
blocked_clients:0
tracking_clients:0
clients_in_timeout_table:0

# Memory
used_memory:2246088
used_memory_human:2.14M
used_memory_rss:12701696
used_memory_rss_human:12.11M
used_memory_peak:3836632
used_memory_peak_human:3.66M
used_memory_peak_perc:58.54%
used_memory_overhead:1729724
used_memory_startup:1605336
used_memory_dataset:516364
used_memory_dataset_perc:80.59%
allocator_allocated:2751032
allocator_active:3465216
allocator_resident:6545408
total_system_memory:7289606144
total_system_memory_human:6.79G
used_memory_lua:37888
used_memory_vm_eval:37888
used_memory_lua_human:37.00K
used_memory_scripts_eval:0
number_of_cached_scripts:0
number_of_functions:0
number_of_libraries:0
used_memory_vm_functions:37888
used_memory_vm_total:75776
used_memory_vm_total_human:74.00K
used_memory_functions:184
used_memory_scripts:184
used_memory_scripts_human:184B
maxmemory:0
maxmemory_human:0B
maxmemory_policy:noeviction
allocator_frag_ratio:1.26
allocator_frag_bytes:714184
allocator_rss_ratio:1.89
allocator_rss_bytes:3080192
rss_overhead_ratio:1.94
rss_overhead_bytes:6156288
mem_fragmentation_ratio:5.49
mem_fragmentation_bytes:10387352
mem_not_counted_for_evict:0
mem_replication_backlog:20508
mem_total_replication_buffers:20504
mem_clients_slaves:0
mem_clients_normal:81936
mem_cluster_links:21760
mem_aof_buffer:0
mem_allocator:jemalloc-5.2.1
active_defrag_running:0
lazyfree_pending_objects:0
lazyfreed_objects:0

# Persistence
loading:0
async_loading:0
current_cow_peak:0
current_cow_size:0
current_cow_size_age:0
current_fork_perc:0.00
current_save_keys_processed:0
current_save_keys_total:0
rdb_changes_since_last_save:50016
rdb_bgsave_in_progress:0
rdb_last_save_time:1643607842
rdb_last_bgsave_status:ok
rdb_last_bgsave_time_sec:0
rdb_current_bgsave_time_sec:-1
rdb_last_cow_size:503808
rdb_last_load_keys_expired:0
rdb_last_load_keys_loaded:0
aof_enabled:0
aof_rewrite_in_progress:0
aof_rewrite_scheduled:0
aof_last_rewrite_time_sec:0
aof_current_rewrite_time_sec:-1
aof_last_bgrewrite_status:ok
aof_last_write_status:ok
aof_last_cow_size:872448
module_fork_in_progress:0
module_fork_last_cow_size:0

# Stats
total_connections_received:9
total_commands_processed:710
instantaneous_ops_per_sec:32
total_net_input_bytes:398579
total_net_output_bytes:2889291
instantaneous_input_kbps:0.93
instantaneous_output_kbps:83.38
rejected_connections:0
sync_full:5
sync_partial_ok:0
sync_partial_err:5
expired_keys:0
expired_stale_perc:0.00
expired_time_cap_reached_count:0
expire_cycle_cpu_milliseconds:0
evicted_keys:0
evicted_clients:0
total_eviction_exceeded_time:0
current_eviction_exceeded_time:0
keyspace_hits:0
keyspace_misses:0
pubsub_channels:0
pubsub_patterns:0
latest_fork_usec:359
total_forks:4
migrate_cached_sockets:0
slave_expires_tracked_keys:0
active_defrag_hits:0
active_defrag_misses:0
active_defrag_key_hits:0
active_defrag_key_misses:0
total_active_defrag_time:0
current_active_defrag_time:0
tracking_total_keys:0
tracking_total_items:0
tracking_total_prefixes:0
unexpected_error_replies:0
total_error_replies:4
dump_payload_sanitizations:0
total_reads_processed:721
total_writes_processed:685
io_threaded_reads_processed:0
io_threaded_writes_processed:0

# Replication
role:master
connected_slaves:1
slave0:ip=127.0.0.1,port=30012,state=online,offset=1232,lag=0
master_failover_state:no-failover
master_replid:2a3a26533a4563723f1c93778b6506c069c23f7d
master_replid2:6bc4c527c36524c7c5918b0fcd6fe689488721b8
master_repl_offset:1273
second_repl_offset:1233
repl_backlog_active:1
repl_backlog_size:1048576
repl_backlog_first_byte_offset:1071
repl_backlog_histlen:203

# CPU
used_cpu_sys:0.184028
used_cpu_user:0.360055
used_cpu_sys_children:0.002642
used_cpu_user_children:0.009071
used_cpu_sys_main_thread:0.180311
used_cpu_user_main_thread:0.360623

# Modules

# Commandstats
cmdstat_set:calls=48,usec=77,usec_per_call=1.60,rejected_calls=0,failed_calls=0
cmdstat_multi:calls=2,usec=0,usec_per_call=0.00,rejected_calls=0,failed_calls=0
cmdstat_debug:calls=3,usec=69261,usec_per_call=23087.00,rejected_calls=0,failed_calls=0
cmdstat_cluster|set-config-epoch:calls=2,usec=45,usec_per_call=22.50,rejected_calls=0,failed_calls=0
cmdstat_cluster|reset:calls=2,usec=6464,usec_per_call=3232.00,rejected_calls=0,failed_calls=0
cmdstat_cluster|replicate:calls=2,usec=444,usec_per_call=222.00,rejected_calls=0,failed_calls=0
cmdstat_cluster|info:calls=13,usec=711,usec_per_call=54.69,rejected_calls=0,failed_calls=0
cmdstat_cluster|meet:calls=2,usec=24,usec_per_call=12.00,rejected_calls=0,failed_calls=0
cmdstat_cluster|nodes:calls=17,usec=2144,usec_per_call=126.12,rejected_calls=0,failed_calls=0
cmdstat_psync:calls=5,usec=1218,usec_per_call=243.60,rejected_calls=0,failed_calls=0
cmdstat_exec:calls=2,usec=6537,usec_per_call=3268.50,rejected_calls=0,failed_calls=0
cmdstat_config|set:calls=13,usec=50,usec_per_call=3.85,rejected_calls=0,failed_calls=0
cmdstat_config|rewrite:calls=2,usec=2409,usec_per_call=1204.50,rejected_calls=0,failed_calls=0
cmdstat_info:calls=545,usec=37221,usec_per_call=68.30,rejected_calls=0,failed_calls=0
cmdstat_replconf:calls=18,usec=41,usec_per_call=2.28,rejected_calls=0,failed_calls=0
cmdstat_flushall:calls=3,usec=11753,usec_per_call=3917.67,rejected_calls=2,failed_calls=0
cmdstat_select:calls=2,usec=1,usec_per_call=0.50,rejected_calls=0,failed_calls=0
cmdstat_role:calls=17,usec=26,usec_per_call=1.53,rejected_calls=0,failed_calls=0
cmdstat_ping:calls=12,usec=12,usec_per_call=1.00,rejected_calls=2,failed_calls=0

# Errorstats
errorstat_LOADING:count=2
errorstat_READONLY:count=2

# Latencystats
latency_percentiles_usec_set:p50=1.003,p99=10.047,p99.9=10.047
latency_percentiles_usec_multi:p50=0.001,p99=0.001,p99.9=0.001
latency_percentiles_usec_debug:p50=1.003,p99=69730.303,p99.9=69730.303
latency_percentiles_usec_cluster|set-config-epoch:p50=22.015,p99=23.039,p99.9=23.039
latency_percentiles_usec_cluster|reset:p50=3194.879,p99=3293.183,p99.9=3293.183
latency_percentiles_usec_cluster|replicate:p50=196.607,p99=248.831,p99.9=248.831
latency_percentiles_usec_cluster|info:p50=56.063,p99=79.359,p99.9=79.359
latency_percentiles_usec_cluster|meet:p50=10.047,p99=14.015,p99.9=14.015
latency_percentiles_usec_cluster|nodes:p50=95.231,p99=282.623,p99.9=282.623
latency_percentiles_usec_psync:p50=150.527,p99=569.343,p99.9=569.343
latency_percentiles_usec_exec:p50=3244.031,p99=3309.567,p99.9=3309.567
latency_percentiles_usec_config|set:p50=3.007,p99=10.047,p99.9=10.047
latency_percentiles_usec_config|rewrite:p50=1130.495,p99=1286.143,p99.9=1286.143
latency_percentiles_usec_info:p50=66.047,p99=105.471,p99.9=178.175
latency_percentiles_usec_replconf:p50=2.007,p99=8.031,p99.9=8.031
latency_percentiles_usec_flushall:p50=1409.023,p99=9175.039,p99.9=9175.039
latency_percentiles_usec_select:p50=0.001,p99=1.003,p99.9=1.003
latency_percentiles_usec_role:p50=1.003,p99=4.015,p99.9=4.015
latency_percentiles_usec_ping:p50=1.003,p99=5.023,p99.9=5.023

# Cluster
cluster_enabled:1

# Keyspace

------ CLIENT LIST OUTPUT ------
id=12 addr=127.0.0.1:58648 laddr=127.0.0.1:30009 fd=52 name= age=51 idle=51 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=0 qbuf-free=4 argv-mem=0 multi-mem=0 obl=0 oll=0 omem=0 tot-mem=20488 events=r cmd=NULL user=default redir=-1 resp=2
id=18 addr=127.0.0.1:37012 laddr=127.0.0.1:30009 fd=51 name= age=0 idle=0 flags=S db=0 sub=0 psub=0 multi=-1 qbuf=0 qbuf-free=20474 argv-mem=0 multi-mem=0 obl=0 oll=1 omem=20504 tot-mem=61464 events=r cmd=replconf user=default redir=-1 resp=2
id=6 addr=127.0.0.1:56588 laddr=127.0.0.1:30009 fd=12 name= age=66 idle=0 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=0 qbuf-free=20474 argv-mem=0 multi-mem=0 obl=0 oll=0 omem=0 tot-mem=40960 events=r cmd=flushall user=default redir=-1 resp=2
id=9 addr=127.0.0.1:57610 laddr=127.0.0.1:30009 fd=48 name= age=63 idle=63 flags=N db=0 sub=0 psub=0 multi=-1 qbuf=0 qbuf-free=4 argv-mem=0 multi-mem=0 obl=0 oll=0 omem=0 tot-mem=20488 events=r cmd=NULL user=default redir=-1 resp=2

------ MODULES INFO OUTPUT ------

------ CONFIG DEBUG OUTPUT ------
io-threads-do-reads no
lazyfree-lazy-eviction no
lazyfree-lazy-expire no
lazyfree-lazy-server-del no
lazyfree-lazy-user-del no
lazyfree-lazy-user-flush no
repl-diskless-sync yes
replica-read-only yes
activedefrag no
repl-diskless-load disabled
sanitize-dump-payload no
io-threads 1
list-compress-depth 0
proto-max-bulk-len 512mb
client-query-buffer-limit 1gb

------ FAST MEMORY TEST ------
6077:M 31 Jan 2022 05:44:02.864 # Bio thread for job type #0 terminated
6077:M 31 Jan 2022 05:44:02.865 # Bio thread for job type #1 terminated
6077:M 31 Jan 2022 05:44:02.865 # Bio thread for job type #2 terminated
*** Preparing to test memory region 85a000 (2293760 bytes)
*** Preparing to test memory region 1556000 (135168 bytes)
*** Preparing to test memory region 7fc36c000000 (135168 bytes)
*** Preparing to test memory region 7fc371c00000 (16777216 bytes)
*** Preparing to test memory region 7fc372c00000 (2097152 bytes)
*** Preparing to test memory region 7fc372f7c000 (4194304 bytes)
*** Preparing to test memory region 7fc37337d000 (16777216 bytes)
*** Preparing to test memory region 7fc37437e000 (16777216 bytes)
*** Preparing to test memory region 7fc37537f000 (16777216 bytes)
*** Preparing to test memory region 7fc377380000 (15204352 bytes)
*** Preparing to test memory region 7fc37860c000 (20480 bytes)
*** Preparing to test memory region 7fc378829000 (16384 bytes)
*** Preparing to test memory region 7fc379152000 (20480 bytes)
*** Preparing to test memory region 7fc37915a000 (8192 bytes)
*** Preparing to test memory region 7fc37915e000 (4096 bytes)
.O.O.O.O.O.O.O.O.O.O.O.O.O.O.O
Fast memory test PASSED, however your memory can still be broken. Please run a memory test for several hours if possible.

------ DUMPING CODE AROUND EIP ------
Symbol: call (base: 0x44a320)
Module: ../../../src/redis-server *:30009 [cluster] (base 0x400000)
$ xxd -r -p /tmp/dump.hex /tmp/dump.bin
$ objdump --adjust-vma=0x44a320 -D -b binary -m i386:x86-64 /tmp/dump.bin
------
6077:M 31 Jan 2022 05:44:03.175 # dump of function (hexdump of 496 bytes):
41574156415541545589f5534889fb4883ec184c8ba7d0000000448b2da7a042004c8b7f704c89e04825ff3fe7ff4585ed488987d0000000750a40f6c6100f84b4030000488b05adaa420048890424488b0512a742004889050bf44000488b05a4a34200488d50014885c048891596a342000f84b8030000830591a3420001ff15fb4a41004989c6488b43704889dfff5050ff15e84a41004989c1488b05c6a64200482b05bff340004d29f14c8b3545aa42004c898bb8000000832d4fa34200014885c07e084983878001000001488b83d000000048ba00000000000100004885d0741848bafffffffffffeffff4821d04883c840488983d00000008b1582a4420085d20f8456020000f6c4010f85cd02000040f6c501745341f6476140488b0d73ae4200bf6a4a5800b8184b5800480f44f84885c974274c89c848bacff753e3a59bc42048f7ea4c89c848c1f83f48c1fa074829c24839d10f8e11030000f683d0000000100f84d4020000488b437048f74060100800007531488b4b604885c90f84d9020000448b435c488b4318488b352aa142004889df4c894c24088b5028e84a7a02004c8b4c2408488b83d0000000a8100f845602000040f6c502741d8b0d56a842004d018f68010000498387700100000185c90f85d301000040f6c50c0f84a90000004889c281e200001800

=== REDIS BUG REPORT END. Make sure to include from START to END. ===

```

**Additional information**

happened in GH actions cluster tests on CentOS 7 with jemalloc



## Curated Answers



### High Signal Answer 1

Looking at the above crashes, the current_client seems to be NULL in both cases (the `CURRENT CLIENT INFO` section is missing).

I see that in the above crash logs (redis 9 and redis 3), in one case the master has just 1 slave, and in the other there are 3.
when i run these tests locally, and print the number of slaves each master has at that point in time, i get 5 for all 3 masters.
so i think it's safe to conclude that the released client is a slave, which means the command must have been a REPLCONF ACK.

updateSlavesWaitingBgsave has a couple of calls to freeClient (freeing the slave), and it is called from the done handler that's called from checkChildrenDone, which is used in replconfCommand, so could be called from REPLCONF ACK and then crash on its way out.

- Author: oranagra
- Quality score: 4
- URL: https://github.com/redis/redis/issues/10221#issuecomment-1031461249
