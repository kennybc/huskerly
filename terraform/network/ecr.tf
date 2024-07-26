# Create repos
resource "aws_ecr_repository" "huskerly-user-repo" {
  name = "huskerly-user-repo"
}

resource "aws_ecr_repository" "huskerly-message-repo" {
  name = "huskerly-message-repo"
}

resource "aws_ecr_repository" "huskerly-upload-repo" {
  name = "huskerly-upload-repo"
}

# Lifecycle policy document (only keep latest 30 images)
data "aws_ecr_lifecycle_policy_document" "huskerly-repo-policy" {
  rule {
    priority = 1

    selection {
      tag_status = "any"
      count_type = "imageCountMoreThan"
      count_number = 30
    }

    action {
      type = "expire"
    }
  }
}

# Attach policy doc to repos
resource "aws_ecr_lifecycle_policy" "huskerly-user-repo" {
  repository = aws_ecr_repository.huskerly-user-repo.name
  policy = data.aws_ecr_lifecycle_policy_document.huskerly-repo-policy.json
}

resource "aws_ecr_lifecycle_policy" "huskerly-message-repo" {
  repository = aws_ecr_repository.huskerly-message-repo.name
  policy = data.aws_ecr_lifecycle_policy_document.huskerly-repo-policy.json
}

resource "aws_ecr_lifecycle_policy" "huskerly-upload-repo" {
  repository = aws_ecr_repository.huskerly-upload-repo.name
  policy = data.aws_ecr_lifecycle_policy_document.huskerly-repo-policy.json
}
