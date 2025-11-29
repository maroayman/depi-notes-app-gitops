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

# Karpenter NodePool
resource "kubernetes_manifest" "karpenter_nodepool" {
  depends_on = [helm_release.karpenter]
  
  manifest = {
    apiVersion = "karpenter.sh/v1beta1"
    kind       = "NodePool"
    metadata = {
      name = "notes-app-nodepool"
    }
    spec = {
      template = {
        metadata = {
          labels = {
            app = "notes-app"
          }
        }
        spec = {
          requirements = [
            {
              key      = "kubernetes.io/arch"
              operator = "In"
              values   = ["amd64"]
            },
            {
              key      = "karpenter.sh/capacity-type"
              operator = "In"
              values   = ["spot", "on-demand"]
            },
            {
              key      = "node.kubernetes.io/instance-type"
              operator = "In"
              values   = ["t3.medium", "t3.large", "m5.large"]
            }
          ]
          nodeClassRef = {
            apiVersion = "karpenter.k8s.aws/v1beta1"
            kind       = "EC2NodeClass"
            name       = "notes-app-nodeclass"
          }
        }
      }
      limits = {
        cpu    = 1000
        memory = "1000Gi"
      }
      disruption = {
        consolidationPolicy = "WhenUnderutilized"
        consolidateAfter    = "30s"
      }
    }
  }
}

# Karpenter EC2NodeClass
resource "kubernetes_manifest" "karpenter_nodeclass" {
  depends_on = [helm_release.karpenter]
  
  manifest = {
    apiVersion = "karpenter.k8s.aws/v1beta1"
    kind       = "EC2NodeClass"
    metadata = {
      name = "notes-app-nodeclass"
    }
    spec = {
      amiFamily = "AL2"
      subnetSelectorTerms = [
        {
          tags = {
            "karpenter.sh/discovery" = module.eks.cluster_name
          }
        }
      ]
      securityGroupSelectorTerms = [
        {
          tags = {
            "karpenter.sh/discovery" = module.eks.cluster_name
          }
        }
      ]
      userData = base64encode(<<-EOT
        #!/bin/bash
        /etc/eks/bootstrap.sh ${module.eks.cluster_name}
      EOT
      )
    }
  }
}
