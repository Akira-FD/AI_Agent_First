# "externalTrafficPolicy": "Local" on AWS does not work if the dhcp of the vpc is not set exactly to <region>.compute.internal



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #61486

- State: closed

- Labels: kind/bug, area/provider/aws, sig/cloud-provider, triage/accepted

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/61486



## Problem



**Is this a BUG REPORT or FEATURE REQUEST?**:

> Uncomment only one, leave it on its own line: 
>
/kind bug
> /kind feature

/sig aws

**What happened**:

Run a Gossip-cluster
Using NLB  as ExternalLoadBalancer on AWS, with externalTrafficPolicy set to Local, all the targets in the Target groups were unhealthy even though the pod for the service was running on a specific Node

**What you expected to happen**:

Find a healthy target on the Instance (node) containing the pod related to the service

**How to reproduce it (as minimally and precisely as possible)**:

1) Create an existing VPC with domain name set to vpc.internal
2) Use kops to deploy kubernetes on AWS on the existing VPC as a gossip-cluster (no dns zones) cluster name ends with k8s.local
    a) kops will correctly start kubelet with --cloud-provider=aws and --hostname-override=<ip-...>.vpc.internal
    b) Observe the kubectl get nodes still shows node names as <ip-...>.region.compute.internal (non us-east-1 region)
3) Deploy a pod affinitized to a specific node
4) Deploy a LoadBalancer service for NLB annotation with externalTrafficPolicy: Local
5) Observe in aws that Target Group associated with the NLB doesn't have any healthy targets. Also observe that the curl to the host on the health port returns a 503 with localendpoints: 0

**Anything else we need to know?**:

Basically, the issues is related to the following bug in a tangential manner

https://github.com/kubernetes/kubernetes/issues/11543 

If VPC has a different domain name than the one aws cloudprovider in kubernetes sets for the nodes name then the endpoint.NodeName does not match the hostname that the proxy is running on and this causes the proxy to determine that there are no local endpoints for the service.

**Environment**:
- Kubernetes version (use `kubectl version`):
bash-3.2$ kubectl version
Client Version: version.Info{Major:"1", Minor:"9", GitVersion:"v1.9.2", GitCommit:"5fa2db2bd46ac79e5e00a4e6ed24191080aa463b", GitTreeState:"clean", BuildDate:"2018-01-18T10:09:24Z", GoVersion:"go1.9.2", Compiler:"gc", Platform:"darwin/amd64"}
Server Version: version.Info{Major:"1", Minor:"9", GitVersion:"v1.9.4", GitCommit:"bee2d1505c4fe820744d26d41ecd3fdd4a3d6546", GitTreeState:"clean", BuildDate:"2018-03-12T16:21:35Z", GoVersion:"go1.9.3", Compiler:"gc", Platform:"linux/amd64"}

- Cloud provider or hardware configuration: AWS
- OS (e.g. from /etc/os-release):
NAME="Red Hat Enterprise Linux Server"
VERSION="7.4 (Maipo)"
ID="rhel"
ID_LIKE="fedora"
VARIANT="Server"
VARIANT_ID="server"
VERSION_ID="7.4"
PRETTY_NAME="Red Hat Enterprise Linux Server 7.4 (Maipo)"
ANSI_COLOR="0;31"
CPE_NAME="cpe:/o:redhat:enterprise_linux:7.4:GA:server"
HOME_URL="https://www.redhat.com/"
BUG_REPORT_URL="https://bugzilla.redhat.com/"

REDHAT_BUGZILLA_PRODUCT="Red Hat Enterprise Linux 7"
REDHAT_BUGZILLA_PRODUCT_VERSION=7.4
REDHAT_SUPPORT_PRODUCT="Red Hat Enterprise Linux"
REDHAT_SUPPORT_PRODUCT_VERSION="7.4"
- Kernel (e.g. `uname -a`):
Linux ip-10-103-184-242.vpc.internal 3.10.0-693.17.1.el7.x86_64 #1 SMP Sun Jan 14 10:36:03 EST 2018 x86_64 x86_64 x86_64 GNU/Linux
- Install tools:
kops
- Others:



## Curated Answers



### High Signal Answer 1

I can confirm that [this workaround](https://github.com/kubernetes/kubernetes/issues/61486#issuecomment-542314543) worked for us on EKS 1.15. The full patch to be easily copypasted:

```yaml
---
spec:
  template:
    spec:
      containers:
        - name: kube-proxy
          command:
            - kube-proxy
            - --hostname-override=$(NODE_NAME)
            - --v=2
            - --config=/var/lib/kube-proxy-config/config
          env:
            - name: NODE_NAME
              valueFrom:
                fieldRef:
                  apiVersion: v1
                  fieldPath: spec.nodeName
```

and the `kubectl` command for easy copypasting too:
```bash
kubectl -n kube-system patch daemonset kube-proxy --patch "$(cat nodeport-local-patch.yml)"
```

- Author: vide
- Quality score: 39
- URL: https://github.com/kubernetes/kubernetes/issues/61486#issuecomment-635169272

### High Signal Answer 2

@shaikatz You can patch your kube-proxy daemonset to add two things:
1) Add a NODE_NAME env var:
```yaml
        env:
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              apiVersion: v1
              fieldPath: spec.nodeName
```
2. Then use the NODE_NAME env var to pass in a --hostname-override to the list of flags to the kube-proxy command.  Mine looks something like this:
```yaml
      - command:
        - /bin/sh
        - -c
        - kube-proxy --resource-container="" --oom-score-adj=-998 --master=https://abc123.sk1.us-east-1.eks.amazonaws.com
          --kubeconfig=/var/lib/kube-proxy/kubeconfig --proxy-mode=iptables --v=2
          --hostname-override=${NODE_NAME} 1>>/var/log/kube-proxy.log 2>&1
```

- Author: victortrac
- Quality score: 10
- URL: https://github.com/kubernetes/kubernetes/issues/61486#issuecomment-533130117

### High Signal Answer 3

This workaround did not work for us in EKS. It resulted in the `Failed to retrieve node info: nodes "${node_name}" not found` in the kube-proxy logs. We have a newer version of kube-proxy, so that might be the issue. `--hostname-override=$(NODE_NAME)` instead worked for us. Here is the relevant portion of our kube-proxy manifest.
```yaml
- command:
  - kube-proxy
  - --hostname-override=$(NODE_NAME)
  - --v=2
  - --config=/var/lib/kube-proxy-config/config
  env:
  - name: NODE_NAME
    valueFrom:
      fieldRef:
        apiVersion: v1
        fieldPath: spec.nodeName

- Author: bluskool
- Quality score: 10
- URL: https://github.com/kubernetes/kubernetes/issues/61486#issuecomment-542314543
