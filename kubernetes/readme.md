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
ARGOCD_LB="138.197.60.161"
kubens cicd && k get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d | xargs -t -I {} argocd login $ARGOCD_LB --username admin --password {} --insecure

# create cluster role binding for admin user [sa]
k create clusterrolebinding cluster-admin-binding --clusterrole=cluster-admin --user=system:serviceaccount:cicd:argocd-application-controller -n cicd

# register cluster
CLUSTER="do-nyc3-poc-kafka-k8s"
argocd cluster add $CLUSTER --in-cluster

# add repo into argo-cd repositories
REPOSITORY="https://github.com/Tiao553/bigdata-k8s-kafka.git"
argocd repo add $REPOSITORY --username [NAME] --password [PWD] --port-forward
```
> In this point all updates on your repository apply your yaml map to argoCD. If prefer you can individual apply yaml, how show below: (obs: You need execute only time this commands, after update repo to argoCD apply YAMLs)


# Load balancer

```sh
k apply -f kubernetes/app-manifests/misc/load-balancers-svc.yaml
```

# Ingestion
```
k apply -f kubernetes/app-manifests/ingestion/kafka-broker.yaml 
k apply -f kubernetes/app-manifests/ingestion/schema-registry.yaml 
k apply -f kubernetes/app-manifests/ingestion/kafka-connect.yaml 
k apply -f kubernetes/app-manifests/ingestion/cruise-control.yaml 
k apply -f kubernetes/app-manifests/ingestion/kafka-connectors.yaml 
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
k apply -f kubernetes/app-manifests/processing/ksqldb.yaml
```

## Acess to ksqlDB
```sh
# access ksqldb server
KSQLDB=ksqldb-server-5dbf5c69bb-j7dkv
k exec $KSQLDB -n processing -i -t -- bash ksql

# set latest offset read
SET 'auto.offset.reset' = 'earliest';
SET 'auto.offset.reset' = 'latest';

# show info
SHOW TOPICS;
SHOW STREAMS;
SHOW TABLES;
SHOW QUERIES;
```

## Task definition in ksqlDB

 1. In our application we are going to create an event stream for the events that come from the mongo db and therefore we are going to put it into a table to be picked up by minio and pinot.

 2. For the postgres database we will already create a table where we will perform the treatment and make the data available in a table.

# Deep storage

```sh
k apply -f kubernetes/app-manifests/deepstorage/minio-operator.yaml
```

To make use of minio you need to expose a gateway to the cluster, the so-called port-forward.  To do this, we either use a tool to manage this or we create another prompt because the access runs until the prompt is interrupted and to generate the access we use the following code:

[documentation](https://kubernetes.io/docs/tasks/access-application-cluster/port-forward-access-application-cluster/)

```sh
kubectl port-forward service/console-minio 8087:9090
```

## to get your password access type on prompt

```sh
k get secret $(k get serviceaccount console-sa --namespace deepstorage -o jsonpath="{.secrets[0].name}") --namespace deepstorage -o jsonpath="{.data.token}" | base64 --decode
```


# Datastore

```sh
k apply -f kubernetes/app-manifests/datastore/pinot.yaml
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

# Deployed apps

```sh
k get applications -n cicd
```

## To delete all application with command line
```sh
k delete application.argoproj.io --all
```

## or only appication
```sh
k delete application.argoproj.io/kubecost
```