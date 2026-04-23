# kubectl get pods should report last restart time?



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #54491

- State: closed

- Labels: area/kubectl, kind/feature, sig/cli, lifecycle/frozen, good first issue

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/54491



## Problem



When a pod is being restarted, the time it last restarted is very relevant (if it was hours ago, I don't care).  We should consider some information being presented about how recent the restart is.

For example, real world example

```
$ kubectl get pods
NAME           READY     STATUS    RESTARTS   AGE
prometheus-0   5/5       Running   30         21h
```

I don't know when the time of the last restart was.  In this case it was 15 hours ago, so the 30 restarts actually doesn't matter.  The age is 21h, but that's not very useful.  Trying to find a middle ground would be useful.



## Curated Answers



### High Signal Answer 1

This feature should be there. It helps in identifying issue in much better/easy way. For example if we are facing issues during in a time window, in the that time window it is very relevant information to see.

- Author: rohitkhatana
- Quality score: 8
- URL: https://github.com/kubernetes/kubernetes/issues/54491#issuecomment-569166688

### High Signal Answer 2

Hey @soltysh, I opened the PR, if you have some time to check it

- Author: jjacobelli
- Quality score: 7
- URL: https://github.com/kubernetes/kubernetes/issues/54491#issuecomment-797480517
