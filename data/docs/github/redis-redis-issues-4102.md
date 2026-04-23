# In Redis 4.0 partial synchronization not working when slave instance restarted.



## GitHub Provenance



- Repository: redis/redis

- Issue: #4102

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/4102



## Problem



I am experimenting with Redis 4.0 RC3 (redis-4.0.0-0.3.RC3.fc26.remi.x86_64) installed on both master and slave. In the release notes it is mentioned that with PSYNC2 the master-slave will be able to partially resynchronize when a slave instance is restarted. However when I tried this feature then the partial resynchronization is NOT happening after slave restarts. The slave still does FULL SYNC. I think this is a  bug.

Slave logs say:
Partial resynchronization not possible (no cached master)
Full resync from master: 2d126ef1e016de2d03279436babd55152eecbba9:4536

Steps:
1) Slave starts and connects to Master. Expectedly Full SYNC happens for first time.
2) Slave restarts and connects to Master but again FULL SYNC happens and not the expected partial 
    resync!

The RDB file on slave has correct ReplicationId and Offset from the first sync run of the slave but still after restart slave complains that 'no cached master'.

On Slave:

$ redis-check-rdb /var/lib/redis/dump.rdb 
[offset 85] AUX FIELD aof-preamble = '0'
[offset 135] AUX FIELD repl-id = '2d126ef1e016de2d03279436babd55152eecbba9'
[offset 151] AUX FIELD repl-offset = '4536'

$  redis-cli -h localhost -p 6379 
localhost:6379> INFO replication
role:slave
master_host:10.168.10.104
master_port:6379
master_link_status:up
master_last_io_seconds_ago:1
master_sync_in_progress:0
slave_repl_offset:4536
slave_priority:100
slave_read_only:0
connected_slaves:0
master_replid:2d126ef1e016de2d03279436babd55152eecbba9
master_replid2:0000000000000000000000000000000000000000
master_repl_offset:4536
second_repl_offset:-1
repl_backlog_active:1
repl_backlog_size:10485760
repl_backlog_first_byte_offset:3949
repl_backlog_histlen:14


On Master before slave connects:

localhost:6379> INFO replication
role:master
connected_slaves:0
master_replid:2d126ef1e016de2d03279436babd55152eecbba9
master_replid2:0000000000000000000000000000000000000000
master_repl_offset:4536
second_repl_offset:-1
repl_backlog_active:1
repl_backlog_size:104857600
repl_backlog_first_byte_offset:1
repl_backlog_histlen:4536
localhost:6379> INFO replication

Issue: In 4.0 slave does NOT partially resynchronize with master after slave restarts.



## Curated Answers



### High Signal Answer 1

Hello, thanks for your hints, yes... that makes sense, it's non obvious how to do it properly, but we want to do it, also because supporting slave restarts with partial resync with RDB forced us to do a lot of work in the replication side, so not exploiting it also for AOF is a shame. I think that we should start at least to provide ASAP the restart with the slave is stopped with SHUTDOWN. This is trivial because we can just append the metadata to AOF. Then we can figure out how to do the rest... that is, to snapshot from time to time such metadata into the AOF and make Redis able to discard the last tail after the last snapshot, so that it is possible to restart the replication easily.

- Author: antirez
- Quality score: 4
- URL: https://github.com/redis/redis/issues/4102#issuecomment-434015612
