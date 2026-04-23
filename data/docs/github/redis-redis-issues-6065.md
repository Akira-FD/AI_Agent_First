# Design of new modules API functions: server events and module private data



## GitHub Provenance



- Repository: redis/redis

- Issue: #6065

- State: closed

- Labels: state-design-effort-needed, modules system

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/6065



## Problem



In this issue I'll try to provide a design draft for two features that are very desirable in the modules systems API:

1. An API that allows the module to know about important events that are happening in the server.
2. An API that allows to store into an RDB file, and load back, data which is private to module and has nothing to do with the key space of Redis. Note that this is very different compared to storing module private values as defined by module-exported data types.

## Naming

It is very important for features to have names, otherwise they cannot effectively be communicated among the Redis core community, nor to the users of Redis. We happen to already have APIs doing notifications, for instance:

    RedisModule_SubscribeToKeyspaceEvents()

Fortunately the previous API specifies clearly that we are talking about *keyspace events*, this is surely an advantage in order to pick future good names. I propose the following two names for the two above features:

1. **Server events notifications** API.
2. **RDB modules private data** API.

Note that the second feature is not called *modules aux fields* because it does not use the auxiliary fields inside RDB. Instead the RDB is *already* designed to have module-specific data, even if this feature is not used right now, but only implemented  to the degree that allows it to be future-compatible. The mechanism used is much solid than using AUX fields.

## Server events notifications

Modules will end having a huge number of callbacks they can subscribe to. This is unfortunately but there is no way out: if we want the modules system to be able to do a lot, and at the same time we want Redis to remain simple, we have to provide modules some way to hook into different subsystems. So the temptation of using a single hooking mechanism implementation inside Redis is big. However different hooks and callbacks require different kinds of functions, arguments, opaque structures returned and so for.

However there are many events a module may want to know that is more or less stateless, and that there is nothing the module should be able to do in such context, if not calling the usual APIs. All this cases can be served via a single API, that is indeed, this server events notification API we are going to show here.

There are a number of examples in the following list:

* RDB persistence started
* RDB persistence ended
* AOF persistence started
* AOF persistence ended
* The server is ready for shutdown
* The server just flushed all its data
* A server "tick" elapsed (serverCron() is going to be called)
* A new module was loaded
* A module was unloaded
* The server changed role
* The server got a new replica in online status
* The instance is a replica and the connection with the master is no longer valid

And so forth. All such events should have something in common:

1. They are rarely occurring, so even running the list of currently loaded modules to check if they want such event delivered is not going to be a problem. This is, for instance, why there is no "client disconnected" event in the list above (such feature will be added with a different API for multiple reasons).
2. There is no state to communicate.

This means that the implementation can just be obtained by having a new field in the RedisModule structure itself, with bits set for every different condition. Then a single API inside the core will deliver the messages: such API can run all the modules loaded so far, since, to start, we usually have very few modules loaded, not even in the order of tens often (no latency issues). Secondly because such events are rarely occurring so anyway the time spent in total is small (no big total CPU usage issues).

The above API should be exported to modules with something like that:

    RedisModule_SubscribeToServerEvents(ctx, REDISMODULE_SE_RDB_SAVE_START | REDIS..., myCallBack);

The callback argument may be NULL in order to unsubscribe. Note that in order to subscribe or unsubscribe to multiple events we can just use bitwise OR of the conditions, or multiple calls.

Inside the core a similar function will be called when needed:

   notifyModulesOnServerEvent(REDISMODULE_SE_EMPTYDB);

This will just run the list of modules for matching ones.

**Important**: the module should use a single callback for all the server notifications. Setting a different callback will route *all* the new notifications to the new callback. This should be clearly documented.

## Modules private data (RDB MPD fields)

Modules often have the need to register *substantial* amount of data inside the RDB file. Such data may often be about keys, but they may not necessarily be *about* the key value itself. For instance a module adding expires to Redis hashes may not necessarily want to replace the hash implementation, but instead may want to simply record additional information about each hash key.

Moreover certain times, when the module private data to store inside the RDB is *about* keys that we will load, there are cases where it is a lot more comfortable to store the data before the key itself, so that the callback of the key loaded will be invoked later, after we already loaded our private data, and certain other times we may want to do the reverse, that is, store the data at the end (for instance in the case of the hash fields expires this may make sense), so that we may load the additional module-private data only after the key space is already populated inside Redis.

This need was sensed time ago, so Redis 5 already shipped with the internal RDB modifications to allow for such feature, but without actually implementing it. See the `RDB_OPCODE_MODULE_AUX` opcode inside `rdb.c` for more information.

Now it is time to actually implement this system inside the module system.

This is the proposed API.

1. In order to enable the module private data, the following call should be performed:

    RedisModule_EnableMPD(ctx, load_callback, save_callback);

This function will normally be called from the module initialization function, but the implementation will be better if it can be called at any time. Again by calling the function with both callbacks set to NULL, we can turn off the feature.

The callbacks take a RedisModuleIO handle as usually, however there is another integer argument that is passed to the save() callback, that is called "when", because the callback is called actually in two different contexts:

1. Before the RDB is starting to save keys.
2. After the RDB already saved all the keys.

So the save callback is called also two times with the `when` parameter set to either REDISMODULE_MPD_BEFORE_RDB, REDISMODULE_MPD_AFTER_RDB.

**IMPORTANT:** during a Tel Aviv meeting with my colleagues at Redis Labs we thought that after all there was no need to also call the save callback after each key was persisted, also specifying which key it was. There is to evaluate if we still think likewise. This complicates the implementation and the API but better to be sure than sorry later.

The load callback should probably not need to know if the data is stored before or after, because this should be module-specific and fixed. Moreover Redis has no simple way to know this because of how RDB is structured, and when this is *really* important, the save callback can save as first data an integer with value 0 or 1 (1 byte overhead).

Inside the callbacks, it will be possible to call the usual functions to store data, such as:

    RedisModule_SaveUnsigned)(RedisModuleIO *io, uint64_t value);

And all the other functions of this family. Note that like the module private key values, also the MPD can be parsed with zero knowledge by the rdb-check tool, since each data part is well defined and there is a terminator.

## Feedbacks

Please comment in this issue with feedbacks and use cases, and how your use cases will match or mismatch the proposed API and features.



## Curated Answers



### High Signal Answer 1

good plan, but here are a few quick notes:

i know the notification list is only partial, and you gave some good examples about replica state, but I think these should be added to the list right from the start:
* aof load start / end
* rdb load start / end

I recently said that we may not need these if the MPD is implemented with a different api, but I think, especially about AOF load, the module might wanna know when it's done (maybe trigger some calculation or garbage collection) 

I hate to ruin the nice plan about notification not needing an argument, but I think that:
* flushdb may need to carry dbid and async flag with it (and my be better called before rather than after, or maybe both?) 
* it is useful for cron tick to carry tick count and effective hz with it so modules can implement things similar to the active expire mechanism
* so together with the above, and the client disconnection notifications, maybe we do need to design a way to pass arguments to the callback. 

I think we do still need the key name when loading or saving the key.. think of the hash expiry use case you mentioned. we have a simple piece of code for that which we can PR.

- Author: oranagra
- Quality score: 4
- URL: https://github.com/redis/redis/issues/6065#issuecomment-488766550
