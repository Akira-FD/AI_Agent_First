# Redis is crashing every days using version 2.4.8



## GitHub Provenance



- Repository: redis/redis

- Issue: #3870

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/3870



## Problem



Redis is crashing every day on 7 nodes out of 40 nodes  which has Redis locally on each node.

[25579] 12 Mar 03:33:23 # === REDIS BUG REPORT START: Cut & paste starting from here ===
[25579] 12 Mar 03:33:23 #     Redis 2.4.8 crashed by signal: 11
[25579] 12 Mar 03:33:23 #     Failed assertion: <no assertion failed> (<no file>:0)
[25579] 12 Mar 03:33:23 # --- STACK TRACE
[25579] 12 Mar 03:33:23 # /opt/CSCOcpm/redis/redis-server(lzf_compress+0x276) [0x7eff5db22096]
[25579] 12 Mar 03:33:23 # /opt/CSCOcpm/redis/redis-server(lzf_compress+0x276) [0x7eff5db22096]
[25579] 12 Mar 03:33:23 # /opt/CSCOcpm/redis/redis-server(rdbSaveLzfStringObject+0x7c) [0x7eff5db2d57c]
[25579] 12 Mar 03:33:23 # /opt/CSCOcpm/redis/redis-server(rdbSaveRawString+0x97) [0x7eff5db2d797]
[25579] 12 Mar 03:33:23 # /opt/CSCOcpm/redis/redis-server(rdbSaveObject+0x245) [0x7eff5db2daa5]
[25579] 12 Mar 03:33:23 # /opt/CSCOcpm/redis/redis-server(rdbSave+0x2f3) [0x7eff5db2dea3]
[25579] 12 Mar 03:33:23 # /opt/CSCOcpm/redis/redis-server(rdbSaveBackground+0x9f) [0x7eff5db2e0af]
[25579] 12 Mar 03:33:23 # /opt/CSCOcpm/redis/redis-server(serverCron+0x4ac) [0x7eff5db1fd4c]
[25579] 12 Mar 03:33:23 # /opt/CSCOcpm/redis/redis-server(aeProcessEvents+0x21a) [0x7eff5db1b01a]
[25579] 12 Mar 03:33:23 # /opt/CSCOcpm/redis/redis-server(aeMain+0x2e) [0x7eff5db1b18e]
[25579] 12 Mar 03:33:23 # /opt/CSCOcpm/redis/redis-server(main+0xf2) [0x7eff5db20422]
[25579] 12 Mar 03:33:23 # /lib64/libc.so.6(__libc_start_main+0xfd) [0x7eff5cecfd5d]
[25579] 12 Mar 03:33:23 # /opt/CSCOcpm/redis/redis-server(+0xe529) [0x7eff5db1a529]
[25579] 12 Mar 03:33:23 # --- INFO OUTPUT
[25579] 12 Mar 03:33:23 # redis_version:2.4.8^M
redis_git_sha1:00000000^M
redis_git_dirty:0^M
arch_bits:64^M
multiplexing_api:epoll^M
gcc_version:4.1.2^M
process_id:25579^M
uptime_in_seconds:99059^M
uptime_in_days:1^M
lru_clock:31167^M
used_cpu_sys:0.41^M
used_cpu_user:5.40^M
used_cpu_sys_children:0.00^M
used_cpu_user_children:0.00^M
connected_clients:11^M
connected_slaves:0^M
client_longest_output_list:0^M
client_biggest_input_buf:0^M
blocked_clients:0^M
used_memory:2372195024^M
used_memory_human:2.21G^M
used_memory_rss:1167618048^M
used_memory_peak:1001798808^M
used_memory_peak_human:955.39M^M
mem_fragmentation_ratio:0.49^M
mem_allocator:jemalloc-2.2.5^M
loading:0^M
aof_enabled:0^M
changes_since_last_save:10075^M
bgsave_in_progress:0^M
last_save_time:1489289495^M
bgrewriteaof_in_progress:0^M
total_connections_received:2286^M
total_commands_processed:28126076^M
expired_keys:0^M
evicted_keys:0^M
keyspace_hits:8903705^M
keyspace_misses:70864^M
pubsub_channels:0^M
pubsub_patterns:0^M
latest_fork_usec:2029^M
vm_enabled:0^M
role:master^M
db0:keys=70953,expires=0^M
db1:keys=12713,expires=0^M

[25579] 12 Mar 03:33:23 # --- CLIENT LIST OUTPUT
[25579] 12 Mar 03:33:23 # addr=127.0.0.1:42757 fd=10 idle=6 flags=N db=1 sub=0 psub=0 qbuf=0 obl=0 oll=0 events=r cmd=hmset
addr=127.0.0.1:51626 fd=11 idle=6 flags=N db=0 sub=0 psub=0 qbuf=0 obl=0 oll=0 events=r cmd=exists
addr=127.0.0.1:51875 fd=12 idle=28 flags=N db=0 sub=0 psub=0 qbuf=0 obl=0 oll=0 events=r cmd=hget
addr=127.0.0.1:51876 fd=13 idle=6 flags=N db=0 sub=0 psub=0 qbuf=0 obl=0 oll=0 events=r cmd=hget
addr=127.0.0.1:51878 fd=17 idle=6 flags=N db=0 sub=0 psub=0 qbuf=0 obl=5 oll=0 events=rw cmd=select
addr=127.0.0.1:51965 fd=6 idle=8 flags=N db=1 sub=0 psub=0 qbuf=0 obl=0 oll=0 events=r cmd=hgetall
addr=127.0.0.1:52028 fd=7 idle=6 flags=N db=0 sub=0 psub=0 qbuf=0 obl=0 oll=0 events=r cmd=hgetall
addr=127.0.0.1:52029 fd=8 idle=35 flags=N db=0 sub=0 psub=0 qbuf=0 obl=0 oll=0 events=r cmd=ping
addr=127.0.0.1:52063 fd=15 idle=6 flags=N db=0 sub=0 psub=0 qbuf=0 obl=0 oll=0 events=r cmd=hget
addr=127.0.0.1:52064 fd=16 idle=6 flags=N db=0 sub=0 psub=0 qbuf=0 obl=0 oll=0 events=r cmd=hset
addr=127.0.0.1:52065 fd=18 idle=35 flags=N db=0 sub=0 psub=0 qbuf=0 obl=0 oll=0 events=r cmd=ping



## Curated Answers



### High Signal Answer 1

Version 2.3.8 is quite ancient - more recent versions include fixes to many issues. You should strongly consider upgrading your Redis version.

- Author: itamarhaber
- Quality score: 4
- URL: https://github.com/redis/redis/issues/3870#issuecomment-286039238
