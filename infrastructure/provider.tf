terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "1.22.2"
    }
  }
}

variable "do_token" {default = "ae3e380048ead11c08410bd90d647b4fda98648512fd30ce2400d1ae3d85db08"}

provider "digitalocean" {
  token = var.do_token
}