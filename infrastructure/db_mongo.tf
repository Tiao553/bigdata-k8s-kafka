resource "digitalocean_database_cluster" "mongodb" {
    name       = "mongo-cluster"
    engine     = "mongodb"
    version    = "4"
    size       = "db-s-1vcpu-1gb"
    region     = "nyc3"
    node_count = 1
}