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
      "ecr:GetAuthorizationToken",
    ]
    resources = ["*"]
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
      "ecr:BatchGetImage",
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:GetDownloadUrlForLayer",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart"
    ]
    resources = [aws_ecr_repository.huskerly-repository.arn]
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