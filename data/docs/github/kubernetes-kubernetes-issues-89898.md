# Sometime Liveness/Readiness Probes fail because of net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #89898

- State: closed

- Labels: kind/bug, sig/network, area/kubelet, sig/node, triage/accepted

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/89898



## Problem



**What happened**:
In my cluster sometimes readiness the probes are failing. But the application works fine.
```
Apr 06 18:15:14 kubenode** kubelet[34236]: I0406 18:15:14.056915   34236 prober.go:111] Readiness probe for "default-nginx-daemonset-4g6b5_default(a3734646-77fd-11ea-ad94-509a4c9f2810):nginx" failed (failure): Get http://172.18.123.127:80/: net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)
```

**What you expected to happen**:
Successful Readiness Probe.

**How to reproduce it (as minimally and precisely as possible)**:
We have few clusters with different workloads.
Only in cluster with big number of short living pods we have this issue.
But not on all nodes.
We can't reproduce this error on other our clusters (that have same configuration but different workload).
How i found the issue?
I deployed a daemonset:
```
apiVersion: extensions/v1beta1
kind: DaemonSet
metadata:
  name: default-nginx-daemonset
  namespace: default
  labels:
    k8s-app: default-nginx
spec:
  selector:
    matchLabels:
      name: default-nginx
  template:
    metadata:
      labels:
        name: default-nginx
    spec:
      tolerations:
      - operator: Exists
      containers:
      - name: nginx
        image: nginx:latest
        resources:
          limits:
            cpu: "1"
            memory: "1Gi"
          requests:
            cpu: "1"
            memory: "1Gi"
        readinessProbe:
          httpGet:
            path: /
            port: 80
```
Then i started to listen events on all pods of this daemonset.
After a couple of time i received next events:
```
Warning  Unhealthy  110s (x5 over 44m)  kubelet, kubenode20  Readiness probe failed: Get http://172.18.122.143:80/: net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)
Warning  Unhealthy  11m (x3 over 32m)  kubelet, kubenode10  Readiness probe failed: Get http://172.18.65.57:80/: net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)
....
```
Those events where on ~50% of pods of this daemonset.

On the nodes where the pods with failed probes was placed, I collected the logs of kubelet.
And there was errors like:
```
Apr 06 14:08:35 kubenode20 kubelet[10653]: I0406 14:08:35.464223   10653 prober.go:111] Readiness probe for "default-nginx-daemonset-nkwkf_default(90a3883b-77f3-11ea-ad94-509a4c9f2810):nginx" failed (failure): Get http://172.18.122.143:80/: net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)
```

I was thinking that sometimes the nginx in pod really response slowly.
For excluding this theory, I created a short script that curl the application in pod and store response time in a file:
```
while true; do curl http://172.18.122.143:80/ -s -o /dev/null -w  "%{time_starttransfer}\n" >> /tmp/measurment.txt; done;
```

I run this script on node where the pod is placed for 30 minutes and i get the following:
```
$ cat /tmp/measurment.txt | sort -u
0.000
0.001
0.002
0.003
0.004
0.005
0.006
0.007

$ cat /tmp/measurment.txt | wc -l
482670
```
There was `482670` measurements and the longest response time was `0.007`.

In logs of pod there are only message with response code 200 (from my requests and requests of readiness probes):
```
[06/Apr/2020:14:06:30 +0000] "GET / HTTP/1.1" 200 612 "-" "kube-probe/1.12" "-"
......
[06/Apr/2020:14:08:35 +0000] "GET / HTTP/1.1" 200 612 "-" "curl/7.47.0" "-"
[06/Apr/2020:14:08:35 +0000] "GET / HTTP/1.1" 200 612 "-" "curl/7.47.0" "-"
[06/Apr/2020:14:08:35 +0000] "GET / HTTP/1.1" 200 612 "-" "curl/7.47.0" "-"
......
[06/Apr/2020:14:08:41 +0000] "GET / HTTP/1.1" 200 612 "-" "kube-probe/1.12" "-"
```
It means that part of probes are successful.

Then i stopped the curl script (because the big number of logs).
I waited while new error with failed probe appears in kubelet logs.
```
Apr 06 18:15:14 kubenode13 kubelet[34236]: I0406 18:15:14.056915   34236 prober.go:111] Readiness probe for "default-nginx-daemonset-4g6b5_default(a3734646-77fd-11ea-ad94-509a4c9f2810):nginx" failed (failure): Get http://172.18.123.127:80/: net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)
```

And in logs of that pod with nginx I didn't find the request generated by this probe:
```
kubectl logs default-nginx-daemonset-4g6b5 | grep "15:15"
[06/Apr/2020:18:15:00 +0000] "GET / HTTP/1.1" 200 612 "-" "kube-probe/1.12" "-"
[06/Apr/2020:18:15:20 +0000] "GET / HTTP/1.1" 200 612 "-" "kube-probe/1.12" "-"
[06/Apr/2020:18:15:30 +0000] "GET / HTTP/1.1" 200 612 "-" "kube-probe/1.12" "-"
[06/Apr/2020:18:15:40 +0000] "GET / HTTP/1.1" 200 612 "-" "kube-probe/1.12" "-"
[06/Apr/2020:18:15:50 +0000] "GET / HTTP/1.1" 200 612 "-" "kube-probe/1.12" "-"
``` 

If I restart the kubelet - the error don't disappear.
Have someone any suggestions about this?

**Environment**:
- Kubernetes version: **1.12.1**
- Cloud provider or hardware configuration: ***hardware*
- OS (e.g: `cat /etc/os-release`): ubuntu 16.04
- Kernel (e.g. `uname -a`): 4.15.0-66-generic
- Install tools:
- Network plugin and version (if this is a network-related bug): calico:v3.1.3

Seems like the problem appears in many different installations - https://github.com/kubernetes/kubernetes/issues/51096

/sig network



## Curated Answers



### High Signal Answer 1

any update on this? we have been facing similar issues since few weeks

- Author: manikanta-kondeti
- Quality score: 54
- URL: https://github.com/kubernetes/kubernetes/issues/89898#issuecomment-614812140

### High Signal Answer 2

Are you sure the application don't hit the resources limits? 

In my case, the application starting fine, then the container start using more resources until he hit the limit. After that the readiness probes fail

- Author: Nittarab
- Quality score: 6
- URL: https://github.com/kubernetes/kubernetes/issues/89898#issuecomment-609964017

### High Signal Answer 3

This is the first such report I have seen.  There's nothing obvious about why this would happen.

It's possible kubelet is too busy and starved for CPU and the probe happened to be thing that got thrashed.  How many pods are on this machine?  How busy is it?

It's possible the node itself is thrashing or something and OOM behavior is weird.  Does dmesg show any OOMs?

It's possible some other failure down deep in kubelet is being translated into this?  You could try running kubelet at a higher log level to get more details on what is happening.

A lot of bugs have been fixed since 1.12, so we'd need to try to reproduce this and then try again in a more recent version.  Is there any way you can help boil down a simpler reproduction?

- Author: thockin
- Quality score: 5
- URL: https://github.com/kubernetes/kubernetes/issues/89898#issuecomment-614947666
