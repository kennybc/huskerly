resource "aws_s3_bucket" "huskerly-terraform-state" {
  bucket = "huskerly-terraform-state"
}

# enable versioning in our S3 bucket
resource "aws_s3_bucket_versioning" "huskerly-terraform-state" {
  bucket = aws_s3_bucket.huskerly-terraform-state.id

  versioning_configuration {
    status = "Enabled"
  }
}

# encrypt state files
resource "aws_s3_bucket_server_side_encryption_configuration" "huskerly-terraform-state" {
  bucket = aws_s3_bucket.huskerly-terraform-state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# block public access
resource "aws_s3_bucket_public_access_block" "huskerly-terraform_state" {
  bucket  = aws_s3_bucket.huskerly-terraform-state.id
  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}

