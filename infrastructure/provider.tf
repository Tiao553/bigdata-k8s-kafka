terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "1.22.2"
    }
  }
}

variable "do_token" {default = "token"}
variable "pvt_key" {default = "private-key"}

provider "digitalocean" {
  token = var.do_token
}

data "digitalocean_ssh_key" "terraform" {
  # ls ~/.ssh/*.pub
  name = "public-ssh-key"
}
