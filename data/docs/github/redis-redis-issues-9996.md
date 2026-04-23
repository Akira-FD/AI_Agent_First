# [BUG] `XREADGROUP` with no results does not reset `XINFO CONSUMERS` idle timer



## GitHub Provenance



- Repository: redis/redis

- Issue: #9996

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/9996



## Problem



**Describe the bug**

The `idle` field of the [`XINFO CONSUMERS`](https://redis.io/commands/xinfo-consumers) return value is documented as:

> **idle**: the number of milliseconds that have passed since the consumer last interacted with the server

This number does not reset when the `XREADGROUP` command for that consumer returns an empty result.

**To reproduce**

```redis
XGROUP CREATE my-stream my-group 0 MKSTREAM
XGROUP CREATECONSUMER my-stream my-group my-consumer
```

… some time passes …

```
XREADGROUP GROUP my-group my-consumer COUNT 10 BLOCK 2000 STREAMS my-stream >
XINFO CONSUMERS my-stream my-group
```

**Expected behavior**

The `idle` field in the `XINFO CONSUMERS` return value, based on the phrase "since the consumer last interacted with the server" in the documentation, seems like it should return the time since that `XREADGROUP` command finished, since `XREADGROUP` is an interaction from the consumer.

**Additional information**

When `XREADGROUP` returns a non-empty array, it does seem to reset the `idle` timer, but not when it returns an empty array.

I'm trying to add functionality to a streaming library to remove stale consumers (for example, stream processors that have crashed due to OOM or SEGV) but it does not appear to be possible to automate for a low-volume consumer since the last message and the last interaction appear to be set to the same time.



## Curated Answers



### High Signal Answer 1

update: i went in a slightly different direction:
1. i "fixed" the current code so that seen-time/idle actually refers to interaction attempts (breaking change)
2. i added active-time/inactive to refer to successful interaction (what seen-time/idle used to be)

at first, i tried to avoid changing the behavior of seen-time/idle but then i realized that, in this case, the odds are the people read the docs and implemented their code based on the docs (which didn't match the behavior). for the most part that would work fine, except that this issue here was found.

i was working under the assumption that people relied on the docs, and for the most part, it could have worked well enough. so instead of fixing the docs, as i would usually do, i fixed the code to match the docs in this particular case

- Author: guybe7
- Quality score: 8
- URL: https://github.com/redis/redis/issues/9996#issuecomment-1214391427
