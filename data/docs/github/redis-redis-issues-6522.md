# Redis 4.0.7 crash frequently on arm environment



## GitHub Provenance



- Repository: redis/redis

- Issue: #6522

- State: closed

- Labels: state:to-be-closed

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/6522



## Problem



Hi, I use redis 4.0.7 deployed as pod under kubernetes environment, the host machine on the environment is aarch64(arm) not x86_64,
the redis pod will crash after serverl minitutes each time.
 
System Information is as below:
```
[root@node-1 ~]# uname -a  
Linux node-1.domain.tld 4.14.0-115.8.2.el7a.es.6.aarch64 #1 SMP Fri Oct 25 01:30:55 EDT 2019 aarch64 aarch64 aarch64 GNU/Linux

[root@node-1 ~]# cat /proc/version
Linux version 4.14.0-115.8.2.el7a.es.6.aarch64 (ken@huawei-189) (gcc version 4.8.5 20150623 (Red Hat 4.8.5-39) (GCC)) #1 SMP Fri Oct 25 01:30:55 EDT 2019

[root@node-1 ~]# cat /etc/redhat-release
CentOS Linux release 7.6.1810 (AltArch) 
```
The log of redis pod is as below:
```
kubectl logs redis-57b4b95856-rhnlq -n openstack
1:C 25 Oct 17:33:24.657 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
1:C 25 Oct 17:33:24.681 # Redis version=4.0.7, bits=64, commit=00000000, modified=0, pid=1, just started
1:C 25 Oct 17:33:24.681 # Configuration loaded
1:M 25 Oct 17:33:24.685 * Running mode=standalone, port=6379.
1:M 25 Oct 17:33:24.685 # WARNING: The TCP backlog setting of 511 cannot be enforced because /proc/sys/net/core/somaxconn is set to the lower value of 128.
1:M 25 Oct 17:33:24.685 # Server initialized
1:M 25 Oct 17:33:24.686 # WARNING you have Transparent Huge Pages (THP) support enabled in your kernel. This will create latency and memory usage issues with Redis. To fix this issue run the command 'echo never > /sys/kernel/mm/transparent_hugepage/enabled' as root, and add it to your /etc/rc.local in order to retain the setting after a reboot. Redis must be restarted after THP is disabled.
1:M 25 Oct 17:33:24.686 * Ready to accept connections


=== REDIS BUG REPORT START: Cut & paste starting from here ===
1:M 25 Oct 17:34:38.290 # Redis 4.0.7 crashed by signal: 11
1:M 25 Oct 17:34:38.294 # Accessing address: 0xffffffffffffffff
1:M 25 Oct 17:34:38.294 # Failed assertion: <no assertion failed> (<no file>:0)

------ STACK TRACE ------
redis-server *:6379(logStackTrace+0x2c)[0x4688f8]

------ INFO OUTPUT ------

It is strange that each crash information has the same content as below:
1:M 25 Oct 17:34:38.290 # Redis 4.0.7 crashed by signal: 11
1:M 25 Oct 17:34:38.294 # Accessing address: 0xffffffffffffffff
1:M 25 Oct 17:34:38.294 # Failed assertion: <no assertion failed> (<no file>:0)

------ STACK TRACE ------
redis-server *:6379(logStackTrace+0x2c)[0x4688f8]
```

But I searched the article:
https://redis.io/topics/ARM
The content in the article shows that Redis 4 versions supports the ARM processor,
the version of my redis is 4.0.7. 

I have collected some information nearly crash but before crashed time as below:
127.0.0.1:6379> KEYS *
1) "incoming:b50bd56d-ad74-420d-abbf-22797a9ad2e1"
2) "incoming:1a874789-8d3c-4e2c-94ee-3720168b4f2d"
3) "incoming:60c29b94-ef7c-4515-a71b-a018f7ce0179"
4) "incoming:616d9dad-10a8-4e1b-af91-2e11d575f637"
127.0.0.1:6379> INFO
# Server
redis_version:4.0.7
redis_git_sha1:00000000
redis_git_dirty:0
redis_build_id:2175d76041ffae3
redis_mode:standalone
os:Linux 4.14.0-115.8.2.el7a.es.6.aarch64 aarch64
arch_bits:64
multiplexing_api:epoll
atomicvar_api:atomic-builtin
gcc_version:4.9.2
process_id:16
run_id:77290e48e887e34578349dd00d86fcbb1bda1211
tcp_port:6379
uptime_in_seconds:590
uptime_in_days:0
hz:10
lru_clock:12144401
executable:/data/redis-server
config_file:

