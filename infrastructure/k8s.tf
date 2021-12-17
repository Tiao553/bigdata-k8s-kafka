data "digitalocean_kubernetes_versions" "cluster" {
  version_prefix = "1.20.11-do.0"
}

resource "digitalocean_kubernetes_cluster" "do-k8s" {
  name         = "k8s-kafka-challenge-test"
  region       = "nyc3"
  auto_upgrade = true
  version      = data.digitalocean_kubernetes_versions.cluster.latest_version

  node_pool {
    name       = "challenge"
    size       = "s-2vcpu-4gb"
    node_count = 6
  }
}