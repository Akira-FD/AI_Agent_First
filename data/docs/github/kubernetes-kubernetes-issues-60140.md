# kubectl cp fails on large files 



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #60140

- State: closed

- Labels: kind/bug, sig/node, sig/cli, triage/accepted

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/60140



## Problem



<!-- This form is for bug reports and feature requests ONLY! 

If you're looking for help check [Stack Overflow](https://stackoverflow.com/questions/tagged/kubernetes) and the [troubleshooting guide](https://kubernetes.io/docs/tasks/debug-application-cluster/troubleshooting/).
-->

**Is this a BUG REPORT or FEATURE REQUEST?**:

/kind bug

**What happened**:
Copying either a large file, or a large directory from a container via `kubectl cp` results in the error of `error: unexpected EOF` and a failure to transfer.  In my case, the file is 1.7G.

I executed the following command

```bash
kubectl cp infra-cassandra-global-0:cassandra.tar.gz infra-cassandra-global-0-cassandra.tar.gz
```

The command executes, however the terminal will print the error below after 10-14 seconds of execution, and no file is copied. 

```bash
error: unexpected EOF
```


**What you expected to happen**:

The large file to be downloaded from the container.

**How to reproduce it (as minimally and precisely as possible)**:

Add a large file >= 1.7G to any location in the pod.  I was able to re-create this will the file on a PV, or locally on the image file system. 

Execute `kubectl cp` to download the large file.  It will fail.

**Anything else we need to know?**:

**Environment**:
- Kubernetes version (use `kubectl version`): v1.8.6, client v1.8.5
- Cloud provider or hardware configuration: AWS
- OS (e.g. from /etc/os-release): k8s-1.8-debian-jessie-amd64-hvm-ebs-2017-12-02 (ami-06a57e7e)
- Kernel (e.g. `uname -a`):
- Install tools: Kops
- Others:



## Curated Answers



### High Signal Answer 1

This problem may be solved if kubectl cp would implement resumable downloads to work around temporary network errors.

- Author: purplemana
- Quality score: 44
- URL: https://github.com/kubernetes/kubernetes/issues/60140#issuecomment-470432939

### High Signal Answer 2

I found the issue here in our environment.  We had blocked ICMP packets in the SG attached to the ENI of our API ELB (CLB these days).  This meant that requests to fragment large packets were not getting back to the ELB.  Because of that, the packet was never re-sent by the ELB, which meant it was lost.  This breaks the TCP session and the connection resets.

In short, make sure that ICMP is allowed between your Load Balancer and your hosts, and your MTU settings are correctly calibrated.

- Author: integrii
- Quality score: 19
- URL: https://github.com/kubernetes/kubernetes/issues/60140#issuecomment-393751563

### High Signal Answer 3

I ended up splitting the file into 500mb chunks and copied over each chunk 1 at a time and it worked fine. 

`split ./largeFile.bin -b 500m part.`
copy all of the files
`kubectl cp <pod>:<path_to_part.aa> part.aa`
Then reassemble with cat
`cat part* > largeFile.bin`
 I suggest you use a checksum to validate the files integrity once you are done

- Author: MicahRam
- Quality score: 18
- URL: https://github.com/kubernetes/kubernetes/issues/60140#issuecomment-673060019