# Clients
connected_clients:138
client_longest_output_list:0
client_biggest_input_buf:0
blocked_clients:0

# Memory
used_memory:3721032
used_memory_human:3.55M
used_memory_rss:9371648
used_memory_rss_human:8.94M
used_memory_peak:4195800
used_memory_peak_human:4.00M
used_memory_peak_perc:88.68%
used_memory_overhead:3157512
used_memory_startup:798336
used_memory_dataset:563520
used_memory_dataset_perc:19.28%
total_system_memory:134972637184
total_system_memory_human:125.70G
used_memory_lua:37888
used_memory_lua_human:37.00K
maxmemory:0
maxmemory_human:0B
maxmemory_policy:noeviction
mem_fragmentation_ratio:2.52
mem_allocator:jemalloc-4.0.3
active_defrag_running:0
lazyfree_pending_objects:0

# Persistence
loading:0
rdb_changes_since_last_save:356
rdb_bgsave_in_progress:0
rdb_last_save_time:1572424899
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

# Stats
total_connections_received:197
total_commands_processed:886
instantaneous_ops_per_sec:0
total_net_input_bytes:68431
total_net_output_bytes:37943
instantaneous_input_kbps:0.00
instantaneous_output_kbps:0.00
rejected_connections:0
sync_full:0
sync_partial_ok:0
sync_partial_err:0
expired_keys:0
evicted_keys:0
keyspace_hits:435
keyspace_misses:8
pubsub_channels:0
pubsub_patterns:0
latest_fork_usec:0
migrate_cached_sockets:0
slave_expires_tracked_keys:0
active_defrag_hits:0
active_defrag_misses:0
active_defrag_key_hits:0
active_defrag_key_misses:0

# Replication
role:master
connected_slaves:0
master_replid:86a6972b565a3211ce617f54042a6b7db9eed5d3
master_replid2:0000000000000000000000000000000000000000
master_repl_offset:0
second_repl_offset:-1
repl_backlog_active:0
repl_backlog_size:1048576
repl_backlog_first_byte_offset:0
repl_backlog_histlen:0

# CPU
used_cpu_sys:0.54
used_cpu_user:0.24
used_cpu_sys_children:0.00
used_cpu_user_children:0.00

# Cluster
cluster_enabled:0

# Keyspace

127.0.0.1:6379> INFO memory
# Memory
used_memory:3761072
used_memory_human:3.59M
used_memory_rss:9371648
used_memory_rss_human:8.94M
used_memory_peak:4195800
used_memory_peak_human:4.00M
used_memory_peak_perc:89.64%
used_memory_overhead:3190284
used_memory_startup:798336
used_memory_dataset:570788
used_memory_dataset_perc:19.27%
total_system_memory:134972637184
total_system_memory_human:125.70G
used_memory_lua:37888
used_memory_lua_human:37.00K
maxmemory:0
maxmemory_human:0B
maxmemory_policy:noeviction
mem_fragmentation_ratio:2.49
mem_allocator:jemalloc-4.0.3
active_defrag_running:0
lazyfree_pending_objects:0
127.0.0.1:6379> KEYS *
Could not connect to Redis at 127.0.0.1:6379: Connection refused

I also get some information about unlimi:
[root@node-1 ~]# ulimit -n
102400
[root@node-1 ~]# ulimit -Hn
112640
[root@node-1 ~]# ulimit -Sn
102400

The maxclients of redis is 10000 as default.
Some memory correction information is as below:
[root@node-1 ~]# dmidecode -t memory | grep 'Error Correction'
	Error Correction Type: Unknown

Could you have some solution to solve the problem?
Thanks.



## Curated Answers



### High Signal Answer 1

I've seen quite a few reports of crashes on arm with older redis (mostly on 3.2), and none in recent version (5, 6, 6.2, which i assume get tested more on arm in recent years).
it could possibly be related to #3892 (merged as part of redis 5.0), so i wanna assume this issue is already resolved.

- Author: oranagra
- Quality score: 4
- URL: https://github.com/redis/redis/issues/6522#issuecomment-882458703
