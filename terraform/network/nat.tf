# Resource: aws_eip
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eip
resource "aws_eip" "huskerly-eip" {
  domain = "vpc"

  tags = {
    Name = "huskerly-eip"
  }
}

# Resource: aws_nat_gateway
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/nat_gateway
resource "aws_nat_gateway" "huskerly-nat" {
  allocation_id = aws_eip.huskerly-eip.id
  subnet_id     = aws_subnet.huskerly-public-a.id

  tags = {
    Name = "huskerly-nat"
  }

  # To ensure proper ordering, it is recommended to add an explicit dependency
  # on the Internet Gateway for the VPC.
  depends_on = [aws_internet_gateway.huskerly-igw]
}