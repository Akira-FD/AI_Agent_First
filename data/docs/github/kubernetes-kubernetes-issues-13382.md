# Suddenly getting TLS Handshake timeout on most requests to the api server



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #13382

- State: closed

- Labels: priority/important-soon, sig/node, sig/api-machinery

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/13382



## Problem



I'm unable to use `kubectl` because of TLS handshake timeout.

```
kubectl get pods
error: couldn't read version from server: Get https://master-ip/api: net/http: TLS handshake timeout
```

edit: After several tries I got one to go through, so it's not happening 100% of the time.  But the error has been recorded over 4k times in the logs.

I've also noticed the error is showing up often in `/var/log/kube-apisever.log` from requests from minions.

```
I0831 12:35:19.950945       8 logs.go:41] http: TLS handshake error from 172.20.0.65:58143: EOF
I0831 12:35:20.599641       8 logs.go:41] http: TLS handshake error from 172.20.0.148:53774: EOF
I0831 12:35:20.601809       8 logs.go:41] http: TLS handshake error from 172.20.0.240:41027: EOF
I0831 12:35:22.272985       8 logs.go:41] http: TLS handshake error from 172.20.0.25:42939: EOF
I0831 12:35:23.210921       8 logs.go:41] http: TLS handshake error from 172.20.0.240:41034: EOF
I0831 12:35:24.520112       8 logs.go:41] http: TLS handshake error from 172.20.0.65:58172: EOF
```

I also noticed a lot of `dial tcp 127.0.0.1:8080: connection refused` errors in the logs on various endpoints.

```
E0831 12:36:54.588879       5 reflector.go:136] Failed to list *api.ResourceQuota: Get http://127.0.0.1:8080/api/v1/resourcequotas: dial tcp 127.0.0.1:8080: connection refused
E0831 12:36:54.589161       5 reflector.go:136] Failed to list *api.Secret: Get http://127.0.0.1:8080/api/v1/secrets?fieldSelector=type%3Dkubernetes.io%2Fservice-account-token: dial tcp 127.0.0.1:8080: connection refused
E0831 12:36:54.628359       5 reflector.go:136] Failed to list *api.ServiceAccount: Get http://127.0.0.1:8080/api/v1/serviceaccounts: dial tcp 127.0.0.1:8080: connection refused
E0831 12:36:54.628471       5 reflector.go:136] Failed to list *api.LimitRange: Get http://127.0.0.1:8080/api/v1/limitranges: dial tcp 127.0.0.1:8080: connection refused
E0831 12:36:54.628608       5 reflector.go:136] Failed to list *api.Namespace: Get http://127.0.0.1:8080/api/v1/namespaces: dial tcp 127.0.0.1:8080: connection refused
E0831 12:36:54.628669       5 reflector.go:136] Failed to list *api.Namespace: Get http://127.0.0.1:8080/api/v1/namespaces: dial tcp 127.0.0.1:8080: connection refused
```

If it's relevant, the ephemeral filesystem on /mnt/ephemeral/kubernetes is 99% on one of my minions.  Most of my kube-system pods (kube-ui, kube-dns, elasticsearch, etc) are running that minion. It's full because of elasticsearch and heapster empity-dir volumes, and the mount is only 3.75GB. This filesystem being full caused other problems this weekend, including containers from the kube-dns pod shutting down which in turn brought down all of my other production pods over the weekend.



## Curated Answers



### High Signal Answer 1

@lavalamp we're running into the same problem, unfortunately, it doesn't seem [any SO post has been created](http://stackoverflow.com/search?q=%5Bkubernetes%5D+TLS+handshake+timeout) for this issue.

We're running on GKE without any manual modifications, should it still be considered a "question" on SO, or is this an issue related to Kubernetes?

In our case, we had a script use a service-account on Kubernetes to access the API using `kubectl`, but suddenly we started seeing failures, related to the command not being able to access the API server:

```
$ kubectl get pod
error: couldn't read version from server: Get https://10.135.240.1:443/api: net/http: TLS handshake timeout
```

- Author: JeanMertz
- Quality score: 13
- URL: https://github.com/kubernetes/kubernetes/issues/13382#issuecomment-143466968

### High Signal Answer 2

@rroopreddy Your master ran out of memory. Force reboot it via your cluster.

On the master, after it comes back up:

```
sudo apt-get update
sudo apt-get install swapspace
```

This will automatically scale swap so that you never run out of memory and deadlock yourself out.

- Author: paralin
- Quality score: 10
- URL: https://github.com/kubernetes/kubernetes/issues/13382#issuecomment-154891888

### High Signal Answer 3

Just started seeing this again @roberthbailey 

```
Oct 21 06:31:43 ip-172-20-0-115 kubelet[25950]: E1021 06:31:43.245829   25950 kubelet.go:2259] Error updating node status, will retry: Put https://172.20.0.9/api/v1/nodes/ip-172-20-0-115.us-west-2.compute.internal/status: net/http: TLS handshake timeout
Oct 21 06:31:46 ip-172-20-0-115 kubelet[25950]: E1021 06:31:46.303538   25950 reflector.go:206] pkg/kubelet/kubelet.go:211: Failed to watch *api.Service: Get https://172.20.0.9/api/v1/watch/services?resourceVersion=1904: net/http: TLS handshake timeout
```

Any ideas?

- Author: paralin
- Quality score: 5
- URL: https://github.com/kubernetes/kubernetes/issues/13382#issuecomment-149795474
