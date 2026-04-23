# Suggestion: Redis Functions, an extension to Lua scripts



## GitHub Provenance



- Repository: redis/redis

- Issue: #8693

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/8693



## Problem



Edit: implemented in: #9780, #9936, #9938, #10004, #10066, #9899, #9968

The following is a proposal for a new way mechanism to program Redis.

The new mechanism extends the existing Lua scripting approach that assumes scripts are part of the application and are only handed to the server for execution.

With the new approach, scripts are a part of the server. As such they are persistent, replicated, and named. These new scripts are called *Redis Functions*.

We also propose a modular implementation based on engines (languages), to make it easy to support several languages for Redis Functions.

Abstract
========

Today, Lua scripts are considered an extension of the client; they are:

* Not managed by Redis
* By contract, may disappear and need to be re-loaded by the client

This approach greatly simplifies the server side and is proven to be useful in many cases, but it also has several major drawbacks:

* Scripts cannot be considered a way to extend Redis, like stored procedures
* Clients can either use `EVAL` only (inefficient), or implement a more complex logic of trying `EVALSHA` and falling back to `EVAL`
* Using `EVALSHA` inside `MULTI` is inherently risky
* Meaningless SHAs are harder to identify and debug, e.g. in a `MONITOR` session
* `EVAL` inadvertently promotes the wrong pattern of rendering scripts on the client side instead of using `KEYS` and `ARGV`. 

These led to the following definition of *Redis Functions*.

The proposed *Redis Functions* are an evolution of Redis' scripts. They provide the same core functionality, but they are guaranteed to be persistent and replicated, so the user does not need to worry about them being missing.

Conceptually, if current scripts are treated as client code that runs on the server, then functions are extensions to the server logic that can be implemented by the user.

This new design also attempts to decouple the language in which functions are written. Lua is simple and easy to learn, but for many users it’s still an obstacle.

The design makes no assumptions about the programming language in which functions are implemented. Instead, we define an *engine* component that is responsible for executing functions. Engines can execute functions in any language as long as they respect certain rules like memory limits and the ability to kill a function's execution (the full list of engine capabilities will be covered in detail).

Naturally, the first engine that will be implemented is the Lua 5.1 engine, but we propose additional engines to support other languages such as JavaScript.

Important: As with the current scripting approach, functions are atomic. During function execution, Redis is blocked and doesn't accept any commands. This implies that functions are intended for short execution times, and not long running operations, just like Lua scripts today.

Function Life Cycle
====================

A function needs to be created and named in Redis before it can be used.

To do this, the `FUNCTION CREATE` command is used. Function code is loaded into the specified engine that compiles and stores it.

After the function is created, it can be invoked using `FUNCTION CALL` command that executes the named function.

Created functions are also propagated to replicas and AOF, and are saved as part of the RDB file.

Function Engines
================

As mentioned above, the engine is the component that is responsible for executing functions.

We propose to support multiple engines in the same Redis process, in order to support multiple function programming languages. 

Function Commands
=================

INFO functions
--------------

A new proposed `INFO functions` section will be added to the `INFO` command. The section will show general information about the engines and functions.

Information about the engines will include the following:

* Engine name
* Used Memory
* Max Memory
* Function count
* Information about the functions
* Total number of functions

FUNCTION CREATE
---------------

Usage: FUNCTION CREATE `ENGINE` `NAME` `[REPLACE]` `[ARGS_DESCRIPTOR <ARGS DESCRIPTOR>]` `[DESC <DESCRIPTION>]` <BLOB>

