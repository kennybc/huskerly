# Configure AWS provider
provider "aws" {
  region = "us-east-2"
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.6.2"
    }
  }
  backend "s3" {
    bucket         = "huskerly-terraform-state"
    dynamodb_table = "huskerly-terraform-lock"
    key            = "terraform.tfstate"
    region         = "us-east-2"
    encrypt        = true
  }
}