# Changing Redis master-slave replication terms with something else



## GitHub Provenance



- Repository: redis/redis

- Issue: #5335

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/5335



## Problem



(Note: I'll update the description here as the discussion evolves)

## Background

It was asked multiple times by activists in the area of inclusiveness for Redis to migrate to a different terminology than *master-slave*, specifically one that has no reference to slavery. Personally I [do not consider the effort worthwhile](http://antirez.com/news/122), but this is my personal opinion. On the other hand different Twitter threads, especially an exchange with DHH, together with many accounts of people starting to suggest to never use Redis again, made me reflecting about a few things. Specifically I think that it could be a problem for engineers just willing to use Redis because they believe is the right too for the job, to apply it in certain workplaces, because the terminology used in Redis may be a problem. I don't want, as a result of my ideas, to create problems to the Redis community.

At the same time once I started to be more open to the possibility of renaming such terms, I started to receive private complains from *multiple* people that contribute to the project for years, that are annoyed by the fact we'll have to do work that will not change the system in any way, and that will be costly, create compatibility issues.

My idea is to find a middle ground between all those things, because there are multiple issues caused by the change of terminology:

* PRs will no longer apply.
* We have commands such as `INFO` and `ROLE` that reply with protocol containing the *slave* term.
* There are 1500 occurrences inside the source code of the term *slave*.
* People having private trees and merging things as needed will get a lot of problems.

So this change can potentially create a lot of issues. Moreover many folks on Twitter do not understand the Redis culture of backward compatibility. Redis 5 that is now release candidate is backward compatible with the *first stable version of Redis released*, to the point it's a drop in replacement. This culture traditionally made sure that upgrade operations are simple, there is no useless work to do in the client side, and so forth. This is something big to consider.

## Possible soltuion

Yet I want to give a signal, because in a [Twitter pool I started](https://twitter.com/antirez/status/1038094104129937408) too many people asked for the terminology to be changed. While I handle the Redis community, I do not want to be its *king*, I need to serve people here. A signal however does not need to create a number of problems across the community, so this is what I propose to do.

### Short term changes

To start we do the following:

1. Change the documentation to refer to master-replica. If we take master, which should not offend anybody in 2018 (next year we'll see...), at least there are less things to change. Replicas is very used and is also used inside Redis Cluster already.
2. Alias SLAVEOF to REPLICAOF. You can still use SLAVEOF but now there is an option.
3. Refer to REPLICAOF inside the documentation.
4. Change the configuration directive as well from `slaveof` to `replicaof`.
5. Leave all the internals as they are mentioning still slave at source level as a first step. Changing all those things now would be a big issue because we are at release candidate state, and there are too many pending PRs.
6. Continue to reply with `slave` to INFO and ROLE, because this is a major breakage, for now.

## Long term changes

1. At some point in the future, write an alternative to INFO, since anyway INFO is not the future of Redis data gathering... It's too limited, provides too many info at once, clients need to have to parse it. We'll design a new command, and in the new command we'll not refer to slaves, but to replicas.
2. When we are going to break a lot of things anyway, like for example with the inclusion of RESPv3, also change the `ROLE` command to output replica instead of slave. If clients detect it's a RESPv3 server, they now that ROLE will reply differently, that is, instead of "slave" it will reply with "replica".
3. The first thing that we'll have to replace a lot of things internally, because of some technical reason, so that many PRs will not apply anyway, switch the variable and function names as well. However **this is not acceptable to do as a change out of context**, because it will cause really a lot of problems. We have to put this inside a much larger change somewhere.

We'll provide no ETA for the second step, and I hope the community will understand our technical issues here. However I hope that people will appreciate that at least somebody is listening here. Certain people demanding this change are vocal and hostile, but I saw a huge amount of people on Twitter just asking peacefully to see some improvement. One thing is for sure: the master-slave terminology is not going to be used in the future, so let's make this change together, and move forward to our actual work, that is, to make Redis better and available.

## Please provide your POV if you are among the contributors of Redis

I know this may seem gross, but I would like most comments here to be provided by people that did something in Redis-land in the latest few years. People sending PRs, opening issues, writing a client library, using Redis at scale and provided hints regularly, and so forth, don't just comment if you are a casual Github user jumping here to say "change it!" or "don't change it". This will just create noise. Thanks.

**Off topic and offensive comments will be removed**



## Curated Answers



### High Signal Answer 1

Since when did programming start to bow the whims of SJWs?  Master/slave in the programming world has no ties to anything in human history related to human master/slave relationships.  Simply because there is a negative connotation to the application of master/slave terms to humans does not mean the same thing applies to other domains.  These are redis instances for crying out loud.

I definitely agree with @zhujinhe that if someone is so deeply offended by these words that they can't make the disconnect between modern programming and human history, they can start a fork of the project to suffice their needs.  Lets focus on actual bug fixes and making the application work better instead of coddling the feelings of a small percentage of people.

- Author: badloop
- Quality score: 178
- URL: https://github.com/redis/redis/issues/5335#issuecomment-419715240

### High Signal Answer 2

I (probably other people also) have some scripts that reference the 'master/slave' keywords. My suggestion is that anyone who is not happy with these terms can fork this project, change the terms whatever they like and leave the master/slave keywords of this project alone.

- Author: zhujinhe
- Quality score: 95
- URL: https://github.com/redis/redis/issues/5335#issuecomment-419713269

### High Signal Answer 3

> I don’t believe that terminology out of context is offensive

especially if the context is the software

**how much it will costs this change** ?  for the sake of ?

kindly suggest you to act like a benevolent dictator (here we are again), so please consider my words in the software context

i strongly think that "time" should be spent in a more usefull way

my 2eurocent,


p.s.
it seems that nowadays you cannot even use the  name of some acient egypt gods to mark  the intern codename relaeses like as has been done already for several years...

- Author: alikon
- Quality score: 72
- URL: https://github.com/redis/redis/issues/5335#issuecomment-419701326
