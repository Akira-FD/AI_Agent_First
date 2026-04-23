# New scheduler priority for real load average and free memory



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #73269

- State: closed

- Labels: sig/scheduling, sig/node, kind/feature, lifecycle/rotten

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/73269



## Problem



**What would you like to be added**:
Kubelet should update node's status.loadavg and status.freeMemory on each heartbeat.
`loadavg` should be a map taken from /proc/loadavg.
`freeMemory` should be calculated as `free + buffers + cache` from /proc/meminfo, see `man 1 free`.

Scheduler should be extended with two more PriorityMaps: `loadAverage` and `freeMemory`.


**Why is this needed**:

Every kubernetes newby sooner or later gets frustrated with the fact that pods are _not_ distributed over cluster according to real-time node utilization.

Instead, _all_ containers spec must be extended with _static_ requests.memory and requests.cpu in order to improve pod scheduling decisions and prevent a "noizy neighbour" problem. What a hacky and tedious task, especially thinking of how far from reality all those requests values may be!

As of now, kube-scheduler decides on which node a new pod should be started based on [priorities](https://github.com/kubernetes/kubernetes/tree/master/pkg/scheduler/algorithm/priorities). The `kube-scheduler --policy-config-file` argument points to a json config listing weights of those priorityMaps.

Unfortunately, none of those priorityMaps have anything to do with real CPU and memory usage. Disk latency is not considered either. All scheduling decisions are based on static node info and the previous schedulings.

In reality, node resources may be well below of what is written by kubelet into `status.allocatable`, such as in case of kernel memory leak or some system daemon going crazy.

Also, a k8s user may write too small `requests.cpu` and `requests.memory` pod specs or not write them at all.

Any of those issues may lead to kernel OOM and extremely high `load average`. But scheduler will never know about such bad condition of a node unless kubelet sends heartbeats.  [Descheduler](https://github.com/kubernetes-incubator/descheduler) would not help wither, as it depends on good kube-scheduler knowledge.

Use of `loadavg` value for scheduling priority may be good enough to avoid scheduling on a node running out of free CPU, memory or disk throughput.

Adding a second scheduler priority based on amount of actual "free+cached" memory will improve scheduling decisions further.



## Curated Answers



### High Signal Answer 1

@kabakaev @unixfox The "Real Load Aware Scheduling" plugin may help you:

- KEP: https://github.com/kubernetes-sigs/scheduler-plugins/tree/6b7e77af527d8db82afb5060e5474ed524bdc0d6/kep/61-Trimaran-real-load-aware-scheduling

- PR: https://github.com/kubernetes-sigs/scheduler-plugins/pull/115

- Author: warmchang
- Quality score: 5
- URL: https://github.com/kubernetes/kubernetes/issues/73269#issuecomment-766315232
