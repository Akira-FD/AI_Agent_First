# Cannot retrieve logs of running pod via kubectl



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #45911

- State: closed

- Labels: sig/cli, lifecycle/rotten

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/45911



## Problem



<!-- Thanks for filing an issue! Before hitting the button, please answer these questions.-->

**Is this a request for help?** (If yes, you should use our troubleshooting guide and community support channels, see http://kubernetes.io/docs/troubleshooting/.): No


**What keywords did you search in Kubernetes issues before filing this one?** (If you have found any duplicates, you should instead reply there.): `"failed to open log file"` `"/var/log/pods"`

---

**Is this a BUG REPORT or FEATURE REQUEST?** (choose one): BUG REPORT

<!--
If this is a BUG REPORT, please:
  - Fill in as much of the template below as you can.  If you leave out
    information, we can't help you as well.

If this is a FEATURE REQUEST, please:
  - Describe *in detail* the feature/behavior/change you'd like to see.

In both cases, be ready for followup questions, and please respond in a timely
manner.  If we can't reproduce a bug or think a feature already exists, we
might close your issue.  If we're wrong, PLEASE feel free to reopen it and
explain why.
-->

**Kubernetes version** (use `kubectl version`):

```
Client Version: version.Info{Major:"1", Minor:"6", GitVersion:"v1.6.3", GitCommit:"0480917b552be33e2dba47386e51decb1a211df6", GitTreeState:"clean", BuildDate:"2017-05-10T23:29:08Z", GoVersion:"go1.8.1", Compiler:"gc", Platform:"darwin/amd64"}
Server Version: version.Info{Major:"1", Minor:"6", GitVersion:"v1.6.3+coreos.0", GitCommit:"70bc0937018d89b0d529d428eed8c444d8e7729a", GitTreeState:"clean", BuildDate:"2017-05-11T18:15:57Z", GoVersion:"go1.7.5", Compiler:"gc", Platform:"linux/amd64"}
```


**Environment**:
- **Cloud provider or hardware configuration**: AWS
- **OS** (e.g. from /etc/os-release): Container Linux by CoreOS 1353.7.0 (Ladybug)
- **Kernel** (e.g. `uname -a`): `Linux 4.9.24-coreos #1 SMP Wed Apr 26 21:44:23 UTC 2017 x86_64 Intel(R) Xeon(R) CPU E5-2670 v2 @ 2.50GHz GenuineIntel GNU/Linux`
- **Install tools**: kube-aws
- **Others**:


**What happened**:

After observing one of my pods restarted, I was trying to diagnose what happened when I ran `kubectl -n <ns> logs <pod name> -c <container name>`, which gave the following output:

```
$ kubectl -n kube-system logs estranged-anaconda-prometheus-server-2221453258-x1vk5 -c prometheus-server
failed to open log file "/var/log/pods/30aae155-39cb-11e7-97d7-024e1e23286b/prometheus-server_1.log": open /var/log/pods/30aae155-39cb-11e7-97d7-024e1e23286b/prometheus-server_1.log: no such file or directory
```

I could retrieve the previous container's logs with the `--previous` flag though:

```
$ kubectl -n kube-system logs --previous estranged-anaconda-prometheus-server-2221453258-x1vk5 -c prometheus-server
# Lots of logs...
time="2017-05-16T19:38:35Z" level=info msg="Done checkpointing in-memory metrics and chunks in 13.760728705s." source="persistence.go:639"
time="2017-05-16T19:43:35Z" level=info msg="Checkpointing in-memory metrics and chunks..." source="persistence.go:612"
time="2017-05-16T19:44:03Z" level=info msg="Done checkpointing in-memory metrics and chunks in 27.371760948s." source="persistence.go:639"
time="2017-05-16T19:44:24Z" level=error msg="Error sending alerts: context deadline exceeded" alertmanager="http://estranged-anaconda-prometheus-alertmanager:80/api/v1/alerts" count=1 source="notifier.go:335"
```

I logged into the instance via SSH and verified the file `prometheus-server-log_1.log` was not there.

What I saw, though, was that there was a `prometheus-server-log_0.log` (with the zero) sitting in that directory that pointed to the logs of the previous dead container:

```
$ sudo ls -alh /var/log/pods/30aae155-39cb-11e7-97d7-024e1e23286b/prometheus-server_0.log
lrwxrwxrwx. 1 root root 165 May 16 00:10 /var/log/pods/30aae155-39cb-11e7-97d7-024e1e23286b/prometheus-server_0.log -> /var/lib/docker/containers/1dbad7b380f60644dd471b8c2e2f9b193d819505f2e18819e4be8586575d5109/1dbad7b380f60644dd471b8c2e2f9b193d819505f2e18819e4be8586575d5109-json.log

$ docker ps -a
CONTAINER ID        IMAGE                                                                                                                                    COMMAND                  CREATED             STATUS                        PORTS               NAMES
55d8e7e00878        prom/prometheus@sha256:e049c086e35c0426389cd2450ef193f6c18b3d0065b97e5f203fdb254716fa1c                                                  "/bin/prometheus --al"   33 minutes ago      Up 31 minutes                                     k8s_prometheus-server_estranged-anaconda-prometheus-server-2221453258-x1vk5_kube-system_30aae155-39cb-11e7-97d7-024e1e23286b_1
1dbad7b380f6        prom/prometheus@sha256:e049c086e35c0426389cd2450ef193f6c18b3d0065b97e5f203fdb254716fa1c                                                  "/bin/prometheus --al"   20 hours ago        Exited (137) 33 minutes ago                       k8s_prometheus-server_estranged-anaconda-prometheus-server-2221453258-x1vk5_kube-system_30aae155-39cb-11e7-97d7-024e1e23286b_0
```

I also saw that the symlink in `/var/log/containers` pointed to the killed container logs, and not the new container logs:

```
$ ls /var/log/containers
# ...
estranged-anaconda-prometheus-server-2221453258-x1vk5_kube-system_prometheus-server-1dbad7b380f60644dd471b8c2e2f9b193d819505f2e18819e4be8586575d5109.log
```

I could see the logs of the new container by running `docker logs <new container id>`, and verified that these logs were being written correctly to `/var/lib/docker/containers/<new container id>`.

**What you expected to happen**:

I expected `kubectl logs` command to retrieve the logs of the running container.

I also expected the Kubelet to only keep symlinks to running containers in `/var/lib/docker/containers/<container id>`.

**How to reproduce it** (as minimally and precisely as possible):

I haven't been able to reproduce this issue, as I tried retrieving the logs of other pods that restarted, without any similar issues.

**Anything else we need to know**:

When looking at the pod directly, I noticed the pod was terminated with reason `Error`:

```
    Last State:         Terminated
      Reason:           Error
      Exit Code:        137
      Started:          Mon, 01 Jan 0001 00:00:00 +0000
      Finished:         Tue, 16 May 2017 16:45:22 -0300
```

(The "Started" date seems odd as well...)

According to dmesg, the container process was reaped by the Kernel OOM killer:

```
$ dmesg -T | grep prometheus
[Tue May 16 19:45:20 2017] prometheus invoked oom-killer: gfp_mask=0x24201ca(GFP_HIGHUSER_MOVABLE|__GFP_COLD), nodemask=0, order=0, oom_score_adj=179
[Tue May 16 19:45:20 2017] prometheus cpuset=1dbad7b380f60644dd471b8c2e2f9b193d819505f2e18819e4be8586575d5109 mems_allowed=0
[Tue May 16 19:45:20 2017] CPU: 1 PID: 20234 Comm: prometheus Not tainted 4.9.24-coreos #1
[Tue May 16 19:45:20 2017] [15192]     0 15192  1679458  1648518    3283      11        0           179 prometheus
[Tue May 16 19:45:20 2017] Out of memory: Kill process 15192 (prometheus) score 1041 or sacrifice child
[Tue May 16 19:45:20 2017] Killed process 15192 (prometheus) total-vm:6717832kB, anon-rss:6594072kB, file-rss:0kB, shmem-rss:0kB
[Tue May 16 19:45:21 2017] oom_reaper: reaped process 15192 (prometheus), now anon-rss:0kB, file-rss:4kB, shmem-rss:0kB
```

Maybe this could be a clue as to why this happened.



## Curated Answers



### High Signal Answer 1

After spending some time browsing through the source code, I found [this](https://github.com/kubernetes/kubernetes/blob/ff3a847d08553ff977d4484bd3ae9808db180633/pkg/kubelet/dockershim/docker_container.go#L268) snippet that seem to be where the symlinks for the container logs are created.

So, if we are starting a "heavy" container that cause the Docker daemon to hang for a while, it's plausible that `createContainerLogSymlink` don't get called, thus not creating the symlink.

Example scenario:

1. Kubelet calls `StartContainer` to create the container. Docker receives the request and starts the "heavy" container, which immediately cause the Docker daemon to hang (due to high load of some sort) and not respond any subsequent requests for a few minutes
2. Kubelet calls `createContainerLogSymlink`, that calls some other functions that ultimately call `InspectContainer`, which tries to fetch information about the container from the Docker daemon (which is unable to respond)
3. The Kubelet request to the Docker daemon times out, causing the log symlinks not to be created
4. Container finally starts up, causing the Docker daemon to start being able to answer requests again
5. Container is running, but we are unable to fetch the logs via `kubectl logs` due to the missing symlinks

Is that a possible scenario?

- Author: danielfm
- Quality score: 10
- URL: https://github.com/kubernetes/kubernetes/issues/45911#issuecomment-302820569

### High Signal Answer 2

@danielfm Yeah, it is possible.

In Kubelet, we set a 2 minutes timeout for most docker operations, including start container.

If start container takes too long time, we'll cancel the request on kubelet side and returns an error. Thus log symlink will not be created. However, docker should still be starting the container, and the container may be running later.

- Author: Random-Liu
- Quality score: 4
- URL: https://github.com/kubernetes/kubernetes/issues/45911#issuecomment-302836671

### High Signal Answer 3

I'm seeing this issue on a tiny init container that's just trying to copy a file to `emptyDir`

- Author: derekperkins
- Quality score: 4
- URL: https://github.com/kubernetes/kubernetes/issues/45911#issuecomment-353655403
