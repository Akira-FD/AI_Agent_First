# application crash due to k8s 1.9.x open the kernel memory accounting by default



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #61937

- State: closed

- Labels: kind/support, sig/node, needs-triage

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/61937



## Problem



when we upgrade the k8s from 1.6.4 to 1.9.0,  after a few days,  the product environment report the machine is hang and jvm crash in container randomly , we found the cgroup memory css id is not release, when cgroup css id is large than 65535, the machine is hang, we must restart the machine. 

we had found runc/libcontainers/memory.go in k8s 1.9.0 had delete the if condition,  which cause the kernel memory open by default, but we are using kernel 3.10.0-514.16.1.el7.x86_64,  on this version, kernel memory limit is not stable, which leak the cgroup memory leak and application crash randomly

when we run  "docker run -d --name test001 --kernel-memory 100M  " , docker report 
WARNING: You specified a kernel memory limit on a kernel older than 4.0. Kernel memory limits are experimental on older kernels, it won't work as expected and can cause your system to be unstable.
 

```
k8s.io/kubernetes/vendor/github.com/opencontainers/runc/libcontainer/cgroups/fs/memory.go

-		if d.config.KernelMemory != 0 {
+			// Only enable kernel memory accouting when this cgroup
+			// is created by libcontainer, otherwise we might get
+			// error when people use `cgroupsPath` to join an existed
+			// cgroup whose kernel memory is not initialized.
 			if err := EnableKernelMemoryAccounting(path); err != nil {
 				return err
 			}
```
I want to know why kernel memory open by default?  can k8s consider the different kernel version?

**Is this a BUG REPORT or FEATURE REQUEST?**: BUG REPORT

> Uncomment only one, leave it on its own line: 
>
> /kind bug
> /kind feature


**What happened**:
application crash and cgroup memory leak

**What you expected to happen**:
application stable and cgroup memory doesn't leak

**How to reproduce it (as minimally and precisely as possible)**:
install k8s 1.9.x on kernel 3.10.0-514.16.1.el7.x86_64 machine, and create and delete pod repeatedly,  when create more than 65535/3 times , the kubelet report "cgroup no space left on device" error,  when the cluster run a few days , the container will crash. 

**Anything else we need to know?**:

**Environment**: kernel 3.10.0-514.16.1.el7.x86_64   
- Kubernetes version (use `kubectl version`): k8s 1.9.x
- Cloud provider or hardware configuration: 
- OS (e.g. from /etc/os-release):  
```
NAME="CentOS Linux"
VERSION="7 (Core)"
ID="centos"
ID_LIKE="rhel fedora"
VERSION_ID="7"
PRETTY_NAME="CentOS Linux 7 (Core)"
ANSI_COLOR="0;31"
CPE_NAME="cpe:/o:centos:centos:7"
HOME_URL="https://www.centos.org/"
BUG_REPORT_URL="https://bugs.centos.org/"

CENTOS_MANTISBT_PROJECT="CentOS-7"
CENTOS_MANTISBT_PROJECT_VERSION="7"
REDHAT_SUPPORT_PRODUCT="centos"
REDHAT_SUPPORT_PRODUCT_VERSION="7"
```
- Kernel (e.g. `uname -a`):  3.10.0-514.16.1.el7.x86_64 
- Install tools: rpm 
- Others:



## Curated Answers



### High Signal Answer 1

Not only 1.9, but also 1.10 and master have same issue. This is a very serious issue for production, I think providing a parameter to disable kmem limit is good.

/cc @dchen1107 @thockin any comments for this? Thanks.

- Author: gyliu513
- Quality score: 17
- URL: https://github.com/kubernetes/kubernetes/issues/61937#issuecomment-381472045

### High Signal Answer 2

Use below test case can reproduce this error:
first, make cgroup memory to be full:
```
# uname -r
3.10.0-514.10.2.el7.x86_64
# kubelet --version
Kubernetes 1.9.0
# mkdir /sys/fs/cgroup/memory/test
# for i in `seq 1 65535`;do mkdir /sys/fs/cgroup/memory/test/test-${i}; done
# cat /proc/cgroups |grep memory
memory  11      65535   1
```
then release 99 cgroup memory that can be used next to create:
```
# for i in `seq 1 100`;do rmdir /sys/fs/cgroup/memory/test/test-${i} 2>/dev/null 1>&2; done 
# mkdir /sys/fs/cgroup/memory/stress/
# for i in `seq 1 100`;do mkdir /sys/fs/cgroup/memory/test/test-${i}; done 
mkdir: cannot create directory ‘/sys/fs/cgroup/memory/test/test-100’: No space left on device <-- notice number 100 can not create
# for i in `seq 1 100`;do rmdir /sys/fs/cgroup/memory/test/test-${i}; done <-- delete 100 cgroup memory
# cat /proc/cgroups |grep memory
memory  11      65436   1
```
second, create a new pod on this node.
Each pod will create 3 cgroup memory directory. for example:
```
# ll /sys/fs/cgroup/memory/kubepods/pod0f6c3c27-3186-11e8-afd3-fa163ecf2dce/
total 0
drwxr-xr-x 2 root root 0 Mar 27 14:14 6d1af9898c7f8d58066d0edb52e4d548d5a27e3c0d138775e9a3ddfa2b16ac2b
drwxr-xr-x 2 root root 0 Mar 27 14:14 8a65cb234767a02e130c162e8d5f4a0a92e345bfef6b4b664b39e7d035c63d1
```
So when we recreate 100 cgroup memory directory, there will be 4 item failed:
```
# for i in `seq 1 100`;do mkdir /sys/fs/cgroup/memory/test/test-${i}; done    
mkdir: cannot create directory ‘/sys/fs/cgroup/memory/test/test-97’: No space left on device <-- 3 directory used by pod
mkdir: cannot create directory ‘/sys/fs/cgroup/memory/test/test-98’: No space left on device
mkdir: cannot create directory ‘/sys/fs/cgroup/memory/test/test-99’: No space left on device
mkdir: cannot create directory ‘/sys/fs/cgroup/memory/test/test-100’: No space left on device
# cat /proc/cgroups 
memory  11      65439   1
```
third, delete the test pod. Recreate 100 cgroup memory directory before confirm all test pod's container are already destroy.
The correct result that we expected is only number 100 cgroup memory directory can not be create:
```
# cat /proc/cgroups 
memory  11      65436   1
# for i in `seq 1 100`;do mkdir /sys/fs/cgroup/memory/test/test-${i}; done 
mkdir: cannot create directory ‘/sys/fs/cgroup/memory/test/test-100’: No space left on device
```
But the incorrect result is all cgroup memory directory created by pod are leaked:
```
# cat /proc/cgroups 
memory  11      65436   1 <-- now cgroup memory total directory
# for i in `seq 1 100`;do mkdir /sys/fs/cgroup/memory/test/test-${i}; done    
mkdir: cannot create directory ‘/sys/fs/cgroup/memory/test/test-97’: No space left on device
mkdir: cannot create directory ‘/sys/fs/cgroup/memory/test/test-98’: No space left on device
mkdir: cannot create directory ‘/sys/fs/cgroup/memory/test/test-99’: No space left on device
mkdir: cannot create directory ‘/sys/fs/cgroup/memory/test/test-100’: No space left on device
```
Notice that cgroup memory count already reduce 3 , but they occupy space not release.

- Author: qkboy
- Quality score: 13
- URL: https://github.com/kubernetes/kubernetes/issues/61937#issuecomment-377512486
