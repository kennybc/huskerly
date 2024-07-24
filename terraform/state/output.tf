output "s3_arn" {
  value       = aws_s3_bucket.huskerly-terraform-state.arn
  description = "The ARN of the S3 bucket"
}

output "dynamodb_arn" {
  value       = aws_dynamodb_table.huskerly-terraform-lock.arn
  description = "The name of the DynamoDB table"
}