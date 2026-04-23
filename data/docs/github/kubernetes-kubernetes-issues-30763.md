# Add support for fish shell autocompletion



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #30763

- State: closed

- Labels: area/kubectl, priority/awaiting-more-evidence, size/M, sig/cli

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/30763



## Problem



**FEATURE REQUEST**:

[Fish shell](https://fishshell.com) is a relatively new modern interactive user friendly command line shell. It really shines at user friendly features like visual tab completion menus, live syntax highlighting and other useful features.

`kubectl` has a massive set of sub-commands and options. Remembering all those is a chore. Specially when getting to know Kubernetes. All the help is appreciated.

Please provide autocompletion support for fish shell in addition to bash and zsh.

Thanks

**Kubernetes version** (use `kubectl version`):

```
Client Version: version.Info{Major:"1", Minor:"3", GitVersion:"v1.3.4+dd6b458", GitCommit:"dd6b458ef8dbf24aff55795baa68f83383c9b3a9", GitTreeState:"not a git tree", BuildDate:"2016-08-04T09:44:57Z", GoVersion:"go1.6.3", Compiler:"gc", Platform:"darwin/amd64"}
The connection to the server localhost:8080 was refused - did you specify the right host or port?
```

**Environment**:
**Others**: Fish shell



## Curated Answers



### High Signal Answer 1

Found these via a Google search in the meantime:
- https://github.com/evanlucas/fish-kubectl-completions
- https://gist.github.com/terlar/28e1c2e4ac9a27be7a5950306bf45ab2

- Author: zx8
- Quality score: 18
- URL: https://github.com/kubernetes/kubernetes/issues/30763#issuecomment-293521521
