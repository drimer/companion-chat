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


# Setup for local development

1. Make sure you have `Docker` and `docker-compose` installed: https://docs.docker.com/compose/install/

2. Run the infrastructure with Docker:

```bash
docker-compose -f ./infra/docker-compose.yml up -d
```

3. Ensure you have AWS-CLI installed: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

4. Create the required DynamoDB tables with the following command:

```bash
aws dynamodb create-table --table-name conversations --attribute-definitions AttributeName=id,AttributeType=S --key-schema AttributeName=id,KeyType=HASH --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 --table-class STANDARD --endpoint-url http://localhost:8000
```

5. Make sure you have `poetry` installed: https://pypi.org/project/poetry/

6. To install all the dev dependencies:

```bash
poetry install
```

7. To run the server:

```bash
poetry run uvicorn src.companionchat.main:app --reload --port 4000
```


# Processes requiring manual intervention

## Deployment

Deploymnets are automated with GitHub actions, but here are some useful commands:

- Do a terraform plan locally (requires downloading deployment.zip from a GitHub action):

```bash
terraform -chdir=infra/aws/environments/dev plan -out=tfplan
```