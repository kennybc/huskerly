# create dynamodb table with LockID as key
resource "aws_dynamodb_table" "huskerly-terraform-lock" {
  name         = "huskerly-terraform-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
