# Kubernetes pod resource utilization metrics need better documentation



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #70179

- State: closed

- Labels: kind/documentation, sig/node, lifecycle/stale

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/70179



## Problem



<!-- This form is for bug reports and feature requests ONLY!

If you're looking for help check [Stack Overflow](https://stackoverflow.com/questions/tagged/kubernetes) and the [troubleshooting guide](https://kubernetes.io/docs/tasks/debug-application-cluster/troubleshooting/).

If the matter is security related, please disclose it privately via https://kubernetes.io/security/.
-->

**Is this a BUG REPORT or FEATURE REQUEST?**:

> Uncomment only one, leave it on its own line:
>
> /kind bug
<!-- > /kind feature-->


**What happened**:
I have a Kubernetes Pod that has 

* Requested Memory of 1500Mb
* Memory Limit of 2048Mb

I have 2 containers running inside this pod, one is the actual application (heavy Java app) and a lightweight log shipper.

The pod consistently reports a usage of 1.9-2Gb of memory usage. Because of this, the deployment is scaled (an autoscaling configuration is set which scales pods if memory consumption > 80%), naturally resulting in more pods and more costs

**Yellow Line represents application memory usage**

[![enter image description here][1]][1]


However, on deeper investigation, this is what I found.

On `exec`ing inside the application container, I ran the `top` command, and it reports a total of `16431508 KiB` or roughly 16Gb of memory available, which is the memory available on the Machine.

There are 3 processes running inside the application container, out of which the root process (application) takes *5.9%* of memory, which roughly comes out to 0.92Gb.

The log-shipper simply takes 6Mb of memory.

Now, what I don't understand is *WHY* my pod consistently reports such high usage metrics. Am I missing something ? We're incurring significant costs due to the unintended auto-scaling and would like to fix the same.


  [1]: https://i.stack.imgur.com/K3vpL.png

**What you expected to happen**:
I expect the process memory consumption observed via `top` to be the same as the memory occupied by the pod. That's not happening by a long shot

**How to reproduce it (as minimally and precisely as possible)**:
I'm not sure. Is this a fundamental linux/docker issue..?

**Anything else we need to know?**:

Also put up on stackoverflow - https://stackoverflow.com/questions/52963152/kubernetes-pod-reporting-more-memory-usage-than-actual-process-consumption

**Environment**:
- Kubernetes version (use `kubectl version`): Client Version: version.Info{Major:"1", Minor:"11", GitVersion:"v1.11.3", GitCommit:"a4529464e4629c21224b3d52edfe0ea91b072862", GitTreeState:"clean", BuildDate:"2018-09-10T11:44:36Z", GoVersion:"go1.11", Compiler:"gc", Platform:"darwin/amd64"}
- Cloud provider or hardware configuration: AWS
- OS (e.g. from /etc/os-release): Ubuntu
- Kernel (e.g. `uname -a`):
- Install tools:
- Others:



## Curated Answers



### High Signal Answer 1

In kubernetes cluster, the cadvisor is used for mem metrics, `container_memory_usage_bytes`, and this one includes more than expected. I think this is the cause. 
I have a pod which has 1.05 GB from grafana, but with `kubectl top` only 435MB.
issue is [here](https://github.com/google/cadvisor/issues/2138)

- Author: nobody4t
- Quality score: 6
- URL: https://github.com/kubernetes/kubernetes/issues/70179#issuecomment-590047483
