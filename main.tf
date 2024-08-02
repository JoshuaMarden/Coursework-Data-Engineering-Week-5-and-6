# Define AWS Provider
provider "aws" {
  access_key = var.AWS_ACCESS_KEY
  secret_key = var.AWS_SECRET_KEY
  region     = var.AWS_REGION
}

# Fetch the data for VPC
data "aws_vpc" "c12-vpc" {
  id = var.VPC_ID
}

# Create a security group named c12-joshua-pharmazer-sg
resource "aws_security_group" "security_group" {
  name   = "c12-joshua-pharmazer-sg"
  vpc_id = data.aws_vpc.c12-vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "c12-joshua-pharmazer-sg"
  }
}

# Create an ECR repository named c12-joshua-pharmazer-pipeline
resource "aws_ecr_repository" "ecr_repo" {
  name = "c12-joshua-pharmazer-pipeline"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "c12-joshua-pharmazer-pipeline"
  }
}

# Define the task execution role
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "c12-joshua-ecs_task_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
  ]
}

# Define the ECS task definition
resource "aws_ecs_task_definition" "task" {
  family                   = "c12-joshua-pharmazer-pipeline-task"
  cpu                      = 256
  memory                   = 512
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "pipeline"
      image     = aws_ecr_repository.ecr_repo.repository_url
      essential = true
      portMappings = [
        {
          containerPort = 8080
          hostPort      = 8080
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs_log_group.name
          awslogs-region        = var.AWS_REGION
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

# Create a log group for ECS task logs
resource "aws_cloudwatch_log_group" "ecs_log_group" {
  name              = "/ecs/c12-joshua-pharmazer"
  retention_in_days = 5
}


# Create the EventBridge rule
resource "aws_cloudwatch_event_rule" "s3_object_created_rule" {
  name        = "c12-joshua-S3ObjectCreatedRule"
  description = "Rule: trigger ECS task on S3 object creation"
  event_pattern = jsonencode({
    "source": ["aws.s3"],
    "detail-type": ["Object Created"],
    "detail": {
      "bucket": {
        "name": [var.S3_BUCKET]
      },
      "object": {
        "key": [{
          "prefix": "c12-joshua"
        }]
      }
    }
  })
}

# Create a target for the EventBridge rule to trigger the ECS task
resource "aws_cloudwatch_event_target" "ecs_task_target" {
  rule = aws_cloudwatch_event_rule.s3_object_created_rule.name
  arn  = "arn:aws:ecs:eu-west-2:129033205317:cluster/c12-ecs-cluster"

  ecs_target {
    task_definition_arn = aws_ecs_task_definition.task.arn
    launch_type         = "FARGATE"
    network_configuration {
      subnets         = var.SUBNETS
      assign_public_ip = true
      security_groups = [aws_security_group.security_group.id]
    }
  }

  role_arn = aws_iam_role.ecs_task_execution_role.arn
}

# Output the ECR repository URI
output "ecr_repository_url" {
  value       = aws_ecr_repository.ecr_repo.repository_url
  description = "The URL of the ECR repository"
}
