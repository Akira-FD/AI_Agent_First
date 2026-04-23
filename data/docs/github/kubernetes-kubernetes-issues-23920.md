# HostPort seemingly not working



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #23920

- State: closed

- Labels: sig/network

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/23920



## Problem



I am not sure if what I am doing is supposed to work. But I have created the following pod:

```
apiVersion: v1
kind: Pod
metadata:
  name: nginx-host
spec:
  containers:
  - image: caseydavenport/nginx
    imagePullPolicy: IfNotPresent
    name: nginx-host
    ports:
    - containerPort: 80
      hostPort: 80
  restartPolicy: Always
```

This gives me a pod with the following:

```
        "hostIP": "178.x.x.x",
        "podIP": "10.x.x.x",
```

From the host (178.x.x.x), running: `curl http://10.x.x.x` gets me the response from nginx that I expect.
From the host (178.x.x.x), running `curl http://178.x.x.x` gets me `port 80: Connection refused`.

Should this work? Or have I missed something?

Versions:

```
Client Version: version.Info{Major:"1", Minor:"2", GitVersion:"v1.2.1", GitCommit:"50809107cd47a1f62da362bccefdd9e6f7076145", GitTreeState:"clean"}
Server Version: version.Info{Major:"1", Minor:"2", GitVersion:"v1.2.1", GitCommit:"50809107cd47a1f62da362bccefdd9e6f7076145", GitTreeState:"clean"}
```

Networking: Calico

Host OS: Ubuntu 16.04

Docker: 1.10.3

Thanks a lot



## Curated Answers



### High Signal Answer 1

@thockin @microadam - Correct me if I'm misunderstanding something, but I _think_ that `hostPort` just isn't going to work with CNI based integrations at the moment (I see you're using Calico).

`hostPort` currently relies on Docker to configure the port mapping, but in the CNI case Docker doesn't have the knowledge to do this, since pods are started with `net=none`.

I think this could be resolved by sending hostPort the way of NodePort, and writing the iptables rules from k8s instead of docker.  I don't think the `kube-proxy` watches pods at the moment, so probably not a trivial change.

- Author: caseydavenport
- Quality score: 18
- URL: https://github.com/kubernetes/kubernetes/issues/23920#issuecomment-217048099

### High Signal Answer 2

I have the same issue with kube-registry-proxy on 1.4 bare metal with kube-weave cni.

- Author: ghost
- Quality score: 18
- URL: https://github.com/kubernetes/kubernetes/issues/23920#issuecomment-253592395

### High Signal Answer 3

We've also seen this issue with Deis. We use a hostPort with a container called [registry-proxy](https://github.com/deis/registry-proxy) to bypass the Docker `--insecure-registry` requirement for internal networks. We've seen this occur only on CoreOS-specific installations such as with [kube-aws](https://github.com/coreos/coreos-kubernetes). Vagrant (Fedora), GKE (Debian), AWS (Ubuntu) and [Minikube](https://github.com/kubernetes/minikube) (custom ISO) all work without issue.

To reproduce:
- install Workflow v2.7.0 on a kube-aws cluster
- observe registry-proxy isn't listening on the host's port 5555 with `netstat -tan | grep 5555`

A bit of history/debugging is available on both https://github.com/deis/registry/issues/64 and https://github.com/deis/workflow/issues/442

- Author: bacongobbler
- Quality score: 6
- URL: https://github.com/kubernetes/kubernetes/issues/23920#issuecomment-254918942
