# Allow to set an expiration on hash field



## GitHub Provenance



- Repository: redis/redis

- Issue: #1042

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/1042



## Problem



Right now the `EXPIRE` command only allows to set an expiration time on a key. It would be cool to have the possibility to set it on a field of an hash object. For example:

```
HSET key field "Hello"
EXPIRE key field 10
```

In the example above the `EXPIRE` command sets an expiration time of 10 seconds to the `field` hash field, and not to the `key` object.



## Curated Answers



### High Signal Answer 1

+1 Any chance this feature could be reconsidered?

- Author: pensierinmusica
- Quality score: 167
- URL: https://github.com/redis/redis/issues/1042#issuecomment-143109286

### High Signal Answer 2

+1 Here we are, almost 5 years after the first request and Redis still does not support the expiration of individual keys :(

Many people would love to have that feature available in Redis

- Author: danielsan
- Quality score: 129
- URL: https://github.com/redis/redis/issues/1042#issuecomment-366057753

### High Signal Answer 3

Yup, implementation problem.

Small hashes can be stored in ziplists which is just a length-prefixed arrangement of your field-value pairs.  So, (abstractly) if you do `HSET key field1 val1` what Redis stores is: `[6]field1[4]val1`.  If you add field2 with val2, the value of `key` becomes `[6]field1[4]val1[6]field2[4]val2`.  There's _no way_ to reference individual hash fields in that situation for expiration.

Larger hashes get converted to actual hash tables, but even then, Redis has no way to address an individual hashtable entry for global expiration behavior.

If you need expiration for "data is invalid after X seconds" reasons, you can store another field in your hash with `[fieldname]_expiresAt` then always retrieve that with your `[fieldname]` to check if the data is still valid.  Now, that obviously doesn't qualify the data for auto-expiration under memory pressure, but you could _also_ use `HSCAN` to scan your hashes periodically, read all your `_expiresAt` fields, then manually delete values outside the expiration time.

- Author: mattsta
- Quality score: 13
- URL: https://github.com/redis/redis/issues/1042#issuecomment-45367109
