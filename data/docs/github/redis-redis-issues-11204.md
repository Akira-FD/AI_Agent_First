# used_memory_peak keep growing but used_memory/used_memory_rss is small



## GitHub Provenance



- Repository: redis/redis

- Issue: #11204

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/11204



## Problem



The Redis deployment:
- A single instance Redis deployment with a small data set used_memory 80M, RBD 26M.
- Read/write workload is balanced, ops/sec: 2k
- RDB `save 900 1 300 50 60 100`,  triggered every 1-2 minutes
- AOF on, `appendfsync everysec`
- Redis version: 7.0.4 (always tested on 4.0.9, same issue)
- `vm.overcommit_memory = 1`
- `transparent_hugepage = madvise`
- `maxmemory 1GB` and `maxmemory-policy noeviction`
- OS: Ubuntu 18.04.3 LTS, bionic
- OS memory: 2G

The problem:
- The used_memory_peak keeps growing during a time and beyond the `maxmemory` settings, while `used_memory` is small
- The client starts receiving the `OOM command not allowed when used memory > maxmemory message` message
- Redis can continue to perform read/write commands when used_memory reduces to normal
- Restart Redis can fix the high used_memory_peak issue. But used_memory_peak is catching up quickly for every 2-3 days, then it reproduces the OOM error  again

What to expect: the used_memory_peak should not keep growing.

