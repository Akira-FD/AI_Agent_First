# don't require API server connection for `kubectl create configmap ... --dry-run`



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #51475

- State: closed

- Labels: area/kubectl, sig/api-machinery, kind/feature, sig/cli, lifecycle/rotten, triage/accepted

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/51475



## Problem



**Is this a BUG REPORT or FEATURE REQUEST?**: 

/kind feature

**What happened**:
```
kubectl create configmap my-cmap --from-file=file.txt --dry-run --output=yaml > my-cmap.yaml
Unable to connect to the server: dial tcp: lookup REDACDTED on REDACTED: no such host
```

**What you expected to happen**:
Ideally, I expect that no connection to the Kubernetes API server should be needed to create a ConfigMap with `--dry-run`.

**How to reproduce it (as minimally and precisely as possible)**:
Run the above command with no connection to a Kubernetes cluster.

**Anything else we need to know?**:
https://github.com/kubernetes/kubernetes/issues/11488 is a related issue that mentions that we need to decide if `--dry-run` should or should not require server-side connection. In this case for running `--dry-run` to create and save YAMLs, we should not need API server connection. It seems like an API server connection should only be needed if both `--dry-run` and `--validate` are used to validate the manifest against the API server and not apply the manifest.

**Environment**:
- Kubernetes version (use `kubectl version`):
```
Client Version: version.Info{Major:"1", Minor:"6", GitVersion:"v1.6.2", GitCommit:"477efc3cbe6a7effca06bd1452fa356e2201e1ee", GitTreeState:"clean", BuildDate:"2017-04-19T20:33:11Z", GoVersion:"go1.7.5", Compiler:"gc", Platform:"linux/amd64"}
```
- Cloud provider or hardware configuration**: n/a
- OS (e.g. from /etc/os-release): n/a
- Kernel (e.g. `uname -a`): n/a
- Install tools: n/a
- Others: n/a



## Curated Answers



### High Signal Answer 1

/remove-lifecycle stale

so I have another use case for running without a connection to a cluster and that is validating yaml files that have been generated through templating in a CI pipeline without needing to configure that pipeline to connect to any cluster it may/may not have access to

- Author: reefbarman
- Quality score: 14
- URL: https://github.com/kubernetes/kubernetes/issues/51475#issuecomment-440391827

### High Signal Answer 2

Seems like we want the --local flag.
On Mon, Oct 23, 2017 at 1:57 PM Guilhem Lettron <notifications@github.com>
wrote:

> We have same problem here with kubectl create secret generic.
> Even if we specify --dry-run=true --validate=false, command fail with Unable
> to connect to the server.
>
> We only want to some files without having to configure a running cluster.
>
> —
> You are receiving this because you were mentioned.
> Reply to this email directly, view it on GitHub
> <https://github.com/kubernetes/kubernetes/issues/51475#issuecomment-338743815>,
> or mute the thread
> <https://github.com/notifications/unsubscribe-auth/ABmslkbGo7eTSH7z3UT2WaOxm44ajTiyks5svNOYgaJpZM4PFDtw>
> .
>

- Author: julianvmodesto
- Quality score: 7
- URL: https://github.com/kubernetes/kubernetes/issues/51475#issuecomment-338843740
