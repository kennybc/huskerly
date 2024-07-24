output "github-arn" {
  value = aws_iam_role.github-role.arn
  description = "The ARN of the Github role"
}

output "repo-arn" {
  value = aws_ecr_repository.huskerly-repository.repository_url
  description = "The ARN of the ECR repository"
}