# Karpenter
module "karpenter" {
  source  = "terraform-aws-modules/eks/aws//modules/karpenter"
  version = "~> 19.0"
  
  cluster_name = module.eks.cluster_name
  
  irsa_oidc_provider_arn          = module.eks.oidc_provider_arn
  irsa_namespace_service_accounts = ["karpenter:karpenter"]
  
  create_iam_role = true
  iam_role_name   = "KarpenterNodeInstanceProfile-${module.eks.cluster_name}"
  
  tags = {
    Environment = "production"
  }
}

# Karpenter Helm Chart
resource "helm_release" "karpenter" {
  depends_on = [module.karpenter]
  
  namespace        = "karpenter"
  create_namespace = true
  
  name       = "karpenter"
  repository = "oci://public.ecr.aws/karpenter"
  chart      = "karpenter"
  version    = "v0.32.0"
  
  values = [
    <<-EOT
    settings:
      clusterName: ${module.eks.cluster_name}
      clusterEndpoint: ${module.eks.cluster_endpoint}
      interruptionQueueName: ${module.karpenter.queue_name}
    serviceAccount:
      annotations:
        eks.amazonaws.com/role-arn: ${module.karpenter.irsa_arn}
    EOT
  ]
}

# Note: Karpenter NodePool and NodeClass will be deployed via Ansible after cluster creation
