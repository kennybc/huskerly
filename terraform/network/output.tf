output "github-arn" {
  value = aws_iam_role.github-role.arn
  description = "The ARN of the Github role"
}

output "user-repo-arn" {
  value = aws_ecr_repository.huskerly-user-repo.repository_url
  description = "The ARN of the ECR user repository"
}

output "message-repo-arn" {
  value = aws_ecr_repository.huskerly-message-repo.repository_url
  description = "The ARN of the ECR message repository"
}

output "upload-repo-arn" {
  value = aws_ecr_repository.huskerly-upload-repo.repository_url
  description = "The ARN of the ECR upload repository"
}