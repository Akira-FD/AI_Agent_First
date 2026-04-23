# DNS intermittent delays of 5s



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #56903

- State: closed

- Labels: kind/bug, sig/network, area/dns

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/56903



## Problem



**Is this a BUG REPORT or FEATURE REQUEST?**:
/kind bug

**What happened**:
DNS lookup is sometimes taking 5 seconds.

**What you expected to happen**:
No delays in DNS.

**How to reproduce it (as minimally and precisely as possible)**:

1. Create a cluster in AWS using kops with cni networking:
```
kops create cluster     --node-count 3     --zones eu-west-1a,eu-west-1b,eu-west-1c     --master-zones eu-west-1a,eu-west-1b,eu-west-1c     --dns-zone kube.example.com   --node-size t2.medium     --master-size t2.medium  --topology private --networking cni   --cloud-labels "Env=Staging"  ${NAME}
```
2. CNI plugin:
```
kubectl apply -f "https://cloud.weave.works/k8s/net?k8s-version=$(kubectl version | base64 | tr -d '\n')"
```
3. Run this script in any pod with that has curl:
```
var=1
while true ; do
  res=$( { curl -o /dev/null -s -w %{time_namelookup}\\n  http://www.google.com; } 2>&1 )
  var=$((var+1))
  if [[ $res =~ ^[1-9] ]]; then
    now=$(date +"%T")
    echo "$var slow: $res $now"
    break
  fi
done
```
**Anything else we need to know?**:
1. I am encountering this issue in both staging and production clusters, but for some reason staging cluster is having a lot more 5s delays.
2. Delays happen both for external services (google.com) or internal, such as service.namespace.
3. Happens on both 1.6 and 1.7 version of kubernetes, but did not encounter these issues in 1.5 (though the setup was a bit different - no CNI back then).
4. Have not tested with 1.7 without CNI yet.

**Environment**:
- Kubernetes version (use `kubectl version`):
```
Client Version: version.Info{Major:"1", Minor:"8", GitVersion:"v1.8.2", GitCommit:"bdaeafa71f6c7c04636251031f93464384d54963", GitTreeState:"clean", BuildDate:"2017-10-24T19:48:57Z", GoVersion:"go1.8.3", Compiler:"gc", Platform:"linux/amd64"}
Server Version: version.Info{Major:"1", Minor:"7", GitVersion:"v1.7.10", GitCommit:"bebdeb749f1fa3da9e1312c4b08e439c404b3136", GitTreeState:"clean", BuildDate:"2017-11-03T16:31:49Z", GoVersion:"go1.8.3", Compiler:"gc", Platform:"linux/amd64"}
```
- Cloud provider or hardware configuration:
```
AWS
```
- OS (e.g. from /etc/os-release):
```
PRETTY_NAME="Ubuntu 16.04.3 LTS"
```
- Kernel (e.g. `uname -a`):
```
Linux ingress-nginx-3882489562-438sm 4.4.65-k8s #1 SMP Tue May 2 15:48:24 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux
```

**Similar issues**
1. https://github.com/kubernetes/dns/issues/96 - closed but seems to be exactly the same
2. https://github.com/kubernetes/kubernetes/issues/45976 - has some comments matching this issue, but is taking the direction of fixing kube-dns up/down scaling problem, and is not about the intermittent failures.

/sig network



## Curated Answers



### High Signal Answer 1

In my tests, using this option on /etc/resolv.conf 
`options single-request-reopen`

Fixed the problem.
But I don't find a "clean" way to put it on pods in kubernetes 1.8.
What I do:
```
        lifecycle:
          postStart:
            exec:
              command:
              - /bin/sh
              - -c 
              - "/bin/echo 'options single-request-reopen' >> /etc/resolv.conf"
```

@mikksoone Could you try if it solve your problem too?

- Author: vasartori
- Quality score: 32
- URL: https://github.com/kubernetes/kubernetes/issues/56903#issuecomment-359897058

### High Signal Answer 2

Doesn't solve the issue for me. Even with this option in resolv.conf I get timeouts of 5s, 2.5s and 3.5s - and they happen very often, twice per minute or so.

- Author: mikksoone
- Quality score: 15
- URL: https://github.com/kubernetes/kubernetes/issues/56903#issuecomment-360900998

### High Signal Answer 3

Just in case someone got here  because of dns delays, in our case it was arp table overflow on the nodes (arp -n showing more than 1000 entries). Increasing the limits solved the problem.

- Author: aguerra
- Quality score: 12
- URL: https://github.com/kubernetes/kubernetes/issues/56903#issuecomment-359035254
