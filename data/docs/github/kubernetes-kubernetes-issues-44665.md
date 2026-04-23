# 1.6.1 The connection to the server localhost:8080 was refused



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #44665

- State: closed

- Labels: none

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/44665



## Problem



**Kubernetes version v1.6.1**


**Environment**:
- **arm64 cavium thunder x**:
- **Ubuntu 16.04.2 LTS**
- **4.4.0-72-generic**

**What happened**:
init kubernetes with
`kubeadm init --kubernetes-version=v1.6.1 --pod-network-cidr=10.244.0.0/16
`than tried
`kubectl taint nodes --all  node-role.kubernetes.io/master-
`and got this
`The connection to the server localhost:8080 was refused - did you specify the right host or port?
`

or this
```
# kubectl apply -f https://github.com/coreos/flannel/raw/master/Documentation/kube-flannel.yml
The connection to the server localhost:8080 was refused - did you specify the right host or port?
```

or

```
# kubectl version
Client Version: version.Info{Major:"1", Minor:"6", GitVersion:"v1.6.1", GitCommit:"b0b7a323cc5a4a2019b2e9520c21c7830b7f708e", GitTreeState:"clean", BuildDate:"2017-04-03T20:44:38Z", GoVersion:"go1.7.5", Compiler:"gc", Platform:"linux/arm64"}
The connection to the server localhost:8080 was refused - did you specify the right host or port?

```



## Curated Answers



### High Signal Answer 1

did you run below commands after kubeadm init

To start using your cluster, you need to run (as a regular user):

  sudo cp /etc/kubernetes/admin.conf $HOME/
  sudo chown $(id -u):$(id -g) $HOME/admin.conf
  export KUBECONFIG=$HOME/admin.conf

- Author: csarora
- Quality score: 590
- URL: https://github.com/kubernetes/kubernetes/issues/44665#issuecomment-295216655

### High Signal Answer 2

I didn't have `admin.conf`  
Did I miss something?

- Author: Rukeith
- Quality score: 131
- URL: https://github.com/kubernetes/kubernetes/issues/44665#issuecomment-312420325

### High Signal Answer 3

Reproduce the same error when doing a tutorial from Udacity called Scalable Microservices with Kubernetes https://classroom.udacity.com/courses/ud615, at the point of Using Kubernetes, Part 3 of Lesson.

Launch a Single Instance:

`kubectl run nginx --image=nginx:1.10.0`

Error:

`Unable to connect to the server: dial tcp [::1]:8080: connectex: No connection could be made because the target machine actively refused it.`

How I resolved the Error:

Login to Google Cloud Platform

Navigate to Container Engine Google Cloud Platform, Container Engine

Click CONNECT on Cluster

Use login Credentials to access Cluster [NAME] in your Teminal

Proceeded With Work!!!

- Author: GoodFaithParadigm8
- Quality score: 71
- URL: https://github.com/kubernetes/kubernetes/issues/44665#issuecomment-301290042
