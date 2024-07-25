# Resource: aws_vpc
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc
resource "aws_vpc" "huskerly-vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "huskerly-vpc"
  }
}