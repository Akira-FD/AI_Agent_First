# kubectl port-forward doesn't properly recover from interrupted connection errors



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #78446

- State: closed

- Labels: kind/bug, sig/cli, lifecycle/stale

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/78446



## Problem



**What happened**:
When I open a large number (in the 100s) of concurrent long-running HTTP requests against a port-forwarded pod that is running on GKE 1.13.6-gke.0 which I then interrupt/cancel, I observe timeout errors being reported by `kubectl port-forward pod/[pod_name] 8000:8000`. Eventually, the forwarded port becomes permanently unusable until I relaunch the command.

Types of messages that get logged by `kubectl port-forward`:
1. `Handling connection for 8000`
1. `E0528 16:12:42.255465   13724 portforward.go:303] error copying from remote stream to local connection: readfrom tcp4 127.0.0.1:8000->127.0.0.1:62974: write tcp4 127.0.0.1:8000->127.0.0.1:62974: wsasend: An established connection was aborted by the software in your host machine.`
1. `E0528 16:13:12.495226   13724 portforward.go:293] error creating forwarding stream for port 8000 -> 8000: Timeout occured`
1. `E0528 16:13:53.891935   13724 portforward.go:271] error creating error stream for port 8000 -> 8000: Timeout occured`

After the port-forward becomes permanently unusable, I still see incoming requests logged as:
```
Handling connection for 8000
```

which then all fail about 30 seconds later with the following error, without the request being set to the pod:
```
E0528 16:38:06.245530    6668 portforward.go:271] error creating error stream for port 8000 -> 8000: Timeout occured
```

**What you expected to happen**:

1. Never have to relaunch `kubectl port-forward` because it is in a permanent failed state
1. All concurrent long-running HTTP requests to succeed (up to some reasonable amount of them of course)

**How to reproduce it (as minimally and precisely as possible)**:
1. Create an nginx pod serving a large 1GB static file:
    ```
    kubectl run -ti --rm --restart=Never --image=nginx nginx -- bash "-c" "dd if=/dev/zero of=/usr/share/nginx/html/large_file.bin count=1024 bs=1048576 && nginx -g 'daemon off;'"
    ```
1.  Port-forward it: `kubectl port-forward nginx 1234:80`
1. Run [Apache Bench](https://httpd.apache.org/docs/2.4/programs/ab.html) with 100 total requests, 100 concurrent ones and 1 second timeout, that you interrupt using Control+C (for some reason the timeout doesn't seem to be well enforced):
    ```
    ab -n 100 -c 100 -s 1 http://127.0.0.1:1234/large_file.bin
    ```
    Note that in my initial use-case, I managed to get this issue simply by quickly refreshing the URL in Google Chrome without any benchmarking tool.
1. If needed, re-run the same Apache Bench command until the port-forwarding fails to serve all incoming requests
1. Observe that now all requests to the nginx servers, even to http://127.0.0.1:1234/index.html are all failing. Additionally, nginx doesn't output those requests in its logs.
1. Relaunch the `kubectl port-forward nginx 1234:80` command, and the URL becomes available again showing that the pod was still healthy. 

**Anything else we need to know?**:

Possibility related issues & PRs:
- https://github.com/openshift/origin/issues/4287 - reports a similar bug
- https://github.com/kubernetes/kubernetes/issues/13673
- https://github.com/kubernetes/kubernetes/pull/12283

**Environment**:
- Kubernetes version (use `kubectl version`):
```
Client Version: version.Info{Major:"1", Minor:"12+", GitVersion:"v1.12.8-dispatcher", GitCommit:"1215389331387f57594b42c5dd024a2fe27334f8", GitTreeState:"clean", BuildDate:"2019-05-13T18:28:02Z", GoVersion:"go1.10.8", Compiler:"gc", Platform:"windows/amd64"}
Server Version: version.Info{Major:"1", Minor:"13+", GitVersion:"v1.13.6-gke.0", GitCommit:"14c9138d6fb5b57473e270fe8a2973300fbd6fd6", GitTreeState:"clean", BuildDate:"2019-05-08T16:22:55Z", GoVersion:"go1.11.5b4", Compiler:"gc", Platform:"linux/amd64"}
```
- Cloud provider or hardware configuration: GKE 1.13.6-gke.0
- OS (e.g: `cat /etc/os-release`): Windows
- Kernel (e.g. `uname -a`): Windows
- Install tools:
- Network plugin and version (if this is a network-related bug):
- Others:



## Curated Answers



### High Signal Answer 1

Same error when port-forwarding to AWS EKS pod:

`E0806 17:04:44.805492   78962 portforward.go:385] error copying from local connection to remote stream: read tcp6 [::1]:3000->[::1]:61216: read: connection reset by peer`

kubectl version:

>Client Version: version.Info{Major:"1", Minor:"15", GitVersion:"v1.15.2", GitCommit:"f6278300bebbb750328ac16ee6dd3aa7d3549568", GitTreeState:"clean", BuildDate:"2019-08-05T16:54:35Z", GoVersion:"go1.12.7", Compiler:"gc", Platform:"darwin/amd64"}

- Author: cksassy
- Quality score: 16
- URL: https://github.com/kubernetes/kubernetes/issues/78446#issuecomment-519195645

### High Signal Answer 2

Does anybody have a solid workaround for this?

- Author: KotieSmit
- Quality score: 13
- URL: https://github.com/kubernetes/kubernetes/issues/78446#issuecomment-588087802
