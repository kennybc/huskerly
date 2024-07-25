resource "aws_ecr_repository" "huskerly-user-repo" {
  name = "huskerly-user-repo"
}

resource "aws_ecr_repository" "huskerly-message-repo" {
  name = "huskerly-message-repo"
}

resource "aws_ecr_repository" "huskerly-upload-repo" {
  name = "huskerly-upload-repo"
}