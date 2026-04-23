# slave hung in processUnblockedClients



## GitHub Provenance



- Repository: redis/redis

- Issue: #5229

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/5229



## Problem



Here's an issue i'm unable to figure out. maybe someone can help...

A slave redis (4.0.9) stopped responding, and ate 100% CPU for some half an hour.
```
~# time redis-cli <port> info all     
Could not connect to Redis at 10.0.1.9:29565: Connection timed out

real    2m9.415s
user    0m0.036s
sys     0m0.011s
```

The watchdog was trying to kill it with SIGTERM (10 signals one second apart), but it's not responding to these either. and the log shows:
```
4116:S 08 Aug 15:51:31.685 # == CRITICAL == This slave is sending an error to its master: 'Error running script (call to f_d4d1d1b62afa6d576d81cfbecc482ad7e516d172): @user_script:80: user_script:80: too many results to unpack ' after processing the command 'evalsha'
4116:S 08 Aug 15:57:04.503 # == CRITICAL == This slave is sending an error to its master: 'Error running script (call to f_d4d1d1b62afa6d576d81cfbecc482ad7e516d172): @user_script:80: user_script:80: too many results to unpack ' after processing the command 'evalsha'
4116:signal-handler (1533743958) Received SIGTERM scheduling shutdown...
4116:signal-handler (1533743958) Received SIGTERM scheduling shutdown...
4116:signal-handler (1533743959) Received SIGTERM scheduling shutdown...
4116:signal-handler (1533743960) Received SIGTERM scheduling shutdown...
4116:signal-handler (1533743961) Received SIGTERM scheduling shutdown...
4116:signal-handler (1533743962) Received SIGTERM scheduling shutdown...
4116:signal-handler (1533743963) Received SIGTERM scheduling shutdown...
4116:signal-handler (1533743964) Received SIGTERM scheduling shutdown...
4116:signal-handler (1533743965) Received SIGTERM scheduling shutdown...
4116:signal-handler (1533743966) Received SIGTERM scheduling shutdown...
4116:S 08 Aug 16:02:51.103 # == CRITICAL == This slave is sending an error to its master: 'Error running script (call to f_d4d1d1b62afa6d576d81cfbecc482ad7e516d172): @user_script:80: user_script:80: too many results to unpack ' after processing the command 'evalsha'
4116:S 08 Aug 16:05:38.817 # == CRITICAL == This slave is sending an error to its master: 'Error running script (call to f_d4d1d1b62afa6d576d81cfbecc482ad7e516d172): @user_script:80: user_script:80: too many results to unpack ' after processing the command 'evalsha'
```

Apparently the "CRITICAL" errors were present in this database since forever, and were harmless. possibly, a script that's failing on the master's side too, but only after performing some modification, so that redis is forced to replicate it to the slave to fail there too.

The fact that we see CRITICAL log messages after the SIGTERM signal was received, is an indication that the process is not hung in an endless loop, but still processing commands (in a long running loop), but does't (yet) read commands from other clients, or get to serverCron to respond to the shutdown_asap flag.

I sent a SIGSEGV to the slave so that i can get a crash report with stack trace, and this is what i saw:

```
Backtrace:
redis-server redis-2525.conf *:29565(logStackTrace+0x45)[0x476c65]
redis-server redis-2525.conf *:29565(sigsegvHandler+0xbb)[0x47742b]
/lib/x86_64-linux-gnu/libpthread.so.0(+0x11390)[0x7fb9f4432390]
/lib/x86_64-linux-gnu/libc.so.6(+0x14dcde)[0x7fb9f41a4cde]
redis-server redis-2525.conf *:29565(sdsrange+0x187)[0x432947]
redis-server redis-2525.conf *:29565(processMultibulkBuffer+0x473)[0x43bc63]
redis-server redis-2525.conf *:29565(processInputBuffer+0xe6)[0x43d246]
redis-server redis-2525.conf *:29565(processUnblockedClients+0x78)[0x496908]
redis-server redis-2525.conf *:29565(beforeSleep+0xb5)[0x429095]
redis-server redis-2525.conf *:29565(aeMain+0x1e)[0x4247de]
redis-server redis-2525.conf *:29565(main+0x4ca)[0x42131a]
/lib/x86_64-linux-gnu/libc.so.6(__libc_start_main+0xf0)[0x7fb9f4077830]
redis-server redis-2525.conf *:29565(_start+0x29)[0x421599]
```

I do know that processInputBuffer may be inefficient in some cases, imagine a command that takes long time to execute, and during that time, a huge (1gb max, assuming there are no bugs) input buffer is collected, then processInputBuffer trims one command (a few bytes) at a time, memmoving the entire 1gb backwards multiple times. but this does not explain a half hour hung. unless there is some way in which readQueryFromClient can be called from within this loop, and keep feeding the loop.

Theoretically processUnblockedClients should never be executed on slaves, since redis replaces BLPOP with LPOP when it propagates the commands, and obviously all blocking commands are rejected in scripts.
but there's at least one case which still propagates a blocking command to slaves, and this is BRPOPLPUSH, in the case the key existed when the command was executed on the master and it didn't block.

In this case, theoretically, it wouldn't block on the slave side too, but there are cases (e.g. #5171 and others) in which there are data inconsistencies between master and slaves.
so this could explain why we'll have a blocked (and possibly deadlocked) master client... and in case the command was executed with a timeout, we'll also get to processUnblockedClients.

But all of that still doesn't explain why the process will be hang in processInputBuffer for half an hour eating 100% CPU.

if anyone has any idea, let's chat.



## Curated Answers



### High Signal Answer 1

bottom line:
the second fix of #5250 (the one about scripts performing eviction when not in `lua_replicate_commands` mode), together with the fix for BRPOPLPUSH (#5248) seem to explain why we got to `processUnblockedClients` in the slave, and accumulated a large query buffer.

The hung of over 30 minutes feels too much for me for processing 70mb of query buffer (despite the inefficiency that #5244 finally fixes), but i may be wrong, and there may be other slow commands and scripts in that buffer, so it *is* plausible.

I guess we can close this issue and be happy about it (fixing at least 4 different issues).

- Author: oranagra
- Quality score: 5
- URL: https://github.com/redis/redis/issues/5229#issuecomment-413446927
