# kube-apiserver log spammed with "failed to connect to etcd"



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #134080

- State: closed

- Labels: kind/bug, sig/api-machinery, help wanted, triage/accepted

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/134080



## Problem



### What happened?

Running 1.34.1 with talos 1.11.0 (etcd 3.6.4). It doesn't seem to be related to talos.

All kube-apiserver logs are spammed every 15sec with
```
grpc: addrConn.createTransport failed to connect to {Addr: "localhost:2379", ServerName: "localhost:2379", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp: lookup localhost: operation was canceled"
```

The cluster is working as expected.

See also https://github.com/siderolabs/talos/issues/11797

### What did you expect to happen?

Not have the log spammed when everything works well.

### How can we reproduce it (as minimally and precisely as possible)?

Deploy a VM with talos 1.11.0 and bootstrap the cluster.

### Anything else we need to know?

_No response_

### Kubernetes version

<details>

```console
❯ k version
Client Version: v1.33.3
Kustomize Version: v5.6.0
Server Version: v1.34.1
```

</details>


### Cloud provider

<details>
Proxmox with Talos
</details>


### OS version

<details>

```console
Talos 1.11.0
```

</details>


### Install tools

<details>

</details>


### Container runtime (CRI) and version (if applicable)

<details>

</details>


### Related plugins (CNI, CSI, ...) and versions (if applicable)

<details>
Cilium 1.18
</details>



## Curated Answers



### High Signal Answer 1

Seeing the same on a cluster with 1.34.1, every 15 seconds. I also haven't observed any issues.

Here with verbose logs:

```
apiserver I0916 13:56:55.132842       1 clientconn.go:857] "[core] [Channel #11940 SubChannel #11941]Subchannel created\n"
apiserver I0916 13:56:55.132917       1 logging.go:39] "[core] [Channel #11940]Resolver state updated: {\n  \"Addresses\": null,\n  \"Endpoints\": [\n    {\n      \"Addresses\": [\n        {\n          \"Addr\": \"etcd-0.etcd.namespace.svc.cluster.local.:2379\",\n          \"ServerName\": \"etcd-0.etcd.namespace.svc.cluster.local.:2379\",\n          \"Attributes\": null,\n          \"BalancerAttributes\": null,\n          \"Metadata\": null\n        }\n      ],\n      \"Attributes\": null\n    },\n    {\n      \"Addresses\": [\n        {\n          \"Addr\": \"etcd-1.etcd.namespace.svc.cluster.local.:2379\",\n          \"ServerName\": \"etcd-1.etcd.namespace.svc.cluster.local.:2379\",\n          \"Attributes\": null,\n          \"BalancerAttributes\": null,\n          \"Metadata\": null\n        }\n      ],\n      \"Attributes\": null\n    },\n    {\n      \"Addresses\": [\n        {\n          \"Addr\": \"etcd-2.etcd.namespace.svc.cluster.local.:2379\",\n          \"ServerName\": \"etcd-2.etcd.namespace.svc.cluster.local.:2379\",\n          \"Attributes\": null,\n          \"BalancerAttributes\": null,\n          \"Metadata\": null\n        }\n      ],\n      \"Attributes\": null\n    }\n  ],\n  \"ServiceConfig\": {\n    \"Config\": {\n      \"Config\": null,\n      \"Methods\": {}\n    },\n    \"Err\": null\n  },\n  \"Attributes\": null\n} (service config updated)\n"
apiserver I0916 13:56:55.132940       1 logging.go:39] "[core] [Channel #11940]Channel switches to new LB policy \"round_robin\"\n"
apiserver I0916 13:56:55.133006       1 logging.go:39] "[core] [Channel #11940 SubChannel #11941]Subchannel Connectivity change to CONNECTING\n"
apiserver I0916 13:56:55.133021       1 clientconn.go:857] "[core] [Channel #11940 SubChannel #11942]Subchannel created\n"
apiserver I0916 13:56:55.133175       1 logging.go:39] "[core] [Channel #11940 SubChannel #11942]Subchannel Connectivity change to CONNECTING\n"
apiserver I0916 13:56:55.133196       1 clientconn.go:857] "[core] [Channel #11940 SubChannel #11943]Subchannel created\n"
apiserver I0916 13:56:55.133136       1 logging.go:39] "[core] [Channel #11940 SubChannel #11941]Subchannel picks a new address \"etcd-0.etcd.namespace.svc.cluster.local.:2379\" to connect\n"
apiserver I0916 13:56:55.133274       1 logging.go:39] "[core] [Channel #11940 SubChannel #11942]Subchannel picks a new address \"etcd-0.etcd.namespace.svc.cluster.local.:2379\" to connect\n"
apiserver I0916 13:56:55.133330       1 logging.go:39] "[core] [Channel #11940 SubChannel #11943]Subchannel Connectivity change to CONNECTING\n"
apiserver I0916 13:56:55.133301       1 clientconn.go:857] "[core] [Channel #11940 SubChannel #11944]Subchannel created\n"
apiserver I0916 13:56:55.133504       1 logging.go:39] "[core] [Channel #11940 SubChannel #11943]Subchannel picks a new address \"etcd-1.etcd.namespace.svc.cluster.local.:2379\" to connect\n"
apiserver I0916 13:56:55.133548       1 clientconn.go:333] "[core] [Channel #11940]Channel exiting idle mode\n"
apiserver I0916 13:56:55.133509       1 logging.go:39] "[core] [Channel #11940 SubChannel #11944]Subchannel Connectivity change to CONNECTING\n"
apiserver I0916 13:56:55.133609       1 logging.go:39] "[core] [Channel #11940 SubChannel #11941]Subchannel Connectivity change to SHUTDOWN\n"
apiserver I0916 13:56:55.133614       1 logging.go:39] "[core] [Channel #11940 SubChannel #11944]Subchannel picks a new address \"etcd-2.etcd.namespace.svc.cluster.local.:2379\" to connect\n"
apiserver I0916 13:56:55.133650       1 clientconn.go:1551] "[core] [Channel #11940 SubChannel #11941]Subchannel deleted\n"
apiserver I0916 13:56:55.133749       1 clientconn.go:1401] "[core] Creating new client transport to \"{Addr: \\\"etcd-0.etcd.namespace.svc.cluster.local.:2379\\\", ServerName: \\\"etcd-0.etcd.namespace.svc.cluster.local.:2379\\\", BalancerAttributes: {\\\"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>\\\": \\\"<%!p(bool=true)>\\\" }}\": connection error: desc = \"transport: Error while dialing: dial tcp: lookup etcd-0.etcd.namespace.svc.cluster.local.: operation was canceled\"\n"
apiserver W0916 13:56:55.133834       1 logging.go:55] [core] [Channel #11940 SubChannel #11941]grpc: addrConn.createTransport failed to connect to {Addr: "etcd-0.etcd.namespace.svc.cluster.local.:2379", ServerName: "etcd-0.etcd.namespace.svc.cluster.local.:2379", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp: lookup etcd-0.etcd.namespace.svc.cluster.local.: operation was canceled"
```

