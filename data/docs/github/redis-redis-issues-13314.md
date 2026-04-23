# [BUG] Record, deleted from stream, stays in PEL



## GitHub Provenance



- Repository: redis/redis

- Issue: #13314

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/13314



## Problem



**Describe the bug**

In our implementation, after reading messages from stream (with XREADGROUP), we delete it from the stream(with XDEL). In this case, messages stay in Pending Entities List, which leads to OOM at some point.

**To reproduce**

We use XADD to add messages, XREAD GROUP to read them, XDEL to delete, and XINFO STREAM FULL to check PEL-count.

**Expected behavior**

Messages, deleted from the stream with XDEL, should probably be deleted from the PEL too, without explicit XACK. Or, if there is a reason for current behavior to be expected, it should be documented to be clear.



## Curated Answers



### High Signal Answer 1

@trilga We have added a new XDELEX command in https://github.com/redis/redis/pull/14130 to support the simultaneous deletion of PEL when deleting elements.

- Author: sundb
- Quality score: 4
- URL: https://github.com/redis/redis/issues/13314#issuecomment-3026065391