Dataset
- hash set with 10K keys. Field size ranges from a few bytes to a few KB. It worth to notice that most hash fields are getting updated hourly. (it's not a cache-like heavy read senario)
- two continuous updated lists with 2K elements

info output:

```
# Server
redis_version:7.0.4
redis_git_sha1:00000000
redis_git_dirty:0
redis_build_id:c7d71d4b63066c
redis_mode:standalone
os:Linux 4.15.0-66-generic x86_64
arch_bits:64
monotonic_clock:POSIX clock_gettime
multiplexing_api:epoll
atomicvar_api:c11-builtin
gcc_version:7.5.0
process_id:12185
process_supervised:systemd
run_id:8354e5bed5dbe1fccf5e646a145b0f61da9e48ea
tcp_port:6379
server_time_usec:1661790764977190
uptime_in_seconds:180951
uptime_in_days:2
hz:10
configured_hz:10
lru_clock:846380
executable:/usr/bin/redis-server
config_file:/etc/redis/redis.conf
io_threads_active:0

# Clients
connected_clients:11
cluster_connections:0
maxclients:10000
client_recent_max_input_buffer:24576
client_recent_max_output_buffer:0
blocked_clients:0
tracking_clients:0
clients_in_timeout_table:0

# Memory
used_memory:75396296
used_memory_human:71.90M
used_memory_rss:93913088
used_memory_rss_human:89.56M
used_memory_peak:874747728
used_memory_peak_human:834.22M
used_memory_peak_perc:8.62%
used_memory_overhead:1625088
used_memory_startup:862872
used_memory_dataset:73771208
used_memory_dataset_perc:98.98%
allocator_allocated:75875800
allocator_active:80228352
allocator_resident:92692480
total_system_memory:2090356736
total_system_memory_human:1.95G
used_memory_lua:72704
used_memory_vm_eval:72704
used_memory_lua_human:71.00K
used_memory_scripts_eval:5368
number_of_cached_scripts:5
number_of_functions:0
number_of_libraries:0
used_memory_vm_functions:32768
used_memory_vm_total:105472
used_memory_vm_total_human:103.00K
used_memory_functions:184
used_memory_scripts:5552
used_memory_scripts_human:5.42K
maxmemory:1073741824
maxmemory_human:1.00G
maxmemory_policy:noeviction
allocator_frag_ratio:1.06
allocator_frag_bytes:4352552
allocator_rss_ratio:1.16
allocator_rss_bytes:12464128
rss_overhead_ratio:1.01
rss_overhead_bytes:1220608
mem_fragmentation_ratio:1.25
mem_fragmentation_bytes:18539112
mem_not_counted_for_evict:3584
mem_replication_backlog:0
mem_total_replication_buffers:0
mem_clients_slaves:0
mem_clients_normal:233832
mem_cluster_links:0
mem_aof_buffer:3584
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
rdb_changes_since_last_save:1867
rdb_bgsave_in_progress:0
rdb_last_save_time:1661790710
rdb_last_bgsave_status:ok
rdb_last_bgsave_time_sec:0
rdb_current_bgsave_time_sec:-1
rdb_saves:2961
rdb_last_cow_size:1724416
rdb_last_load_keys_expired:0
rdb_last_load_keys_loaded:9696
aof_enabled:1
aof_rewrite_in_progress:0
aof_rewrite_scheduled:0
aof_last_rewrite_time_sec:0
aof_current_rewrite_time_sec:-1
aof_last_bgrewrite_status:ok
aof_rewrites:54
aof_rewrites_consecutive_failures:0
aof_last_write_status:ok
aof_last_cow_size:2101248
module_fork_in_progress:0
module_fork_last_cow_size:0
aof_current_size:64293026
aof_base_size:26768248
aof_pending_rewrite:0
aof_buffer_length:0
aof_pending_bio_fsync:0
aof_delayed_fsync:0

# Stats
total_connections_received:3279
total_commands_processed:166708366
instantaneous_ops_per_sec:94
total_net_input_bytes:13110746003
total_net_output_bytes:1023300757932
total_net_repl_input_bytes:0
total_net_repl_output_bytes:0
instantaneous_input_kbps:13.49
instantaneous_output_kbps:952.60
instantaneous_input_repl_kbps:0.00
instantaneous_output_repl_kbps:0.00
rejected_connections:0
sync_full:0
sync_partial_ok:0
sync_partial_err:0
expired_keys:32393
expired_stale_perc:0.00
expired_time_cap_reached_count:0
expire_cycle_cpu_milliseconds:5031
evicted_keys:0
evicted_clients:0
total_eviction_exceeded_time:0
current_eviction_exceeded_time:0
keyspace_hits:153600497
keyspace_misses:294921
pubsub_channels:2
pubsub_patterns:0
pubsubshard_channels:0
latest_fork_usec:4069
total_forks:3015
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
total_error_replies:7194
dump_payload_sanitizations:0
total_reads_processed:97876771
total_writes_processed:65215040
io_threaded_reads_processed:0
io_threaded_writes_processed:0
reply_buffer_shrinks:71960
reply_buffer_expands:209143

# Replication
role:master
connected_slaves:0
master_failover_state:no-failover
master_replid:e37f7b0e1c92fc1b44b73954193cbd5e531cec54
master_replid2:0000000000000000000000000000000000000000
master_repl_offset:0
second_repl_offset:-1
repl_backlog_active:0
repl_backlog_size:1048576
repl_backlog_first_byte_offset:0
repl_backlog_histlen:0

# CPU
used_cpu_sys:2951.271491
used_cpu_user:2038.693100
used_cpu_sys_children:182.416595
used_cpu_user_children:1118.169646
used_cpu_sys_main_thread:2897.980343
used_cpu_user_main_thread:2032.222419

# Modules

# Errorstats
errorstat_ERR:count=7194

# Cluster
cluster_enabled:0

# Keyspace
db0:keys=9703,expires=1,avg_ttl=1648
```

bigkeys output

```
-------- summary -------

Sampled 9703 keys in the keyspace!
Total key length in bytes is 371795 (avg len 38.32)

Biggest   list found '"bq:main:waiting"' has 1332 items
Biggest   hash found '"bq:main:jobs"' has 1340 fields
Biggest string found '"pkgs:extra"' has 289767 bytes
Biggest    set found '"ve:pkgs"' has 1864 members

2 lists with 1337 items (00.02% of keys, avg size 668.50)
9692 hashs with 60329 fields (99.89% of keys, avg size 6.22)
7 strings with 393826 bytes (00.07% of keys, avg size 56260.86)
0 streams with 0 entries (00.00% of keys, avg size 0.00)
2 sets with 1866 members (00.02% of keys, avg size 933.00)
0 zsets with 0 members (00.00% of keys, avg size 0.00)
```

config
```
bind 0.0.0.0 ::1
protected-mode yes
port 6379
tcp-backlog 511
timeout 0
tcp-keepalive 300
daemonize yes
supervised auto
pidfile /run/redis/redis-server.pid
loglevel notice
logfile /var/log/redis/redis-server.log
databases 16
always-show-logo no
set-proc-title yes
proc-title-template "{title} {listen-addr} {server-mode}"
save 900 1
save 300 50
save 60 100
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
rdb-del-sync-files no
dir /var/lib/redis
replica-serve-stale-data yes
replica-read-only yes
repl-diskless-sync yes
repl-diskless-sync-delay 5
repl-diskless-sync-max-replicas 0
repl-diskless-load disabled
repl-disable-tcp-nodelay no
replica-priority 100
acllog-max-len 128
requirepass **********
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command KEYS ""
rename-command CONFIG ""
rename-command SHUTDOWN ""
maxmemory 1GB
maxmemory-policy noeviction
maxmemory-samples 5
lazyfree-lazy-eviction no
lazyfree-lazy-expire no
lazyfree-lazy-server-del no
replica-lazy-flush no
lazyfree-lazy-user-del no
lazyfree-lazy-user-flush no
oom-score-adj no
oom-score-adj-values 0 200 800
disable-thp yes
appendonly yes
appendfilename "appendonly.aof"
appenddirname "appendonlydir"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-load-truncated yes
aof-use-rdb-preamble yes
aof-timestamp-enabled no

slowlog-log-slower-than 10000
slowlog-max-len 128
latency-monitor-threshold 0
notify-keyspace-events ""
hash-max-listpack-entries 512
hash-max-listpack-value 64
list-max-listpack-size -2
list-compress-depth 0
set-max-intset-entries 512
zset-max-listpack-entries 128
zset-max-listpack-value 64
hll-sparse-max-bytes 3000
stream-node-max-bytes 4096
stream-node-max-entries 100
activerehashing yes
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
hz 10
dynamic-hz yes
aof-rewrite-incremental-fsync yes
rdb-save-incremental-fsync yes
jemalloc-bg-thread yes
```

MEMORY MALLOC-STATS
```
___ Begin jemalloc statistics ___
Version: "5.2.1-0-g0"
Build-time option settings
  config.cache_oblivious: true
  config.debug: false
  config.fill: true
  config.lazy_lock: false
  config.malloc_conf: ""
  config.opt_safety_checks: false
  config.prof: false
  config.prof_libgcc: false
  config.prof_libunwind: false
  config.stats: true
  config.utrace: false
  config.xmalloc: false
Run-time option settings
  opt.abort: false
  opt.abort_conf: false
  opt.confirm_conf: false
  opt.retain: true
  opt.dss: "secondary"
  opt.narenas: 1
  opt.percpu_arena: "disabled"
  opt.oversize_threshold: 8388608
  opt.metadata_thp: "disabled"
  opt.background_thread: false (background_thread: true)
  opt.dirty_decay_ms: 10000 (arenas.dirty_decay_ms: 10000)
  opt.muzzy_decay_ms: 0 (arenas.muzzy_decay_ms: 0)
  opt.lg_extent_max_active_fit: 6
  opt.junk: "false"
  opt.zero: false
  opt.tcache: true
  opt.lg_tcache_max: 15
  opt.thp: "default"
  opt.stats_print: false
  opt.stats_print_opts: ""
Arenas: 2
Quantum size: 8
Page size: 4096
Maximum thread-cached size class: 32768
Number of bin size classes: 39
Number of thread-cache bin size classes: 44
Number of large size classes: 196
Allocated: 75871872, active: 80171008, metadata: 8122408 (n_thp 0), resident: 88342528, mapped: 92893184, retained: 948342784
Background threads: 1, num_runs: 97805, run_interval: 1852260339 ns
                           n_lock_ops (#/sec)       n_waiting (#/sec)      n_spin_acq (#/sec)  n_owner_switch (#/sec)   total_wait_ns   (#/sec)     max_wait_ns  max_n_thds
background_thread             3601540      19               0       0               0       0               1       0               0         0               0           0
ctl                           7208312      39               0       0               0       0               1       0               0         0               0           0
prof                                0       0               0       0               0       0               0       0               0         0               0           0
arenas[0]:
assigned threads: 3
uptime: 181196118161028
dss allocation precedence: "secondary"
decaying:  time       npages       sweeps     madvises       purged
   dirty: 10000           34        79747      1167374     88675723
   muzzy:     0            0            0            0            0
                            allocated         nmalloc (#/sec)         ndalloc (#/sec)       nrequests   (#/sec)           nfill   (#/sec)          nflush   (#/sec)
small:                       35427968        22884936     126        22664739     125       863484357      4765         4002921        22         1610205         8
large:                       40443904        19417855     107        19416954     107        27892586       153        19417855       107         1685269         9
total:                       75871872        42302791     233        42081693     232       891376943      4919        23420776       129         3295474        18

active:                      80171008
mapped:                      92893184
retained:                   948342784
base:                         8024064
internal:                       98344
metadata_thp:                       0
tcache_bytes:                  143096
resident:                    88342528
abandoned_vm:                       0
extent_avail:                   23773
                           n_lock_ops (#/sec)       n_waiting (#/sec)      n_spin_acq (#/sec)  n_owner_switch (#/sec)   total_wait_ns   (#/sec)     max_wait_ns  max_n_thds
large                         1802279       9               0       0               0       0               1       0               0         0               0           0
extent_avail                 38950890     214               4       0               0       0          134347       0               0         0               0           1
extents_dirty                69054893     381              25       0               0       0          159631       0               0         0               0           1
extents_muzzy                 1807146       9               0       0               0       0               1       0               0         0               0           0
extents_retained             22433018     123               1       0               0       0          147645       0               0         0               0           1
decay_dirty                   2230273      12               0       0               0       0          196258       1               0         0               0           0
decay_muzzy                   2226811      12               0       0               0       0          171657       0               0         0               0           0
base                          3629779      20               0       0               0       0               5       0               0         0               0           0
tcache_list                   1802282       9               0       0               0       0               5       0               0         0               0           0
bins:           size ind    allocated      nmalloc (#/sec)      ndalloc (#/sec)    nrequests   (#/sec)  nshards      curregs     curslabs  nonfull_slabs regs pgs   util       nfills (#/sec)     nflushes (#/sec)       nslabs     nreslabs (#/sec)      n_lock_ops (#/sec)       n_waiting (#/sec)      n_spin_acq (#/sec)  n_owner_switch (#/sec)   total_wait_ns   (#/sec)     max_wait_ns  max_n_thds
                   8   0       364544       139409       0        93841       0     15416252        85        1        45568           90              1  512   1  0.988        69383       0        53058       0          103         1222       0         1924837      10               0       0               0       0               1       0               0         0               0           0
                  16   1       677408       433433       2       391095       2     28808785       158        1        42338          167              3  256   1  0.990        70414       0        55453       0          332        10404       0         1928645      10               0       0               0       0            3639       0               0         0               0           0
                  24   2      1699416     18539867     102     18469058     101    495930525      2736        1        70809          153             23  512   3  0.903      2531010      13       255280       1          615       146824       0         4589646      25               0       0               0       0            3635       0               0         0               0           0
                  32   3       236384       408004       2       400617       2    111870902       617        1         7387           59             22  128   1  0.978       103725       0       100175       0          136        82759       0         2006392      11               0       0               0       0               1       0               0         0               0           0
                  40   4       133240       484839       2       481508       2     17159991        94        1         3331            7              2  512   5  0.929       124465       0        94698       0           10        28409       0         2021455      11               0       0               0       0               1       0               0         0               0           0
                  48   5       110640       447552       2       445247       2     51301701       283        1         2305           11              5  256   3  0.818        76355       0        90399       0           91        16959       0         1969204      10               0       0               0       0               1       0               0         0               0           0
                  56   6       611968       346025       1       335097       1     73619509       406        1        10928           24              3  512   7  0.889        96912       0        76897       0          123         9097       0         1976310      10               0       0               0       0               1       0               0         0               0           0
                  64   7       142080       162313       0       160093       0     42075839       232        1         2220           57             55   64   1  0.608        79346       0        57801       0           58        19444       0         1939485      10               0       0               0       0               1       0               0         0               0           0
                  80   8       162000        58226       0        56201       0      7239193        39        1         2025            8              1  256   5  0.988        31111       0        23434       0          144         5246       0         1857104      10               0       0               0       0               1       0               0         0               0           0
                  96   9        93408        64119       0        63146       0      2011540        11        1          973            8              0  128   3  0.950        48867       0        45486       0           15         7272       0         1896654      10               0       0               0       0               1       0               0         0               0           0
                 112  10       156016        43109       0        41716       0      1020392         5        1         1393            6              1  256   7  0.906        33301       0        33788       0            8         5773       0         1869378      10               0       0               0       0               1       0               0         0               0           0
                 128  11       345344        41991       0        39293       0      1437191         7        1         2698           85             16   32   1  0.991        36374       0        36396       0           87         9774       0         1875138      10               0       0               0       0               1       0               0         0               0           0
                 160  12        48480        71757       0        71454       0      1546570         8        1          303            3              0  128   5  0.789        53177       0        46799       0            5        22999       0         1902262      10               0       0               0       0               1       0               0         0               0           0
                 192  13       384192       934980       5       932979       5      5085368        28        1         2001           33              3   64   3  0.947        96558       0       104221       0        12897         5945       0         2028819      11               0       0               0       0               1       0               0         0               0           0
                 224  14      1907584        53209       0        44693       0       787396         4        1         8516           67              1  128   7  0.993        31009       0        31148       0           68         8954       0         1864505      10               0       0               0       0               1       0               0         0               0           0
                 256  15      2760960        34429       0        23644       0       204412         1        1        10785          675              0   16   1  0.998        20883       0        20302       0         1163         5828       0         1845115      10               0       0               0       0               1       0               0         0               0           0
                 320  16       235520        23402       0        22666       0       140794         0        1          736           12              0   64   5  0.958        20479       0        20554       0           16            4       0         1843332      10               0       0               0       0               1       0               0         0               0           0
                 384  17        53376        60357       0        60218       0      5611801        30        1          139            5              1   32   3  0.868        47967       0        48503       0            8        22599       0         1898760      10               0       0               0       0               1       0               0         0               0           0
                 448  18        47040        26683       0        26578       0        79043         0        1          105            2              0   64   7  0.820        21554       0        21686       0            4            2       0         1845525      10               0       0               0       0               1       0               0         0               0           0
                 512  19        81920        21795       0        21635       0       838272         4        1          160           20              0    8   1      1        17465       0        17400       0         4520         3981       0         1846164      10               0       0               0       0               1       0               0         0               0           0
                 640  20       120320        20635       0        20447       0       162614         0        1          188            6              0   32   5  0.979        17205       0        17226       0           11            4       0         1836726      10               0       0               0       0               1       0               0         0               0           0
                 768  21       163584        24751       0        24538       0        49871         0        1          213           14              1   16   3  0.950        17747       0        19405       0           21         3562       0         1839459      10               0       0               0       0               1       0               0         0               0           0
                 896  22       124544        20576       0        20437       0        41378         0        1          139            5              2   32   7  0.868        18073       0        17612       0            8         6081       0         1837975      10               0       0               0       0               1       0               0         0               0           0
                1024  23       176128        36977       0        36805       0        93103         0        1          172           44              2    4   1  0.977        26604       0        28480       0         1485        19374       0         1860289      10               0       0               0       0               1       0               0         0               0           0
                1280  24       423680        22963       0        22632       0        54100         0        1          331           21              1   16   5  0.985        19752       0        19000       0           22        11074       0         1841054      10               0       0               0       0               1       0               0         0               0           0
                1536  25       436224        25808       0        25524       0        50939         0        1          284           36              0    8   3  0.986        21986       0        20445       0          274          230       0         1845222      10               0       0               0       0               1       0               0         0               0           0
                1792  26       456960        22104       0        21849       0        65576         0        1          255           16              1   16   7  0.996        19291       0        18796       0         1430         6347       0         1843210      10               0       0               0       0               1       0               0         0               0           0
                2048  27       475136        35443       0        35211       0        93547         0        1          232          116              0    2   1      1        27264       0        28193       0        12947         8533       0         1883514      10               0       0               0       0               1       0               0         0               0           0
                2560  28      1141760        23455       0        23009       0        61582         0        1          446           56              1    8   5  0.995        19616       0        19105       0          624         6716       0         1842192      10               0       0               0       0               1       0               0         0               0           0
                3072  29      1195008        25061       0        24672       0        80687         0        1          389           98              0    4   3  0.992        21095       0        20652       0         7438         4584       0         1858804      10               0       0               0       0               1       0               0         0               0           0
                3584  30      1257984        21418       0        21067       0        47622         0        1          351           44              0    8   7  0.997        18343       0        17802       0           71           27       0         1838522      10               0       0               0       0               1       0               0         0               0           0
                4096  31      1429504        34910       0        34561       0        94062         0        1          349          349              0    1   1      1        26519       0        27382       0        34910            0       0         1925651      10               0       0               0       0               1       0               0         0               0           0
                5120  32      2380800        29439       0        28974       0        82163         0        1          465          117              1    4   5  0.993        23051       0        21954       0         2518        10144       0         1852203      10               0       0               0       0               1       0               0         0               0           0
                6144  33      2260992        28033       0        27665       0        60915         0        1          368          185              2    2   3  0.994        22238       0        19936       0         4484        16281       0         1853236      10               0       0               0       0               1       0               0         0               0           0
                7168  34      1892352        25983       0        25719       0        49110         0        1          264           66              0    4   7      1        21167       0        18477       0         1814        10508       0         1845485      10               0       0               0       0               1       0               0         0               0           0
                8192  35      2023424        35399       0        35152       0        83791         0        1          247          247              0    1   2      1        25278       0        26433       0        35399            0       0         1924541      10               0       0               0       0               1       0               0         0               0           0
               10240  36      3819520        22414       0        22041       0        58767         0        1          373          187              1    2   5  0.997        18794       0        14083       0         7925         9946       0         1850819      10               0       0               0       0               1       0               0         0               0           0
               12288  37      2961408        20086       0        19845       0        44840         0        1          241          241              0    1   3      1        16727       0        13337       0        20086            0       0         1872274      10               0       0               0       0               1       0               0         0               0           0
               14336  38      2437120        13982       0        13812       0        24214         0        1          170           85              0    2   7      1        11816       0         8409       0         3379         8454       0         1829177      10               0       0               0       0               1       0               0         0               0           0
large:          size ind    allocated      nmalloc (#/sec)      ndalloc (#/sec)    nrequests (#/sec)  curlextents
               16384  39      2113536        18776       0        18647       0        56607       0          129
               20480  40      3727360     14147744      78     14147562      78     21571491     119          182
               24576  41      3686400       536856       2       536706       2       966652       5          150
               28672  42      2121728       509812       2       509738       2       824567       4           74
               32768  43      2392064       290623       1       290550       1       559225       3           73
               40960  44      3481600       726183       4       726098       4       726183       4           85
               49152  45      2457600       540095       2       540045       2       540095       2           50
               57344  46      1720320       342278       1       342248       1       342278       1           30
               65536  47      1507328       411680       2       411657       2       411680       2           23
               81920  48      2293760       345112       1       345084       1       345112       1           28
               98304  49      1867776       349519       1       349500       1       349519       1           19
              114688  50      1835008       222161       1       222145       1       222161       1           16
              131072  51      1179648       326572       1       326563       1       326572       1            9
              163840  52      1146880        50204       0        50197       0        50204       0            7
              196608  53      1179648       158131       0       158125       0       158131       0            6
              229376  54       917504       101889       0       101885       0       101889       0            4
              262144  55      1310720        20832       0        20827       0        20832       0            5
              327680  56       655360        37316       0        37314       0        37316       0            2
              393216  57      1179648        96870       0        96867       0        96870       0            3
              458752  58       917504        32186       0        32184       0        32186       0            2
              524288  59       524288        34218       0        34217       0        34218       0            1
              655360  60       655360        33678       0        33677       0        33678       0            1
              786432  61      1572864        85120       0        85118       0        85120       0            2
                     ---
extents:        size ind       ndirty        dirty       nmuzzy        muzzy    nretained     retained       ntotal        total
                4096   0            1         4096            0            0           18        73728           19        77824
                8192   1            0            0            0            0           15       122880           15       122880
               12288   2            0            0            0            0           21       258048           21       258048
               16384   3            0            0            0            0            9       147456            9       147456
               20480   4            0            0            0            0           10       204800           10       204800
               24576   5            0            0            0            0           10       245760           10       245760
               28672   6            0            0            0            0            2        57344            2        57344
               32768   7            0            0            0            0            3        98304            3        98304
               40960   8            0            0            0            0            8       311296            8       311296
               49152   9            0            0            0            0            4       184320            4       184320
               57344  10            0            0            0            0            3       163840            3       163840
                     ---
               81920  12            0            0            0            0            2       143360            2       143360
                     ---
              114688  14            0            0            0            0            1       106496            1       106496
                     ---
              163840  16            1       135168            0            0            0            0            1       135168
                     ---
              458752  22            0            0            0            0            1       458752            1       458752
                     ---
              917504  26            0            0            0            0            2      1642496            2      1642496
             1048576  27            0            0            0            0            2      2072576            2      2072576
             1310720  28            0            0            0            0            1      1146880            1      1146880
                     ---
             2621440  32            0            0            0            0            1      2203648            1      2203648
                     ---
             3670016  34            0            0            0            0            1      3411968            1      3411968
             4194304  35            0            0            0            0            1      3817472            1      3817472
             5242880  36            0            0            0            0            2      9633792            2      9633792
             6291456  37            0            0            0            0            2     11452416            2     11452416
                     ---
             8388608  39            0            0            0            0            2     15212544            2     15212544
            10485760  40            0            0            0            0            1      9121792            1      9121792
            12582912  41            0            0            0            0            1     12349440            1     12349440
                     ---
            20971520  44            0            0            0            0            1     17006592            1     17006592
                     ---
            41943040  48            0            0            0            0            2     76554240            2     76554240
                     ---
           805306368  65            0            0            0            0            1    780140544            1    780140544
                     ---
--- End jemalloc statistics ---
```

top (VIRT is high)
```
  PID USER      PR  NI    VIRT    RES    SHR S %CPU %MEM     TIME+ COMMAND
12185 redis     20   0 1092568 113256   5620 S  9.0  5.5  83:27.07 /usr/bin/redis-server 0.0.0.0:6379
```

Any help is appreciated.



## Curated Answers



### High Signal Answer 1

let me see if i get this right.
at some point, some clients get OOM error, and later when you look at INFO you see the peak was high, but by now the used_memory returned below the limit. is that right?

it sounds normal to me... i.e. during some workload the used memory grew beyond the limit, clients started getting OOM error, then the used memory shrunk and now all we can see is the old peak.

since you have noeviction set, and maybe you don't even delete anything, then the suspect is probably client output buffers.
i.e. some client sends a workload that results in big output buffers (either one command with a big reply, or a pipeline of a lot of smaller ones).

maybe setting `client-output-buffer-limit`, `client-query-buffer-limit`, or `maxmemory-clients` can mitigate that.

- Author: oranagra
- Quality score: 4
- URL: https://github.com/redis/redis/issues/11204#issuecomment-1233883748

### High Signal Answer 2

Sadly, there's not peak metric for the clients memory, but maybe the solution for both issues (the OOM kill too) is to use the `maxmemory-clients` config.

- Author: oranagra
- Quality score: 4
- URL: https://github.com/redis/redis/issues/11204#issuecomment-1235641002
