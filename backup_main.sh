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
resource "aws_security_group" "db_security_group" {
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

# Create a CodeCommit repository named c12-joshua-pharmazer-pipeline
resource "aws_codecommit_repository" "repo" {
  repository_name = "c12-joshua-pharmazer-pipeline"
  description     = "Code repository for c12-joshua-pharmazer pipeline"

  tags = {
    Name = "c12-joshua-pharmazer-pipeline"
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
  name = "ecs_task_execution_role"

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

  # Use a default managed policy for ECS task execution role
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
  ]
}

# Define the ECS task definition
resource "aws_ecs_task_definition" "task" {
  family                   = "c12-joshua-pharmazer-task"
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

# Run the ECS service
resource "aws_ecs_service" "service" {
  name            = "c12-joshua-pharmazer-service"
  cluster         = var.ECS_CLUSTER
  task_definition = aws_ecs_task_definition.task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.SUBNETS
    security_groups = [aws_security_group.db_security_group.id]
  }

}

# Output the ECR repository URI
output "ecr_repository_url" {
  value       = aws_ecr_repository.ecr_repo.repository_url
  description = "The URL of the ECR repository"
}