- Author: ovstuckrad
- Quality score: 15
- URL: https://github.com/kubernetes/kubernetes/issues/134080#issuecomment-3298931624

### High Signal Answer 2

I'll give it a try.

/assign

- Author: PatrickLaabs
- Quality score: 5
- URL: https://github.com/kubernetes/kubernetes/issues/134080#issuecomment-3776390238

### High Signal Answer 3

/triage accepted

We can see this in upstream CI logs here:

https://prow.k8s.io/view/gs/kubernetes-ci-logs/logs/ci-kubernetes-gce-conformance-latest-1-34/1970548919561621504

https://storage.googleapis.com/kubernetes-ci-logs/logs/ci-kubernetes-gce-conformance-latest-1-34/1970548919561621504/artifacts/cluster-logs/kt2-3c70e128-76fe-master/kube-apiserver.log

```
W0923 18:07:34.536179      11 logging.go:55] [core] [Channel #13 SubChannel #14]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:2379", ServerName: "127.0.0.1:2379", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:2379: operation was canceled"
W0923 18:07:34.536297      11 logging.go:55] [core] [Channel #13 SubChannel #15]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:2379", ServerName: "127.0.0.1:2379", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:2379: connect: connection refused"
W0923 18:07:35.462312      11 logging.go:55] [core] [Channel #2 SubChannel #6]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:2379", ServerName: "127.0.0.1:2379", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:2379: connect: connection refused"
W0923 18:07:35.462404      11 logging.go:55] [core] [Channel #1 SubChannel #4]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:2379", ServerName: "127.0.0.1:2379", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:2379: connect: connection refused"
W0923 18:07:35.467482      11 logging.go:55] [core] [Channel #7 SubChannel #10]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:4002", ServerName: "127.0.0.1:4002", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:4002: connect: connection refused"
W0923 18:07:35.467571      11 logging.go:55] [core] [Channel #8 SubChannel #12]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:4002", ServerName: "127.0.0.1:4002", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:4002: connect: connection refused"
W0923 18:07:35.538456      11 logging.go:55] [core] [Channel #13 SubChannel #15]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:2379", ServerName: "127.0.0.1:2379", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:2379: connect: connection refused"
W0923 18:07:36.795656      11 logging.go:55] [core] [Channel #7 SubChannel #10]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:4002", ServerName: "127.0.0.1:4002", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:4002: connect: connection refused"
W0923 18:07:36.940809      11 logging.go:55] [core] [Channel #2 SubChannel #6]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:2379", ServerName: "127.0.0.1:2379", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:2379: connect: connection refused"
W0923 18:07:36.978912      11 logging.go:55] [core] [Channel #8 SubChannel #12]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:4002", ServerName: "127.0.0.1:4002", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:4002: connect: connection refused"
W0923 18:07:37.184582      11 logging.go:55] [core] [Channel #1 SubChannel #4]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:2379", ServerName: "127.0.0.1:2379", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:2379: connect: connection refused"
W0923 18:07:37.216093      11 logging.go:55] [core] [Channel #13 SubChannel #15]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:2379", ServerName: "127.0.0.1:2379", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:2379: connect: connection refused"
W0923 18:07:39.044758      11 logging.go:55] [core] [Channel #7 SubChannel #10]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:4002", ServerName: "127.0.0.1:4002", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:4002: connect: connection refused"
W0923 18:07:39.603209      11 logging.go:55] [core] [Channel #2 SubChannel #6]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:2379", ServerName: "127.0.0.1:2379", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:2379: connect: connection refused"
W0923 18:07:39.628435      11 logging.go:55] [core] [Channel #13 SubChannel #15]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:2379", ServerName: "127.0.0.1:2379", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:2379: connect: connection refused"
W0923 18:07:39.628712      11 logging.go:55] [core] [Channel #8 SubChannel #12]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:4002", ServerName: "127.0.0.1:4002", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:4002: connect: connection refused"
W0923 18:07:39.979648      11 logging.go:55] [core] [Channel #1 SubChannel #4]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:2379", ServerName: "127.0.0.1:2379", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:2379: connect: connection refused"
W0923 18:07:42.558121      11 logging.go:55] [core] [Channel #7 SubChannel #10]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:4002", ServerName: "127.0.0.1:4002", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:4002: connect: connection refused"
W0923 18:07:43.033887      11 logging.go:55] [core] [Channel #13 SubChannel #15]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:2379", ServerName: "127.0.0.1:2379", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:2379: connect: connection refused"
W0923 18:07:43.249939      11 logging.go:55] [core] [Channel #8 SubChannel #12]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:4002", ServerName: "127.0.0.1:4002", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:4002: connect: connection refused"
W0923 18:07:43.257412      11 logging.go:55] [core] [Channel #2 SubChannel #6]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:2379", ServerName: "127.0.0.1:2379", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:2379: connect: connection refused"
W0923 18:07:43.653324      11 logging.go:55] [core] [Channel #1 SubChannel #4]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:2379", ServerName: "127.0.0.1:2379", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:2379: connect: connection refused"
W0923 18:07:50.802223      11 logging.go:55] [core] [Channel #20 SubChannel #21]grpc: addrConn.createTransport failed to connect to {Addr: "127.0.0.1:2379", ServerName: "127.0.0.1:2379", BalancerAttributes: {"<%!p(pickfirstleaf.managedByPickfirstKeyType={})>": "<%!p(bool=true)>" }}. Err: connection error: desc = "transport: authentication handshake failed: context canceled"
```

Also on master:
https://prow.k8s.io/view/gs/kubernetes-ci-logs/logs/ci-kubernetes-gce-conformance-latest/1970542879654809600

But in 1.33, it only happens a dozen times or so early in startup and then not for the rest of the logs.

/cc @siyuanfoundation

- Author: BenTheElder
- Quality score: 4
- URL: https://github.com/kubernetes/kubernetes/issues/134080#issuecomment-3325410257
