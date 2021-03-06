https://docs.digitalocean.com/reference/doctl/how-to/install/
https://docs.digitalocean.com/reference/
https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs

```sh
# digital ocean

# install doctl
brew install doctl
brew upgrade doctl
doctl --help

# api token for access
https://cloud.digitalocean.com/account/api/tokens?i=41b6a9
https://docs.digitalocean.com/reference/api/create-personal-access-token/

# authentication process
# token = []
doctl auth list
doctl auth init

# kubernetes info
doctl kubernetes cluster
doctl kubernetes options sizes
doctl kubernetes cluster list
doctl kubernetes cluster node-pool list []

# get cluster context
doctl kubernetes cluster kubeconfig save []

# remove cluster on kubeconfig
kubectl config delete-cluster [cluster]
kubectl config delete-context [cluster] 
```

```shell
# access iac terraform script/

# init terraform script process
# prepare working directory
terraform init

# build plan to build
# changes required
terraform plan

# apply creation iac code
# create resources
terraform apply -auto-approve

# access cluster
# kubernetes aks engine
doctl kubernetes cluster list
doctl kubernetes cluster node-pool list []

# Need register cluster on kubeconfig local
doctl kubernetes cluster kubeconfig save [id_clustes]

# change [variables.tf]
terraform plan
terraform apply

# remove resources [rg]
# destroy resources
terraform destroy -auto-approve

```