* `ENGINE` - The name of the engine to use to create the script.
* `NAME` - the name of the function that can be used later to call the function using `FUNCTION CALL` command.
* `REPLACE` - if given, replace the given function with existing function (if exists).
* `ARGS DESCRIPTOR` - an optional argument that can be given for argument validation on run time, see [Arguments Descriptor](#arguments-descriptor).
* `DESCRIPTION` - optional argument describing the function and what it does
* `BLOB` - A blob of data representing the function, usually it will be text (e.g., Lua code).

The command will return `OK` if created successfully or error in the following cases:
* The given engine name does not exists
* The function name is already taken and `REPLACE` was not used.
* The given function failed to be created by the engine. In this case the engine should return a more precise error and this error will be returned as well.


FUNCTION CALL
-------------

Usage: FUNCTION CALL `NAME` `NUM_KEYS key1 key2` … `ARGS arg1 arg2`

Call and execute the function specified by `NAME`. The function will receive all arguments given after `NUM_KEYS`. The return value from the function will be returned to the user as a result.

* `NAME` - Name of the function to run.
* The rest is as today with EVALSHA command.

The command will return an error in the following cases:
* `NAME` does not exists
* Function was loaded with a costume `ARGS DESCRIPTOR` and the given arguments (keys or args) are not matching the descriptor.
* The function itself returned an error.


FUNCTION DELETE
---------------

Usage: FUNCTION DELETE `NAME`

Delete a function identified by `NAME`. Return `OK` on success or error on one of the following:
* The given function does not exists


FUNCTION INFO
-------------

Usage: FUNCTION INFO `NAME`

List information about the functions.

If the `NAME` argument is not specified, all the functions will be listed with some shallow and general information about each function.

If the `NAME` argument was specified then detailed information about this function will be provided. An error is returned if the function does not exist.

Information about the function will include the following:
* Function name
* Engine name
* Run count(how many times it run)
* Total runtime
* Description (if given on FUNCTION LOAD command)
* Args descriptor (if given on FUNCTION LOAD command)


FUNCTION KILL
-------------

Usage: `FUNCTION KILL`

Kill the currently executing function. The command will fail if the function already initiated a write command or if the engine does not support stopping a function at runtime.


Other Issues
============

Nested Function Calls
---------------------

Redis Functions cannot be nested, i.e. it is not possible to perform a `FUNCTION CALL` command before the previous `FUNCTION CALL` has completed.


Debugging
---------

Redis Functions will not provide server-side debugging capabilities.

Development and debugging should be done outside the server, and function engines should provide a way to do that seamlessly.

Loading Function On Start
-------------------------

Created functions are persisted in RDB and AOF and will therefore be available after a restart. We propose an additional mechanism to preload functions from files at start time, to support two more scenarios:

* Servers configured with no persistence
* Making sure certain functions are immediately available when bootstrapping a new instance


Open Issues
===========

Arguments Descriptor
--------------------

Considering Redis Functions are a type of API, being able to describe the expected arguments serves several purposes:

* Document the interface, to make it more accessible
* Allow a built-in validation that is independent of the function implementation.


Sharing Functions
-----------------

We would like to allow some level of code reuse between functions, or the ability to create "libraries" that define code that is accessible from different functions.



## Curated Answers



### High Signal Answer 1

Hey @zuiderkwast It wasn't fake at all! But it's not my work - an early version prototyped by @MeirShpilraien. I hope he'll have something stable enough to PR sooner than later.

These are all good questions, I think we'll need to come up with the answers here as this is all still work in progress. These are my thoughts for now:
* Bundling engines with Redis - the main benefit is to have them available as a core capability and easily accessible to users. But at the same time we'd really want to avoid bloat, so I think we'll need to come up with some middle way.
* Theoretically it could be a way to support multiple Lua versions, we did some experiments and saw we can get around some issues and concurrently link different Lua versions.

- Author: yossigo
- Quality score: 4
- URL: https://github.com/redis/redis/issues/8693#issuecomment-824202939

### High Signal Answer 2

@madolson Yes this is definitely something to consider. We briefly mentioned 1st party modules in the past but never had a proper discussion nor a decision, I'll open an issue about that.

- Author: yossigo
- Quality score: 4
- URL: https://github.com/redis/redis/issues/8693#issuecomment-828418652
