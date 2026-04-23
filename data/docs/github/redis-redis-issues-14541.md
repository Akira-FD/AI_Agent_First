# [NEW]Option to skip EXEC ACL re-check during AOF loading.



## GitHub Provenance



- Repository: redis/redis

- Issue: #14541

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/14541



## Problem



**The problem/use-case that the feature addresses**

When Redis loads an AOF and ACL rules were tightened after that AOF was generated, there is an asymmetric behavior:

-  Non-transactional writes in the AOF are replayed successfully (even if the current ACL would forbid them now).
-  Transactional writes inside MULTI/EXEC in the same AOF are blocked by ACL during EXEC’s internal ACL re-check.

This leads to a partially historical state: some keys from the AOF are restored, while others are rejected only because they were part of a transaction and got denied by EXEC’s extra ACL re-check. My understanding is that the re-check was originally designed to catch ACL changes between MULTI and EXEC at runtime, but during AOF replay the fact that the commands are already in the AOF means they must have passed ACL at the time, so this additional check arguably shouldn’t be the reason that prevents them from being restored. I mean even if something is supposed to block these writes during AOF loading, it probably shouldn’t be this EXEC re-check.


**Reproduction**

Environment: Redis 7.2.5:
```
port 6379
dir .
appendonly yes
appendfsync everysec
aclfile ./work/redis-aof-acl/users.acl
loglevel notice
aof-use-rdb-preamble no
auto-aof-rewrite-percentage 0
auto-aof-rewrite-min-size 0
save ""
```
Initial ACL (fully open):

`user default on nopass allkeys allchannels +@all`

 Start Redis with this ACL and config.

 From a client, run:

```
SET beforetx beforetx
MULTI
SET tx1 tx1
SET tx2 tx2
EXEC
SET aftertx aftertx
```

The AOF contains:

```
SET beforetx beforetx
MULTI
SET tx1 tx1
SET tx2 tx2
EXEC
SET aftertx aftertx
```

change ACL in the config 

`user default on nopass allkeys allchannels +@read -@write +multi +exec`

Restart Redis with the AOF.

```
127.0.0.1:6379> KEYS *
1) "beforetx"
2) "aftertx"
127.0.0.1:6379>
```
 there is not tx1 and tx2 , and the server logs something like this

`84815:M 17 Nov 2025 15:49:42.088 # == CRITICAL == This server is sending an error to its AOF-loading-client: '-NOPERM ACLs rules changed between the moment the transaction was accumulated and the EXEC call. This command is no longer allowed for the following reason: no permission to execute the command or subcommand' after processing the command 'exec'
`

**Description of the feature**

Add an optional configuration flag that only affects the AOF-loading client during server.loading

`aof-skip-exec-acl-recheck no # default: no (current behavior preserved)`

When `aof-skip-exec-acl-recheck` is yes:
 -  EXEC does not perform the extra ACL re-check on its queued commands during AOF replay.

Result:
-  In the reproduction above, tx1 and tx2 would be restored as well
-  the -NOPERM ACLs rules changed ... critical logs would not appear.
-  for users who expect AOF to replay everything that succeeded in the past, this may be useful.

**Additional information**

This is my current understanding, if I’m missing something I’d really appreciate any feedback. If this makes sense, I’d like to work on a patch.



## Curated Answers



### High Signal Answer 1

It sounds like we shouldn't check permissions when loading AOF

- Author: ShooterIT
- Quality score: 4
- URL: https://github.com/redis/redis/issues/14541#issuecomment-3545692191
