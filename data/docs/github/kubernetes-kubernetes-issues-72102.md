# kube-apiserver 1.13.x refuses to work when first etcd-server is not available.



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #72102

- State: closed

- Labels: kind/bug, priority/critical-urgent, sig/api-machinery, sig/cluster-lifecycle, lifecycle/frozen

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/72102



## Problem



**How to reproduce the problem**:
Set up a new demo cluster with kubeadm 1.13.1.
Create default configurationwith `kubeadm config print init-defaults`
Initialize cluster as usual with `kubeadm init`

Change the `--etcd-servers` list in kube-apiserver manifest to `--etcd-servers=https://127.0.0.2:2379,https://127.0.0.1:2379`, so that the first etcd node is unavailable ("connection refused").

The kube-apiserver is then not able to connect to etcd any more.

Last message: `Unable to create storage backend: config (\u0026{ /registry [https://127.0.0.2:2379 https://127.0.0.1:2379] /etc/kubernetes/pki/apiserver-etcd-client.key /etc/kubernetes/pki/apiserver-etcd-client.crt /etc/kubernetes/pki/etcd/ca.crt true 0xc000381dd0 \u003cnil\u003e 5m0s 1m0s}), err (dial tcp 127.0.0.2:2379: connect: connection refused)\n","stream":"stderr","time":"2018-12-17T12:13:19.608822816Z"}`

kube-apiserver does not start.

If I upgrade etcd to version 3.3.10, it reports an error `remote error: tls: bad certificate", ServerName ""`

**Environment**:
- Kubernetes version 1.13.1
- kubeadm in Vagrant box

I also experience this bug in an environment with a real etcd cluster.

<!-- DO NOT EDIT BELOW THIS LINE -->
/kind bug



## Curated Answers



### High Signal Answer 1

@timothysc I just came back from trip. Will start working on this from this week! And post updates here.

- Author: gyuho
- Quality score: 11
- URL: https://github.com/kubernetes/kubernetes/issues/72102#issuecomment-509380849

### High Signal Answer 2

We have 3 master and 3 etcdservers, a workaround is to change the order of etcdservers.
**master0:**
```
--etcd-servers=etcd0,etcd1,etcd2
```
**master1:**
```
--etcd-servers=etcd1,etcd0,etcd2
```
**master2:**
```
--etcd-servers=etcd2,etcd0,etcd1
```

- Author: niuqg
- Quality score: 10
- URL: https://github.com/kubernetes/kubernetes/issues/72102#issuecomment-478834647

### High Signal Answer 3

I was able to repro this issue with the repro steps provided by @Cytrian. I also reproduced this issue with a real etcd cluster.

As @JishanXing previously mentioned, the problem is caused by a bug in the etcd v3 client library (or perhaps the grpc library). The vault project is also running into this: https://github.com/hashicorp/vault/issues/4349

The problem seems to be that the etcd library uses the first node’s address as the `ServerName` for TLS. This means that all attempts to connect to any server other than the first will fail with a certificate validation error (i.e. cert has `${nameOfNode2}` in SANs, but the client is expecting `${nameOfNode1}`).

An important thing to highlight is that when the first etcd server goes down, it also takes the Kubernetes API servers down, because they fail to connect to the remaining etcd servers.

With that said, this all depends on what your etcd server certificates look like:
* If you follow the [kubeadm instructions](https://kubernetes.io/docs/setup/independent/setup-ha-etcd-with-kubeadm/) to stand up a 3 node etcd cluster, you get a set of certificates that include the first node’s name and IP in the SANs (because all certs are generated on the first etcd node). Thus, you should not run into this issue.
* If you have used another process to generate certificates for etcd, and the certs do not include the first node’s name and IP in the SANs, you will most likely run into this issue when the first etcd node goes down.

**To reproduce the issue with a real etcd cluster:**
1. Create a 3 node etcd cluster with TLS enabled. Each certificate should only contain the name/IP of the node that will be serving it.
2. Start an API server that points to the etcd cluster.
3. Stop the first etcd node.
4. API server crashes and fails to come back up

**Versions:**
- kubeadm version: v1.13.2
- kubernetes api server version: v1.13.2
- etcd image: k8s.gcr.io/etcd:3.2.24

API server crash log: https://gist.github.com/alexbrand/ba86f506e4278ed2ada4504ab44b525b

I was unable to reproduce this issue with API server v1.12.5 (n.b. this was somewhat of a non-scientific test => tested by updating the image field of the API server static pod produced by kubeadm v1.13.2)

- Author: alexbrand
- Quality score: 9
- URL: https://github.com/kubernetes/kubernetes/issues/72102#issuecomment-460303835
