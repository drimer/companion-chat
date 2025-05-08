# companion-chat

Companion Chat app - for all your needs

# Manual steps needed before using any script

1. Create an S3 bucket with the name `companion-chat-terraform-state`.

2. Create a user for Terraform and attach the following policy:
   
```json
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "VisualEditor0",
			"Effect": "Allow",
			"Action": [
				"s3:*",
				"dynamodb:*"
			],
			"Resource": "*"
		}
	]
}
```


# Processes requiring manual intervention

## Deployment

For now, it's manual. This will need to be part of a pipeline later:

```shell
terraform plan
terraform apply
```