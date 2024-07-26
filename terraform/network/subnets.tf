# Resource: aws_subnet
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/subnet
resource "aws_subnet" "huskerly-private-a" {
  vpc_id = aws_vpc.huskerly-vpc.id
  cidr_block = "10.0.0.0/19"
  availability_zone = "us-east-2a"

  tags = {
    "Name" = "huskerly-private-a"
    "kubernetes.io/role/internal-elb" = "1"
    "kubernetes.io/cluster/demo" = "owned"
  }
}

resource "aws_subnet" "huskerly-private-b" {
  vpc_id = aws_vpc.huskerly-vpc.id
  cidr_block = "10.0.32.0/19"
  availability_zone = "us-east-2b"

  tags = {
    "Name" = "huskerly-private-b"
    "kubernetes.io/role/internal-elb" = "1"
    "kubernetes.io/cluster/huskerly-cluster" = "owned"
  }
}

resource "aws_subnet" "huskerly-public-a" {
  vpc_id = aws_vpc.huskerly-vpc.id
  cidr_block = "10.0.64.0/19"
  availability_zone = "us-east-2a"

  tags = {
    "Name" = "huskerly-public-a"
    "kubernetes.io/role/elb" = "1"
    "kubernetes.io/cluster/huskerly-cluster" = "owned"
  }
}

resource "aws_subnet" "huskerly-public-b" {
  vpc_id = aws_vpc.huskerly-vpc.id
  cidr_block = "10.0.96.0/19"
  availability_zone = "us-east-2b"

  tags = {
    "Name" = "huskerly-public-b"
    "kubernetes.io/role/elb" = "1"
    "kubernetes.io/cluster/demo" = "owned"
  }
}