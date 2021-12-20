# Install helm, kubectx, kubens and kubectl. If you use digital ocean install doctl 

# connect into k8s cluster
```sh
kubectx do-nyc3-do-nyc3-k8s-kafka-1639158733671
```

# create namespaces

```sh
k create namespace ingestion
k create namespace processing
k create namespace datastore
k create namespace deepstorage
k create namespace tracing
k create namespace logging
k create namespace monitoring
k create namespace viz
k create namespace cicd
k create namespace app
k create namespace cost
k create namespace misc
k create namespace dataops
k create namespace gateway
```

# Install packge helm kafka 

```sh
kubens ingestion
helm repo add strimzi https://strimzi.io/charts/
helm repo update
```

# Install on namespace

```sh
helm install kafka strimzi/strimzi-kafka-operator --namespace ingestion --version 0.26.0
```

# Run config maps for to get metrics on kafka
```sh
# config maps
k apply -f kubernetes/yamls/ingestion/metrics/kafka-metrics-config.yaml
k apply -f kubernetes/yamls/ingestion/metrics/zookeeper-metrics-config.yaml
k apply -f kubernetes/yamls/ingestion/metrics/connect-metrics-config.yaml
k apply -f kubernetes/yamls/ingestion/metrics/cruise-control-metrics-config.yaml
```

# Install and config ArgoCD to deployment your applications

```sh
# add & update helm list repos
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

# install crd's [custom resources]
# argo-cd
# https://artifacthub.io/packages/helm/argo/argo-cd
# https://github.com/argoproj/argo-helm
helm install argocd argo/argo-cd --namespace cicd --version 3.26.8

# install argo-cd [gitops]
# create a load balancer
k patch svc argocd-server -n cicd -p '{"spec": {"type": "LoadBalancer"}}'

# retrieve load balancer ip
# load balancer = "159.203.145.92"
kubens cicd && kubectl get services -l app.kubernetes.io/name=argocd-server,app.kubernetes.io/instance=argocd -o jsonpath="{.items[0].status.loadBalancer.ingress[0].ip}"

# get password to log into argocd portal
ARGOCD_LB="159.203.145.92"
kubens cicd && k get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d | xargs -t -I {} argocd login $ARGOCD_LB --username admin --password {} --insecure

# create cluster role binding for admin user [sa]
k create clusterrolebinding cluster-admin-binding --clusterrole=cluster-admin --user=system:serviceaccount:cicd:argocd-application-controller -n cicd

# register cluster
CLUSTER="do-nyc3-k8s-kafka-challenge-test"
argocd cluster add $CLUSTER --in-cluster

# add repo into argo-cd repositories
REPOSITORY="https://github.com/Tiao553/bigdata-k8s-kafka.git"
argocd repo add $REPOSITORY --username [NAME] --password [PWD] --port-forward
```

# In this point all updates on your repository apply your yaml map to argoCD. If prefer you can individual apply yaml, how show below:

# Ingestion
```
k apply -f kubernetes/app-manifests/ingestion/kafka-broker.yaml
k apply -f kubernetes/app-manifests/ingestion/schema-registry.yaml
k apply -f kubernetes/app-manifests/ingestion/kafka-connect.yaml
k apply -f kubernetes/app-manifests/ingestion/cruise-control.yaml
k apply -f kubernetes/app-manifests/ingestion/kafka-connectors.yaml
```

# Deep storage
```
k apply -f kubernetes/app-manifests/deepstorage/minio-operator.yaml
```

## to get your password access type on prompt

```
k get secret $(k get serviceaccount console-sa --namespace deepstorage -o jsonpath="{.secrets[0].name}") --namespace deepstorage -o jsonpath="{.data.token}" | base64 --decode
```

# Datastore
```
k apply -f kubernetes/app-manifests/datastore/pinot.yaml
```

# Processing
```
k apply -f kubernetes/app-manifests/processing/ksqldb.yaml
```

# Data ops
```
k apply -f kubernetes/app-manifests/lenses/lenses.yaml
```

# Monitoring
```
k apply -f kubernetes/app-manifests/monitoring/prometheus-alertmanager-grafana-botkube.yaml
```

# Logging
```
k apply -f kubernetes/app-manifests/logging/elasticsearch.yaml
k apply -f kubernetes/app-manifests/logging/filebeat.yaml
k apply -f kubernetes/app-manifests/logging/kibana.yaml
```

# Cost
```
k apply -f kubernetes/app-manifests/cost/kubecost.yaml
```

# Load balancer
```
k apply -f kubernetes/app-manifests/misc/load-balancers-svc.yaml
```

# Deployed apps
```
k get applications -n cicd
```