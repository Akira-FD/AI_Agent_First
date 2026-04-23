# Kubelet/Kubernetes should work with Swap Enabled



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #53533

- State: closed

- Labels: sig/node, kind/feature, triage/accepted

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/53533



## Problem



<!-- This form is for bug reports and feature requests ONLY! 

If you're looking for help check [Stack Overflow](https://stackoverflow.com/questions/tagged/kubernetes) and the [troubleshooting guide](https://kubernetes.io/docs/tasks/debug-application-cluster/troubleshooting/).
-->

**Is this a BUG REPORT or FEATURE REQUEST?**:

> Uncomment only one, leave it on its own line: 
>
/kind bug
> /kind feature


**What happened**:

Kubelet/Kubernetes 1.8 does not work with Swap enabled on Linux Machines.

I have found this original issue https://github.com/kubernetes/kubernetes/issues/31676
This PR https://github.com/kubernetes/kubernetes/pull/31996 
and last change which enabled it by default https://github.com/kubernetes/kubernetes/commit/71e8c8eba43a0fade6e4edfc739b331ba3cc658a

If Kubernetes does not know how to handle memory eviction when Swap is enabled - it should find a way how to do that, but not asking to get rid of swap.

Please follow kernel.org [Chapter 11  Swap Management](https://www.kernel.org/doc/gorman/html/understand/understand014.html), for example

> The casual reader may think that with a sufficient amount of memory, swap is unnecessary but this brings us to the second reason. A significant number of the pages referenced by a process early in its life may only be used for initialisation and then never used again. It is better to swap out those pages and create more disk buffers than leave them resident and unused.

In case of running a lot of node/java applications I have seen always a lot of pages are swapped, just because they aren't used anymore.

**What you expected to happen**:

Kubelet/Kubernetes should work with Swap enabled. I believe instead of disabling swap and giving users no choices kubernetes should support more use cases and various workloads, some of them can be an applications which might rely on caches.

I am not sure how kubernetes decided what to kill with memory eviction, but considering that Linux has this capability, maybe it should align with how Linux does that? https://www.kernel.org/doc/gorman/html/understand/understand016.html

I would suggest to rollback the change for failing when swap is enabled, and revisit how the memory eviction works currently in kubernetes. Swap can be important for some workloads. 

**How to reproduce it (as minimally and precisely as possible)**:

Run kubernetes/kublet with default settings on linux box

**Anything else we need to know?**:

**Environment**:
- Kubernetes version (use `kubectl version`):
- Cloud provider or hardware configuration**:
- OS (e.g. from /etc/os-release):
- Kernel (e.g. `uname -a`):
- Install tools:
- Others:

/sig node
cc @mtaufen @vishh @derekwaynecarr @dims



## Curated Answers



### High Signal Answer 1

Not supporting swap as a default?  I was surprised to hear this -- I thought Kubernetes was ready for the prime time?  Swap is one of those features.

This is not really optional in most open use cases -- it is how the Unix ecosystem is designed to run, with the VMM switching out inactive pages.

If the choice is no swap or no memory limits, I'll choose to keep swap any day, and just spin up more hosts when I start paging, and I will still come out saving money.

Can somebody clarify -- is the problem with memory eviction only a problem if you are using memory limits in the pod definition, but otherwise, it is okay?

It'd be nice to work in a world where I have control over the way an application memory works so I don't have to worry about poor memory usage, but most applications have plenty of inactive memory space.   

I honestly think this recent move to run servers without swap is driven by the PaaS providers trying to coerce people into larger memory instances--while disregarding ~40 years of memory management design. The reality is that the kernel is really good about knowing what memory pages are active or not--let it do its job.

- Author: srevenant
- Quality score: 321
- URL: https://github.com/kubernetes/kubernetes/issues/53533#issuecomment-378107519

### High Signal Answer 2

This is critical use case for us too. We have a cron job that occasionally runs into high memory usage (>30GB) and we don't want to permanently allocate 40+GB nodes. Also, given that we run in three zones (GKE), this will allocate 3 such machines (1 in each zone). And this configuration has to be repeated in 3+ production instances and 10+ test instances making this super expensive to use K8s.  We are forced to have 25+ 48GB nodes which incurs huge cost!.
Please enable swap!.

- Author: fieryorc
- Quality score: 105
- URL: https://github.com/kubernetes/kubernetes/issues/53533#issuecomment-354832960

### High Signal Answer 3

> Can you provide some reference for this so that I could educate myself?

Like all modern virtual memory OSes, Linux demand pages executables from disk into memory.  Under memory pressure, the kernel swaps **the actual executable code of your program to/from disk** just like any other memory pages (the "swap out" is simply a discard because read-only, but the mechanism is the same), and they will be re-fetched if required again.  Same goes for things like string constants, which are typically mmapped read-only from other sections of the executable file. Other mmapped files (common for database-type workloads) are also swapped in+out to their relevant backing files (requiring an actual write-out if they've been modified) in response to memory pressure.  **The _only_ swapping you disable by "disabling swap" is "anonymous memory"** - memory that is _not_ associated with a file (the best examples are the "stack" and "heap" data structures).

There are lots of details I'm skipping over in the above description of course.  In particular, executables can "lock" portions of their memory space into ram using the `mlock` family of syscalls, do clever things via `madvise()`, it gets complicated when the same pages are shared by multiple processes (eg libc.so), etc.  I'm afraid I don't have a more useful pointer to read more other than those manpages, or general things like textbooks or linux kernel source/docs/mailing-list.

So, a practical effect of the above is that as your process gets close to its memory limit, the kernel will be forced to evict _code_ portions and constants from ram.  The next time that bit of code or constant value is required, the program will pause, waiting to fetch it back from disk (and evict something else).  So even with "swap disabled", you still get the same degradation when your working set exceeds available memory.

Before people read the above and start calling to mlock everything into memory or copy everything into a ramdrive as part of the anti-swap witch hunt, I'd like to repeat that the real resource of interest here is **working set size - not total size**.  A program that works linearly through gigabytes of data in ram might only work on a narrow window of that data at a time.  This hypothetical program would work just fine with a large amount of swap and a small ram limit - and it would be terribly inefficient to lock it all into real ram.  As you've learned from the above explanation, this is exactly the same as a program that has a large amount of _code_ but only executes a small amount of it at any particular moment.

My latest personal real-world example of something like that is linking the kubernetes executables.  I'm currently (ironically) unable to compile kubernetes on my kubernetes cluster because the go link stage requires several gigabytes of (anonymous) virtual memory, even though the working set is much smaller.

To really belabour the "its about working set, not virtual memory" point, consider a program that does lots of regular file I/O and nothing to do with mmap.  If you have sufficient ram, the kernel will cache repeatedly-used directory structures and file data in ram and avoid going to disk, and it will allow writes to burst into ram temporarily to optimise disk write-out.  Even a "naive" program like this will degrade from ram-speeds to disk-speeds depending on working set size vs available ram.  When you pin something into ram unnecessarily (eg: using mlock or disabling swap), you prevent the kernel from using that page of physical ram for something actually useful and (if you didn't have enough ram for working set) you've just moved the disk I/O to somewhere even more expensive.

@superdave: I too am interested in improving the status-quo here.  Please include me if you want another pair of eyes to review a doc, or hands at a keyboard.

- Author: anguslees
- Quality score: 51
- URL: https://github.com/kubernetes/kubernetes/issues/53533#issuecomment-427233471
