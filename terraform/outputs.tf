output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "ecr_web_repository_url" {
  description = "ECR repository URL for web app"
  value       = aws_ecr_repository.notes_web.repository_url
}
