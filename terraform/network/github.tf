# Github actions provider
resource "aws_iam_openid_connect_provider" "github-provider" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com",
  ]

  thumbprint_list = ["ffffffffffffffffffffffffffffffffffffffff"]
}

# Github actions role
data "aws_iam_policy_document" "github-role-doc" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github-provider.arn]
    }

    condition {
      test     = "StringEquals"
      values   = ["sts.amazonaws.com"]
      variable = "token.actions.githubusercontent.com:aud"
    }

    condition {
      test     = "StringLike"
      values   = ["repo:kennybc/*"]
      variable = "token.actions.githubusercontent.com:sub"
    }
  }
}

resource "aws_iam_role" "github-role" {
  name = "github-role"
  assume_role_policy = data.aws_iam_policy_document.github-role-doc.json
}

# Github actions policy
data "aws_iam_policy_document" "github-policy-doc" {
  statement {
    effect  = "Allow"
    actions = [
      "s3:ListBucket",
      "s3:GetObject",
      "s3:PutObject",
    ]
    resources = ["${var.s3-arn}/terraform.tfstate"]
  }

  statement {
    effect  = "Allow"
    actions = [
      "dynamodb:DescribeTable",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem"
    ]
    resources = [var.dynamodb-arn]
  }

  statement {
    effect  = "Allow"
    actions = [
      "eks:DescribeCluster",
    ]
    resources = [aws_eks_cluster.huskerly-cluster.arn]
  }

  statement {
    effect  = "Allow"
    actions = [
      "ecr:GetAuthorizationToken",
    ]
    resources = ["*"]
  }

  statement {
    effect  = "Allow"
    actions = [
      "ecr:BatchGetImage",
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:GetDownloadUrlForLayer",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart"
    ]
    resources = [
      aws_ecr_repository.huskerly-user-repo.arn,
      aws_ecr_repository.huskerly-message-repo.arn,
      aws_ecr_repository.huskerly-upload-repo.arn
    ]
  }
}

resource "aws_iam_policy" "github-policy" {
  name = "github-policy"
  policy = data.aws_iam_policy_document.github-policy-doc.json
}

resource "aws_iam_role_policy_attachment" "github-policy" {
  role = aws_iam_role.github-role.name
  policy_arn = aws_iam_policy.github-policy.arn
}

# Github actions to cluster access entry
resource "aws_eks_access_entry" "github-access-entry" {
  cluster_name = aws_eks_cluster.huskerly-cluster.name
  principal_arn = aws_iam_role.github-role.arn
  type = "STANDARD"
}

resource "aws_eks_access_policy_association" "github-access-policy" {
  cluster_name  = aws_eks_cluster.huskerly-cluster.name
  principal_arn = aws_iam_role.github-role.arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSEditPolicy"

  access_scope {
    type       = "namespace"
    namespaces = ["huskerly"]
  }
}