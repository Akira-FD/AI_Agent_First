# kubernetes-dashboard pod in CrashLoopBackOff state 



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #29540

- State: closed

- Labels: kind/support, lifecycle/rotten

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/29540



## Problem



I am trying to intsall Kubernetes dashboard by the command:

`kubectl create -f https://rawgit.com/kubernetes/dashboard/master/src/deploy/kubernetes-dashboard.yaml`.

However when I do `kubectl get po -o wide --all-namespaces` I see the status of the kubernetes-dashboard pod as "CrashLoopBackOff". The output of command `kubectl logs kubernetes-dashboard-3717423461-gxrwv --namespace=kube-system` looks like this:

`Starting HTTP server on port 9090
Creating API server client for https://192.168.3.1:443
Error while initializing connection to Kubernetes apiserver. This most likely means that the cluster is misconfigured (e.g., it has invalid apiserver certificates or service accounts configuration) or the --apiserver-host param points to a server that does not exist. Reason: the server has asked for the client to provide credentials`

Does anyone know how to fix this issue? Thanks in advance.



## Curated Answers



### High Signal Answer 1

I remember resolving the issue by first deleting the secret corresponding to the kube-system namespace, i.e 

`kubectl delete secret secretName -n kube-system`

The api-server will then create a new secret. Now delete the dashboard pod, and the new pod spun up by the rc/deployment will use the new secret and the errors corresponding to "credentials" should be gone.

Alteast this worked for me :)

- Author: rihabbanday
- Quality score: 12
- URL: https://github.com/kubernetes/kubernetes/issues/29540#issuecomment-292779268

### High Signal Answer 2

[update] I solved the issue by manually point to apiserver using the 'args' attribute in 'kubernetes-dashboard.yaml':
args:
          # Uncomment the following line to manually specify Kubernetes API server Host
          # If not specified, Dashboard will attempt to auto discover the API server and connect
          # to it. Uncomment only if the default does not work.
          # - --apiserver-host=http://my-address:port

- Author: amdslancelot
- Quality score: 9
- URL: https://github.com/kubernetes/kubernetes/issues/29540#issuecomment-257412445

### High Signal Answer 3

Same issue here. Why did @dchen1107 even close this?

- Author: jazoom
- Quality score: 9
- URL: https://github.com/kubernetes/kubernetes/issues/29540#issuecomment-292770279
