resource "digitalocean_database_cluster" "postgres" {
    name       = "postgres-cluster"
    engine     = "pg"
    version    = "11"
    size       = "db-s-1vcpu-1gb"
    region     = "nyc1"
    node_count = 1
}