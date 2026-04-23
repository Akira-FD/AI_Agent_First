# Create a kubeadm installer container for CoreOS



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #34134

- State: closed

- Labels: sig/cluster-lifecycle, area/kubeadm

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/34134



## Problem



And other platforms that may not have deb/rpm installation support



## Curated Answers



### High Signal Answer 1

OK, I got kubeadm working on CoreOS quite easily while travelling back from KubeCon :smile:
Here's how to do it:

``` bash
K8S_VERSION=v1.4.4
CNI_RELEASE=07a8a28637e97b22eb8dfe710eeae1344f69d16e

mkdir -p /opt/cni /opt/bin
curl -sSL https://storage.googleapis.com/kubernetes-release/release/${K8S_VERSION}/bin/linux/amd64/kubectl > /opt/bin/kubectl
curl -sSL https://storage.googleapis.com/kubernetes-release-dev/ci-cross/v1.5.0-alpha.2.421+a6bea3d79b8bba/bin/linux/amd64/kubeadm > /opt/bin/kubeadm
chmod +x /opt/bin/kubectl /opt/bin/kubeadm
curl -sSL https://storage.googleapis.com/kubernetes-release/network-plugins/cni-amd64-${CNI_RELEASE}.tar.gz | tar xz -C /opt/cni/
cat > /etc/systemd/system/kubelet.service <<EOF
[Unit]
Description=kubelet: The Kubernetes Node Agent
Documentation=http://kubernetes.io/docs/

[Service]
Environment=KUBELET_VERSION=${K8S_VERSION}_coreos.0
ExecStart=/usr/lib/coreos/kubelet-wrapper --kubeconfig=/etc/kubernetes/kubelet.conf --require-kubeconfig=true --pod-manifest-path=/etc/kubernetes/manifests --allow-privileged=true --network-plugin=cni --cni-conf-dir=/etc/cni/net.d --cni-bin-dir=/opt/cni/bin --cluster-dns=10.96.0.10 --cluster-domain=cluster.local
Restart=always
StartLimitInterval=0
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable docker kubelet
systemctl restart docker kubelet
```

Since CoreOS is missing `socat` on host, kubeadm preflight will stop the user from running init|join, so they must use `--skip-preflight-checks` like this `kubeadm init --skip-preflight-checks`.
We might consider making socat a soft dep for kubeadm, since kubelet will work, but not port-forwarding and such networking features. On CoreOS, we're running the kubelet in a rkt fly environment where socat exists, so it's ok.

I've already made an installer container for all oses here, we should consider making it "core": https://github.com/luxas/kubeadm-installer

How to install it on CoreOS for example:

```
docker run -it -v /etc/cni:/etc/cni -v /etc/systemd:/etc/systemd -v /opt:/opt -v /usr/bin:/usr/bin luxas/kubeadm-installer coreos
```

Feel free to test it out :smile: 
We should at least document these steps on CoreOS, as they differ from all other OSes.

cc @kubernetes/sig-cluster-lifecycle

- Author: luxas
- Quality score: 11
- URL: https://github.com/kubernetes/kubernetes/issues/34134#issuecomment-260252981

### High Signal Answer 2

Correct way to run...

 docker run -it -v /etc/cni:/rootfs/etc/cni -v /etc/systemd:/rootfs/etc/systemd -v /opt:/rootfs/opt -v /usr/bin:/rootfs/usr/bin luxas/kubeadm-installer coreos

- Author: waynebrantley
- Quality score: 8
- URL: https://github.com/kubernetes/kubernetes/issues/34134#issuecomment-260479941
