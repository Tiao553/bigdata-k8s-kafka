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

# Install on namespace ingestion

```sh
helm install kafka strimzi/strimzi-kafka-operator --namespace ingestion --version 0.26.0
```

# Run config maps for to get metrics on kafka
```sh
# config maps
k apply -f kubernetes/yamls/ingestion/metrics/kafka-metrics-config.yaml -n ingestion
k apply -f kubernetes/yamls/ingestion/metrics/zookeeper-metrics-config.yaml -n ingestion
k apply -f kubernetes/yamls/ingestion/metrics/connect-metrics-config.yaml -n ingestion
k apply -f kubernetes/yamls/ingestion/metrics/cruise-control-metrics-config.yaml -n ingestion
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
k apply -f kubernetes/app-manifests/ingestion/kafka-broker.yaml -n ingestion
k apply -f kubernetes/app-manifests/ingestion/schema-registry.yaml -n ingestion
k apply -f kubernetes/app-manifests/ingestion/kafka-connect.yaml -n ingestion
k apply -f kubernetes/app-manifests/ingestion/cruise-control.yaml -n ingestion
k apply -f kubernetes/app-manifests/ingestion/kafka-connectors.yaml -n ingestion
```

## To consume data into kafka connect source topics
```sh
k exec schema-registry-cp-schema-registry-7fcc6d9b49-q28p9 -c cp-schema-registry-server -i -t -- bash

# unset the jmx port to use consume command lines
unset JMX_PORT;

# mongodb patter
kafka-avro-console-consumer \
--bootstrap-server edh-kafka-bootstrap:9092 \
--property schema.registry.url=http://localhost:8081 \
--property print.key=true \
--topic src.mongodb.admin.[collection]

# postgres jdbc pattern
kafka-avro-console-consumer \
--bootstrap-server edh-kafka-bootstrap:9092 \
--property schema.registry.url=http://localhost:8081 \
--property print.key=true \
--topic src-postgres-[table]-avro
```

# Processing

```sh
k apply -f kubernetes/app-manifests/processing/ksqldb.yaml -n processing
```

##

# Deep storage

```sh
k apply -f kubernetes/app-manifests/deepstorage/minio-operator.yaml -n deepstorage
```

## to get your password access type on prompt

```sh
k get secret $(k get serviceaccount console-sa --namespace deepstorage -o jsonpath="{.secrets[0].name}") --namespace deepstorage -o jsonpath="{.data.token}" | base64 --decode
```

# Datastore

```sh
k apply -f kubernetes/app-manifests/datastore/pinot.yaml -n datastore
```

# Data ops

```sh
k apply -f kubernetes/app-manifests/lenses/lenses.yaml
```

# Monitoring

```sh
k apply -f kubernetes/app-manifests/monitoring/prometheus-alertmanager-grafana-botkube.yaml
```

# Logging

```sh
k apply -f kubernetes/app-manifests/logging/elasticsearch.yaml
k apply -f kubernetes/app-manifests/logging/filebeat.yaml
k apply -f kubernetes/app-manifests/logging/kibana.yaml
```

# Cost

```sh
k apply -f kubernetes/app-manifests/cost/kubecost.yaml
```

# Load balancer

```sh
k apply -f kubernetes/app-manifests/misc/load-balancers-svc.yaml
```

# Deployed apps

```sh
k get applications -n cicd
```