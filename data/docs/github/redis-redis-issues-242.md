# Possibility of Hash/Set/List fields expiration



## GitHub Provenance



- Repository: redis/redis

- Issue: #242

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/242



## Problem



Now it's possible to set expiration only for keys to main objects, not for collecion elements.
I have design problem with that.

Let's imagine we store session properties in the hash.
Session expires after some time, but we have to know how many sessions are still alive.
So... | created another collection to store active session list, where:
token (key), and key to session hash (value).

Now, when my session expires, it's token in active collection is still present,
and I have no posiibility to remove them.

Solutions:
1) Possibility of Hash/Set/List fields expiration. I wille simply set expiration of session token, the same like main session hash

2) Expiration triggers - when key expires, some command group wille be executed (Maybe Lua script)

3) Publish expiration message to earlier defined channel, containing expired key. Using drivers I could implements my own triggers



## Curated Answers



### High Signal Answer 1

Hi, this will not be implemented by original design:
- No nested types in keys.
- No complex features in single fields of aggregate data types.

The reasoning is much more complex and is a lot biased by personal feelings, preference and sensibility so there is no objective way I can show you this is better ;)

Closing. Thanks for reporting.

- Author: antirez
- Quality score: 17
- URL: https://github.com/redis/redis/issues/242#issuecomment-3512819
