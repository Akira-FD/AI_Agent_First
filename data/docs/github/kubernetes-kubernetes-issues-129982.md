# Excessive conntrack cleanup causes high memory (12GB) and CPU usage when any Pod with a UDP port changes



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #129982

- State: closed

- Labels: kind/bug, priority/critical-urgent, sig/network, triage/accepted

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/129982



## Problem



### What happened?

We are encountering a severe performance issue in kube-proxy (v1.32) when any Pod with a UDP port is updated (e.g., CoreDNS). In the new kube-proxy implementation, changes to Services or Pods that expose UDP ports trigger a full conntrack cleanup. This cleanup process iterates over the entire conntrack table, leading to extremely high resource consumption—sometimes up to 12 GB of memory and 1.5 CPU cores per kube-proxy instance.

In a simple test, we observed 2,780 instances of the log message "Adding conntrack filter for cleanup", which caused an OOM when kube-proxy was limited to 256 MB of memory. Without that limit, kube-proxy memory usage spiked to 12 GB. On nodes with large conntrack tables, kube-proxy effectively becomes stuck, consuming all available memory each time there is a UDP endpoint change.

This issue appears to be systemic; every change in a Pod with a UDP port triggers all kube-proxy instances to perform the extensive cleanup. Currently, there is no option to disable or throttle this behavior, which disrupts cluster stability and can lead to service degradation or outages. We request that the cleanup logic be revised to target only the relevant conntrack entries or that a mechanism be provided to disable or limit this aggressive cleanup behavior.


https://github.com/kubernetes/kubernetes/pull/127318
https://github.com/kubernetes/kubernetes/issues/126130

### What did you expect to happen?

We expected kube-proxy to handle conntrack cleanup in a more efficient and targeted way. Even if it needs to scan a significant portion of the conntrack table, it should do so without causing a spike to 12 GB of memory usage. Ideally, it would either:

- Limit its cleanup to entries relevant to the specific changed UDP endpoint.
- Provide a way to configure or disable this aggressive cleanup process so it does not risk out-of-memory (OOM) events or excessively high CPU usage.

### How can we reproduce it (as minimally and precisely as possible)?

- Deploy multiple Pods that generate a high volume of DNS requests, for example:
- A simple Golang application making repeated DNS lookups without any caching mechanism.
- Observe kube-proxy resource usage (memory and CPU) on that node.
- Delete or update the coredns Pod (which also uses UDP DNS).
- Watch the logs and resource usage of kube-proxy closely, noting the surge in memory (potentially up to 12 GB) and CPU usage as it performs the conntrack cleanup.

### Anything else we need to know?

![Image](https://github.com/user-attachments/assets/f75f0bc0-e394-45fa-b323-2f6fc0570386)

<img width="1708" alt="Image" src="https://github.com/user-attachments/assets/a4ff03e2-156c-4b60-bf87-7caf53859e51" />

<img width="1679" alt="Image" src="https://github.com/user-attachments/assets/81b4bea7-5cf6-498e-9cd4-ec807f267912" />

### Kubernetes version

<details>

```console
$ kubectl version
Client Version: v1.31.2
Kustomize Version: v5.4.2
Server Version: v1.32.0-eks-5ca49cb
```

</details>


### Cloud provider

<details>
AWS
</details>


### OS version

<details>

```console
# On Linux: Amazon Linux 2
5.10.230-223.885.amzn2.aarch64

```

</details>


### Install tools

<details>
EKS
</details>


### Container runtime (CRI) and version (if applicable)

<details>
containerd://1.7.23
</details>


### Related plugins (CNI, CSI, ...) and versions (if applicable)

<details>
kube-proxy:v1.32.0-minimal-eksbuild.2
</details>



## Curated Answers



### High Signal Answer 1

I tried to reproduce this locally with profiling enabled and found 
https://github.com/vishvananda/netlink/blob/b1ce50cfa9bea7652382b8c5ef6083f8d3f5f853/conntrack_linux.go#L175 to be the root cause of the memory spike. 

In **vishvananda/netlink** all the flow entries for which delete call fails are collected in an array, and bloating of this array is causing the memory spikes.



![Image](https://github.com/user-attachments/assets/3273afc8-025a-4cb9-9b82-dde012b24b60)

/triage accepted
/assign

[EDIT]

I introduced that change in **vishvananda/netlink** with the intention of collecting and aggregating all error messages.
https://github.com/vishvananda/netlink/pull/1014

- Author: aroradaman
- Quality score: 8
- URL: https://github.com/kubernetes/kubernetes/issues/129982#issuecomment-2637019593

### High Signal Answer 2

> K3s (and RKE2 under some configurations) make extensive use of LoadBalancer services where the LB IP is the Node IP or ExternalIP. Anything that continues to cause problems in this configuration wouldn't be great for us.

Nothing can keep causing problems in any configuration, we need to fix all the problems, the question is what solution do we use for it.
I'm happy that I could easily reproduce the bug so I'm confident on the fix https://github.com/kubernetes/kubernetes/pull/130484, we will not need revert the reconciler in 1.33.

For 1.32 we can backport the fix or revert the reconciler (the reconciler fixed 2 long standing bugs related to udp), at the beginning I was not even thinking in a backport, after this was a second bug, but now after checking the fix and that the first bug was in the library not in the logic, and there is no functional regression, I think is a possibility the backport https://github.com/kubernetes/kubernetes/pull/130505

- Author: aojea
- Quality score: 4
- URL: https://github.com/kubernetes/kubernetes/issues/129982#issuecomment-2691663000
