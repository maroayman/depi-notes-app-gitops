# Notes App CI/CD Architecture Diagram

```mermaid
graph TB
    Dev[Developer] --> |Push Code| GH[GitHub Repository]
    
    subgraph "CI/CD Pipelines"
        GH --> |terraform/ changes| IP[Infrastructure Pipeline]
        GH --> |app/ changes| AP[Application Pipeline] 
        GH --> |helm/ changes| DP[Deployment Pipeline]
        
        IP --> |terraform apply| AWS[AWS EKS + ECR]
        
        AP --> Build[Build Docker Image]
        Build --> Push[Push to ECR]
        Push --> Update[Update helm/values.yaml]
        Update --> Commit[Commit back to repo]
        
        Commit --> DP
        DP --> Ansible[Ansible Playbook]
        Ansible --> Helm[Helm Deploy]
    end
    
    subgraph "GitOps"
        ArgoCD[ArgoCD] --> |monitors| GH
        ArgoCD --> |auto-sync| K8s[Kubernetes Cluster]
    end
    
    subgraph "AWS Infrastructure"
        AWS --> EKS[EKS Cluster]
        AWS --> ECR[ECR Registry]
        EKS --> Karpenter[Karpenter Autoscaling]
    end
    
    subgraph "Application Stack"
        K8s --> Nginx[Nginx Proxy]
        K8s --> Flask[Flask Backend]
        K8s --> MySQL[MySQL Database]
    end
    
    Helm --> K8s
    ECR --> K8s
    
    User[End User] --> |http://localhost:3000| Nginx
    
    classDef pipeline fill:#e1f5fe
    classDef aws fill:#fff3e0
    classDef app fill:#f3e5f5
    classDef gitops fill:#e8f5e8
    
    class IP,AP,DP pipeline
    class AWS,EKS,ECR,Karpenter aws
    class Nginx,Flask,MySQL app
    class ArgoCD gitops
```

## Workflow Triggers

1. **Infrastructure Pipeline**: `terraform/` changes → EKS cluster setup
2. **Application Pipeline**: `app/` changes → Docker build → ECR push → values update
3. **Deployment Pipeline**: `helm/values.yaml` changes → Ansible → Helm deploy
4. **GitOps Pipeline**: ArgoCD continuous monitoring → auto-sync to K8s

## Key Components

- **GitHub Actions**: Orchestrates all CI/CD pipelines
- **Terraform**: Infrastructure as Code for AWS resources
- **Ansible**: Deployment automation and orchestration
- **Helm**: Kubernetes package management
- **ArgoCD**: GitOps continuous deployment
- **Karpenter**: Node autoscaling for EKS cluster
