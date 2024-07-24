# Resource: aws_iam_role
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role
resource "aws_iam_role" "huskerly-role-terraform" {
  name = "huskerly-role-terraform"

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "eks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

# Resource: aws_iam_role_policy_attachment
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment
resource "aws_iam_role_policy_attachment" "huskerly-role-terraform-AmazonEKSClusterPolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.huskerly-role-terraform.name
}

# Resource: aws_eks_cluster
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eks_cluster
resource "aws_eks_cluster" "huskerly-cluster" {
  name     = "huskerly-cluster"
  role_arn = aws_iam_role.huskerly-role-terraform.arn

  vpc_config {
    subnet_ids = [
      aws_subnet.huskerly-private-a.id,
      aws_subnet.huskerly-private-b.id,
      aws_subnet.huskerly-public-a.id,
      aws_subnet.huskerly-public-b.id
    ]
  }

  # Ensure that IAM Role permissions are created before and deleted after EKS Cluster handling.
  # Otherwise, EKS will not be able to properly delete EKS managed EC2 infrastructure such as Security Groups.
  depends_on = [aws_iam_role_policy_attachment.huskerly-role-terraform-AmazonEKSClusterPolicy]
}