# 1.6.0 kubelet fails with error "misconfiguration: kubelet cgroup driver: "cgroupfs" is different from docker cgroup driver: "systemd"



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #43805

- State: closed

- Labels: sig/node, area/kubeadm

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/43805



## Problem



kubernetes 1.6.0, installation AIO with kubeadm
centos 7.3
 when kubeadm init run, the following error gets reported and kubelet fails to start:
kubelet: error: failed to run Kubelet: failed to create kubelet: misconfiguration: kubelet cgroup driver: "cgroupfs" is different from docker cgroup driver: "systemd"



## Curated Answers



### High Signal Answer 1

kubelet's  cgroup driver  is not same with docker's cgroup driver, so I update systemd -> cgroupfs.

`vi /etc/systemd/system/kubelet.service.d/10-kubeadm.conf`
update `KUBELET_CGROUP_ARGS=--cgroup-driver=systemd`    to   `KUBELET_CGROUP_ARGS=--cgroup-driver=cgroupfs`  

restart kubelet 
run 'service kubelet restart'

everyting is ok

- Author: heartarea
- Quality score: 41
- URL: https://github.com/kubernetes/kubernetes/issues/43805#issuecomment-304442290

### High Signal Answer 2

Just to add to @heartarea 's response 

## Verify which cgroup driver dockerd is using
`docker info |grep -i cgroup`

output
 ```yaml 
Cgroup Driver: cgroupfs
```

## Verify kubeadm cgroup settings
`cat /etc/systemd/system/kubelet.service.d/10-kubeadm.conf`

## Change it to match Docker's
- `vi /etc/systemd/system/kubelet.service.d/10-kubeadm.conf`

- update `KUBELET_CGROUP_ARGS=--cgroup-driver=systemd` to `KUBELET_CGROUP_ARGS=--cgroup-driver=cgroupfs` 

restart  it
```
systemctl daemon-reload
service kubelet restart
```
# Important NOTE
you'll need to change cgroup driver also in your nodes.

## Versions
kubeadm:  v1.7.3
docker:  17.06.0-ce

- Author: jmarcos-cano
- Quality score: 41
- URL: https://github.com/kubernetes/kubernetes/issues/43805#issuecomment-320965626

### High Signal Answer 3

Seeing the same.

- Author: RichWellum
- Quality score: 26
- URL: https://github.com/kubernetes/kubernetes/issues/43805#issuecomment-290088319
