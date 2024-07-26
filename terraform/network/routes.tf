# Resource: aws_route_table
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route_table
resource "aws_route_table" "huskerly-rt-private" {
  vpc_id = aws_vpc.huskerly-vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_nat_gateway.huskerly-nat.id
  }

  tags = {
    Name = "huskerly-rt-private"
  }
}

resource "aws_route_table" "huskerly-rt-public" {
  vpc_id = aws_vpc.huskerly-vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.huskerly-igw.id
  }

  tags = {
    Name = "huskerly-rt-public"
  }
}

# Resource: aws_route_table_association
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route_table_association
resource "aws_route_table_association" "huskerly-private-a" {
  subnet_id = aws_subnet.huskerly-private-a.id
  route_table_id = aws_route_table.huskerly-rt-private.id
}

resource "aws_route_table_association" "huskerly-private-b" {
  subnet_id = aws_subnet.huskerly-private-b.id
  route_table_id = aws_route_table.huskerly-rt-private.id
}

resource "aws_route_table_association" "huskerly-public-a" {
  subnet_id = aws_subnet.huskerly-public-a.id
  route_table_id = aws_route_table.huskerly-rt-public.id
}

resource "aws_route_table_association" "huskerly-public-b" {
  subnet_id = aws_subnet.huskerly-public-b.id
  route_table_id = aws_route_table.huskerly-rt-public.id
}