# CVE-2021-25742: Ingress-nginx custom snippets allows retrieval of ingress-nginx serviceaccount token and secrets across all namespaces



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #126811

- State: closed

- Labels: kind/bug, priority/critical-urgent, area/security, lifecycle/frozen, committee/security-response, triage/accepted, official-cve-feed

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/126811



## Problem



### Issue Details
A security issue was discovered in ingress-nginx where a user that can create or update ingress objects can use the custom snippets feature to obtain all secrets in the cluster.

This issue has been rated **High** ([CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L](https://www.first.org/cvss/calculator/3.1#CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L)), and assigned **CVE-2021-25742**.

### Affected Components and Configurations
This bug affects ingress-nginx.

Multitenant environments where non-admin users have permissions to create Ingress objects are most affected by this issue.

#### Affected Versions with no mitigation

- v1.0.0
- <= v0.49.0

#### Versions allowing mitigation
This issue cannot be fixed solely by upgrading ingress-nginx. It can be mitigated in the following versions:
- v1.0.1
- v0.49.1

### Mitigation
To mitigate this vulnerability:
1. Upgrade to a version that allows mitigation, (>= v0.49.1 or >= v1.0.1)
2. Set [allow-snippet-annotations](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/configmap/#allow-snippet-annotations) to false in your ingress-nginx ConfigMap based on how you deploy ingress-nginx:

    **Static Deploy Files** 
    Edit the ConfigMap for ingress-nginx **after** deployment:
    ```
    kubectl edit configmap -n ingress-nginx ingress-nginx-controller
    ```
    Add directive:
    ````
    data:
      allow-snippet-annotations: “false”
     ````
    More information on the ConfigMap [here](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/configmap/) 

    **Deploying Via Helm**
    Set `controller.allowSnippetAnnotations` to `false` in the Values.yaml or add the directive to the helm deploy:
    ```
    helm install [RELEASE_NAME] --set controller.allowSnippetAnnotations=false ingress-nginx/ingress-nginx
    ````

    [https://github.com/kubernetes/ingress-nginx/blob/controller-v1.0.1/charts/ingress-nginx/values.yaml#L76](https://github.com/kubernetes/ingress-nginx/blob/controller-v1.0.1/charts/ingress-nginx/values.yaml#L76)

### Detection
If you find evidence that this vulnerability has been exploited, please contact security@kubernetes.io
Additional Details
See ingress-nginx Issue kubernetes/kubernetes#126811 for more details.

### Acknowledgements
This vulnerability was reported by Mitch Hulscher.

Thank You,
CJ Cullen on behalf of the Kubernetes Security Response Committee



## Curated Answers



### High Signal Answer 1

Well [Kubescape](https://github.com/armosec/kubescape) already came out with a control that will detect whether your cluster has this vulnerability

![image](https://user-images.githubusercontent.com/64066841/138477873-a7160888-28cc-4b2e-8ae6-1bfd81cc685e.png)

- Author: dwertent
- Quality score: 22
- URL: https://github.com/kubernetes/kubernetes/issues/126811#issuecomment-2298827670

### High Signal Answer 2

Might be obvious to others but there's an actually FIX coming right ? The final fix isn't removing a feature ?

- Author: Typositoire
- Quality score: 17
- URL: https://github.com/kubernetes/kubernetes/issues/126811#issuecomment-2298827601

### High Signal Answer 3

Happy to see this is now public information! Where I am currently working we can not simply disable the custom-snippets, we have been relying on them for too long. Instead, we came up with a crude opa-gatekeeper policy to prevent our developers from injecting nginx lua-directives. If someone has a better solution then I would love to see it.

```rego
package ingressnginxunsafesnippets

operations = {"CREATE", "UPDATE"}

kind = {"Ingress"}

violation[{"msg": msg}] {
	operations[input.review.operation]
	kind[input.review.kind.kind]

	ingress_snippet_unsafe(input.review.object.metadata.annotations)

	msg := sprintf("invalid ingress '%v/%v' contains unsafe directive(s) in custom nginx snippet", [input.review.object.metadata.namespace, input.review.object.metadata.name])
}

# Prevent injecting custom lua-code

ingress_snippet_unsafe(annotations) {
	contains(annotations["nginx.ingress.kubernetes.io/server-snippet"], "_lua")
}

ingress_snippet_unsafe(annotations) {
	contains(annotations["nginx.ingress.kubernetes.io/server-snippet"], "lua_")
}

ingress_snippet_unsafe(annotations) {
	contains(annotations["nginx.ingress.kubernetes.io/configuration-snippet"], "_lua")
}

ingress_snippet_unsafe(annotations) {
	contains(annotations["nginx.ingress.kubernetes.io/configuration-snippet"], "lua_")
}

# Prevent refering to files at /run/secrets/kubernetes.io

ingress_snippet_unsafe(annotations) {
	contains(annotations["nginx.ingress.kubernetes.io/server-snippet"], "kubernetes.io")
}

ingress_snippet_unsafe(annotations) {
	contains(annotations["nginx.ingress.kubernetes.io/configuration-snippet"], "kubernetes.io")
}

```

- Author: mhulscher
- Quality score: 12
- URL: https://github.com/kubernetes/kubernetes/issues/126811#issuecomment-2298827862
