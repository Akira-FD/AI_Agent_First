# swap configuration



## GitHub Provenance



- Repository: redis/redis

- Issue: #6673

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/6673



## Problem



Redis administration link(https://redis.io/topics/virtual-memory) recommends configuring swap. 

"Make sure to setup some swap in your system (we suggest as much as swap as memory). If Linux does not have swap and your Redis instance accidentally consumes too much memory, either Redis will crash for out of memory or the Linux kernel OOM killer will kill the Redis process. When swapping is enabled Redis will work in a bad way, but you'll likely notice the latency spikes and do something before it's too late."

But virtual memory article says that it is disabled from 2.4 (http://redis.io/topics/virtual-memory)

So above guidelines in administration, should not be applicable for redis > 2.4. Can some please confirm that?



## Curated Answers



### High Signal Answer 1

Hello @thesreyas 

Yes, that recommendation relates to earlier versions of Redis. For modern versions, the usual recommendation is turning swap off.

Keep in mind that this issue tracker should be used for reporting bugs or proposing improvements to the Redis server. Kindly close this one.

Questions should be directed to the [community](https://redis.io/community):

* [/r/redis subreddit](http://www.reddit.com/r/redis)
* [the mailing list](https://groups.google.com/forum/#!forum/redis-db)
* [the `redis` tag at StackOverflow](http://stackoverflow.com/questions/tagged/redis)
* [the irc channel #redis](http://webchat.freenode.net/?channels=redis) on freenode.

- Author: itamarhaber
- Quality score: 5
- URL: https://github.com/redis/redis/issues/6673#issuecomment-566102753
