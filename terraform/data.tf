data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  owners = ["099720109477"]
}

data "http" "myip" {
  url = "https://checkip.amazonaws.com/"
}

data "aws_region" "current" {}

data "aws_caller_identity" "current" {}