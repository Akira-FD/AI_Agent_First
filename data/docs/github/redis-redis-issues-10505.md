# [NEW] Allow WAIT to block until next fsync



## GitHub Provenance



- Repository: redis/redis

- Issue: #10505

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/10505



## Problem



**The problem/use-case that the feature addresses**

This would make "durability" in ACID possible to implement (at least indirectly) in Redis.

**Description of the feature**

A new flag for the `WAIT` command (https://redis.io/commands/wait/) called "SYNC". Adding that flag causes the command to block until the next `fsync` on AOF file for the specified number of replicas, or if the "number of replicas" parameter is 0, the command blocks until the next `fsync` on AOF file for the current Redis instance. If AOF persistence is not enabled, the command returns an error.

**Alternatives you've considered**

This could be implemented as a separate command called `FLUSH`, which blocks until the next `fsync` on AOF file and prompts an `fsync` call for the replicas. But the `WAIT` command might be a better place to implement such a feature since it is designed to improve data safety.

**Additional information**

When comparing Redis to traditional ACID databases, the AOF file is effectively the log file. Under default Redis configuration, fsync is done on the AOF file every second. However, there could still be data losses for up to one second before the data actually gets flushed.

Currently there is no mechanism to have that `fsync` happen from the client side. This means that there is no way for the client to ensure the data is safely stored to disk. Since Redis is single-threaded, waiting for an `fsync` can block all other clients and cause latency spikes, but that's not necessary; the client merely needs a signal that its data has been properly stored, not necessary synchronously.

Such a feature would not directly make Redis ACID-compliant. For example, Redis transactions do not revert in case of failures, and the data written before `WAIT` command are visible to other clients before they are actually persisted. However, this feature should at least make ACID properties possible with the minimal changes. A high-level API could, for example, carefully design commands so they can't fail, and make changes visible to other clients only after a `WAIT`. Other clients can call `WAIT` before perfoming a read to ensure that anything read from Redis is already persisted.



## Curated Answers



### High Signal Answer 1

This was discussed in the past, IIRC called WAITAOF.
Should certainly be on our roadmap.
To make it even more useful, we wanted the REPLCONF ACK sent by the replica to the master, to also include the replication offset that was sync to AOF, so we can wait till the last command was synced to the AOF on the replica side.
i.e. it is very common to let the replica handle persistence in order to avoid latency overheads on the master.

- Author: oranagra
- Quality score: 5
- URL: https://github.com/redis/redis/issues/10505#issuecomment-1086835558
