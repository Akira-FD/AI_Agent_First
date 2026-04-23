# Running Kubernetes Locally via Docker - `kubectl get nodes` returns `The connection to the server localhost:8080 was refused - did you specify the right host or port?`



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #23726

- State: closed

- Labels: kind/support

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/23726



## Problem



Going through [this](http://kubernetes.io/docs/getting-started-guides/docker/) guide to set up kubernetes locally via docker I end up with the error message as stated above.

Steps taken:
- `export K8S_VERSION='1.3.0-alpha.1'` (tried 1.2.0 as well)
- copy-paste the `docker run` command
- download the appropriate `kubectl` binary and put in on `PATH` (`which kubectl` works)
- (optionally) setup the cluster
- run `kubectl get nodes`

In short, no magic. I am running this locally on Ubuntu 14.04, docker 1.10.3. If you need more information let me know



## Curated Answers



### High Signal Answer 1

You can solve this with "kubectl config":

```
$ kubectl config set-cluster demo-cluster --server=http://master.example.com:8080
$ kubectl config set-context demo-system --cluster=demo-cluster
$ kubectl config use-context demo-system
$ kubectl get nodes
NAME                 STATUS    AGE
master.example.com   Ready     3h
node1.example.com    Ready     2h
node2.example.com    Ready     2h
```

- Author: kvarnhammar
- Quality score: 54
- URL: https://github.com/kubernetes/kubernetes/issues/23726#issuecomment-258381872

### High Signal Answer 2

Similar to @sumitkau, I solved my problem with setting new kubelet config location using:
kubectl --kubeconfig /etc/kubernetes/admin.conf get no
You can also copy /etc/kubernetes/admin.conf  to ~/.kube/config and it works, but I don't know that it's a good work or not!

- Author: mamirkhani
- Quality score: 47
- URL: https://github.com/kubernetes/kubernetes/issues/23726#issuecomment-292776436

### High Signal Answer 3

Hello I'm getting the following error on Centos 7, how can solve this issue?

```
[root@ip-172-31-11-12 system]# kubectl get nodes
The connection to the server localhost:8080 was refused - did you specify the right host or port?
```

- Author: rahmanusta
- Quality score: 46
- URL: https://github.com/kubernetes/kubernetes/issues/23726#issuecomment-257036251
