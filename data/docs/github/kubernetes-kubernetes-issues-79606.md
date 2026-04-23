# kubectl wait works for Deployment, but does not for StatefulSet



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #79606

- State: closed

- Labels: kind/bug, sig/apps, sig/cli, lifecycle/rotten, needs-triage

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/79606



## Problem



**What happened**:
```
 kubectl wait -f schema-registry.yaml --for condition=available
```
works for Deployment, but it does not work for StatefulSet

**What you expected to happen**:
Expected that kubectl wait works for StatefulSet

```
kubectl version
Client Version: version.Info{Major:"1", Minor:"13", GitVersion:"v1.13.2", GitCommit:"cff46ab41ff0bb44d8584413b598ad8360ec1def", GitTreeState:"clean", BuildDate:"2019-01-13T23:15:13Z", GoVersion:"go1.11.4", Compiler:"gc", Platform:"darwin/amd64"}
Server Version: version.Info{Major:"1", Minor:"14", GitVersion:"v1.14.3", GitCommit:"5e53fd6bc17c0dec8434817e69b04a25d8ae0ff0", GitTreeState:"clean", BuildDate:"2019-06-06T01:36:19Z", GoVersion:"go1.12.5", Compiler:"gc", Platform:"linux/amd64"}
```



## Curated Answers



### High Signal Answer 1

For everybody coming here, I suggest you try to use the `rollout status` command like this:
```
kubectl rollout status statefulset/name-of-statefulset
```

It is not exactly the same thing, but it might solve your use-case for this feature.

- Author: davelosert
- Quality score: 25
- URL: https://github.com/kubernetes/kubernetes/issues/79606#issuecomment-655282134

### High Signal Answer 2

> For everybody coming here, I suggest you try to use the rollout status command like this:

If you want to wait until a statefulset rollout is finished, you can do the following:

```
kubectl rollout status --watch --timeout=600s statefulset/name-of-statefulset
```

- Author: joshlk
- Quality score: 19
- URL: https://github.com/kubernetes/kubernetes/issues/79606#issuecomment-779779928
