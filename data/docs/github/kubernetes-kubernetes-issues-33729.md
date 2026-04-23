# kubeadm init hangs on ubuntu 16.04



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #33729

- State: closed

- Labels: sig/cluster-lifecycle, area/kubeadm

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/33729



## Problem



<!-- Thanks for filing an issue! Before hitting the button, please answer these questions.-->

**Is this a request for help?** (If yes, you should use our troubleshooting guide and community support channels, see http://kubernetes.io/docs/troubleshooting/.):

**What keywords did you search in Kubernetes issues before filing this one?** (If you have found any duplicates, you should instead reply there.):
created API client, waiting for the control plane to become ready
## Related to or a similar discussion happened @ https://github.com/kubernetes/kubernetes/issues/33544

*\* BUG REPORT *\* (choose one):

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
kubectl version
Client Version: version.Info{Major:"1", Minor:"4", GitVersion:"v1.4.0", GitCommit:"a16c0a7f71a6f93c7e0f222d961f4675cd97a46b", GitTreeState:"clean", BuildDate:"2016-09-26T18:16:57Z", GoVersion:"go1.6.3", Compiler:"gc", Platform:"linux/amd64"}

kubeadm version: version.Info{Major:"1", Minor:"5+", GitVersion:"v1.5.0-alpha.0.1534+cf7301f16c0363-dirty", GitCommit:"cf7301f16c036363c4fdcb5d4d0c867720214598", GitTreeState:"dirty", BuildDate:"2016-09-27T18:10:39Z", GoVersion:"go1.6.3", Compiler:"gc", Platform:"linux/amd64"}

**Environment**:
- **Cloud provider or hardware configuration**:
  Virtual box, vagrant 1.8.1, bento/ubuntu-16.04, 1.5GB RAM, 1 CPU
- **OS** (e.g. from /etc/os-release):
  Distributor ID: Ubuntu
  Description:    Ubuntu 16.04.1 LTS
  Release:    16.04
  Codename:   xenial
- **Kernel** (e.g. `uname -a`):
  Linux vagrant 4.4.0-38-generic #57-Ubuntu SMP Tue Sep 6 15:42:33 UTC 2016 x86_64 x86_64 x86_64 GNU/Linux
- **Install tools**:
- **Others**:

**What happened**:
As I try to run kubeadm init, it hangs with 
root@vagrant:~# kubeadm init

```
<master/tokens> generated token: "eca953.0642ac0fa7fc6378"
<master/pki> created keys and certificates in "/etc/kubernetes/pki"
<util/kubeconfig> created "/etc/kubernetes/kubelet.conf"
<util/kubeconfig> created "/etc/kubernetes/admin.conf"
<master/apiclient> created API client configuration
<master/apiclient> created API client, waiting for the control plane to become ready
```

**What you expected to happen**:
The command should have succeeded thereby downloading and installing the cluster database and “control plane” components

**How to reproduce it** (as minimally and precisely as possible):
Download and install docker on Ubuntu 16.04 by following https://docs.docker.com/engine/installation/linux/ubuntulinux/

Follow http://kubernetes.io/docs/getting-started-guides/kubeadm/ to install kubernete

**Anything else do we need to know**:



## Curated Answers



### High Signal Answer 1

@oz123 I have the same issue here. It doesn't seems to be due to slow connection (i've been waiting for 30 min and I have a very fast internet connection in my office too).
Nothing relevant found into the logs.

- Author: Arv3n6
- Quality score: 5
- URL: https://github.com/kubernetes/kubernetes/issues/33729#issuecomment-250475784

### High Signal Answer 2

@oz123 @Miyurz  I managed to fix the issue after reading this page : https://docs.docker.com/engine/admin/systemd/#/http-proxy

I added the proxy configuration in in the Docker systemd service file and it works (approximately 20 sec to  start the master with # kubeadm init).

- Author: Arv3n6
- Quality score: 5
- URL: https://github.com/kubernetes/kubernetes/issues/33729#issuecomment-250485871

### High Signal Answer 3

I've faced the same issue here in my Ubuntu 16.04, in my case the problem was:
- kubelet service was **not** running
- I had a previous service (personal web server) running in TCP port 8080 (discovery use the same port but there is no error!)

fixed "once" with:
- sudo service kubelet stop
- # stop my personal web server on 8080
- sudo service kubelet start
- kubeadm init

after that kubeadm worked properly

**note**: found the process above may fail sometimes. Looks like a sync problem between kubeadm init start and kubelet do it work. Kubeadm fails with:

```
error: <master/discovery> failed to create "kube-discovery" deployment [deployments.extensions "kube-discovery" already exists]
```

- Author: edsiper
- Quality score: 4
- URL: https://github.com/kubernetes/kubernetes/issues/33729#issuecomment-250960706
