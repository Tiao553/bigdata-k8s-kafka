terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "1.22.2"
    }
  }
}

variable "do_token" {default = "ADD Your TOKEN"}

provider "digitalocean" {
  token = var.do_token
}