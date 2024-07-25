resource "aws_iam_role" "huskerly-role-nodes" {
  name = "huskerly-role-nodes"

  assume_role_policy = jsonencode({
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
    Version = "2012-10-17"
  })
}

resource "aws_iam_role_policy_attachment" "huskerly-role-nodes-AmazonEKSWorkerNodePolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.huskerly-role-nodes.name
}

resource "aws_iam_role_policy_attachment" "huskerly-role-nodes-AmazonEKS_CNI_Policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.huskerly-role-nodes.name
}

resource "aws_iam_role_policy_attachment" "huskerly-role-nodes-AmazonEC2ContainerRegistryReadOnly" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.huskerly-role-nodes.name
}

# Resource: aws_eks_node_group
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eks_node_group
resource "aws_eks_node_group" "huskerly-nodes" {
  cluster_name    = aws_eks_cluster.huskerly-cluster.name
  node_group_name = "huskerly-nodes"
  node_role_arn   = aws_iam_role.huskerly-role-nodes.arn

  subnet_ids = [
    aws_subnet.huskerly-private-a.id,
    aws_subnet.huskerly-private-b.id
  ]

  capacity_type  = "ON_DEMAND"
  instance_types = ["t3.small"]

  scaling_config {
    desired_size = 2
    max_size     = 5
    min_size     = 1
  }

  update_config {
    max_unavailable = 1
  }

  # Ensure that IAM Role permissions are created before and deleted after EKS Node Group handling.
  # Otherwise, EKS will not be able to properly delete EC2 Instances and Elastic Network Interfaces.
  depends_on = [
    aws_iam_role_policy_attachment.huskerly-role-nodes-AmazonEC2ContainerRegistryReadOnly,
    aws_iam_role_policy_attachment.huskerly-role-nodes-AmazonEKS_CNI_Policy,
    aws_iam_role_policy_attachment.huskerly-role-nodes-AmazonEC2ContainerRegistryReadOnly,
  ]
}