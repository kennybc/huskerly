# Resource: aws_internet_gateway
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/internet_gateway
resource "aws_internet_gateway" "huskerly-igw" {
  vpc_id = aws_vpc.huskerly-vpc.id

  tags = {
    Name = "huskerly-igw"
  }
}