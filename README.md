# Notes App - Complete CI/CD with GitOps

![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-623CE4?style=for-the-badge&logo=terraform&logoColor=white)
![Ansible](https://img.shields.io/badge/Ansible-EE0000?style=for-the-badge&logo=ansible&logoColor=white)
![ArgoCD](https://img.shields.io/badge/ArgoCD-EF7B4D?style=for-the-badge&logo=argo&logoColor=white)
![Helm](https://img.shields.io/badge/Helm-0F1689?style=for-the-badge&logo=helm&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)

A 3-tier notes application with full CI/CD pipeline using GitHub Actions, Terraform, Ansible, Helm, and ArgoCD for GitOps deployment on AWS EKS.

## Architecture

- **Frontend/Proxy**: Nginx (reverse proxy)
- **Backend**: Flask web application (custom image in ECR)
- **Database**: MySQL with persistent storage
- **Infrastructure**: AWS EKS cluster with Karpenter autoscaling
- **CI/CD**: GitHub Actions + Ansible + ArgoCD GitOps

## Repository Structure

```
notes-app/
├── app/                    # Flask application source code
│   ├── app/               # Flask app modules
│   ├── migrations/        # Database migrations
│   ├── Dockerfile         # Container build instructions
│   └── requirements.txt   # Python dependencies
├── terraform/             # Infrastructure as Code
│   ├── main.tf           # EKS cluster configuration
│   ├── karpenter.tf      # Auto-scaling setup
│   └── variables.tf      # Configuration variables
├── helm/                  # Kubernetes manifests
│   ├── templates/        # K8s resource templates
│   ├── nginx/           # Nginx configuration
│   └── values.yaml      # Application configuration
├── argocd/               # GitOps configuration
│   └── notes-app.yaml   # ArgoCD application manifest
├── ansible/              # Deployment automation
│   ├── deploy.yml       # Ansible playbook
│   └── requirements.yml # Ansible dependencies
└── .github/workflows/    # CI/CD pipelines
    ├── infrastructure.yml # Terraform deployment
    ├── application.yml   # Docker build & push
    └── deploy.yml       # Ansible deployment
```

## CI/CD Workflow

### 1. Infrastructure Pipeline
**Trigger**: Changes to `terraform/` directory
```
Code Push → GitHub Actions → Terraform Apply → EKS Cluster + ECR Ready
```

### 2. Application Pipeline  
**Trigger**: Changes to `app/` directory
```
Code Push → GitHub Actions → 
  ├── Build Flask Docker Image
  ├── Push to ECR with Git SHA tag
  ├── Update helm/values.yaml
  └── Commit changes back to repo
```

### 3. Deployment Pipeline
**Trigger**: Changes to `helm/values.yaml`
```
Updated Values → GitHub Actions → Ansible Playbook → Helm Deploy
```

### 4. GitOps Pipeline
**Trigger**: ArgoCD monitors repository
```
Helm Changes → ArgoCD Auto-Sync → Kubernetes Deployment
```

## Prerequisites

- AWS CLI configured with appropriate permissions
- GitHub repository with the following secrets:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`

## Quick Start

### 1. Deploy Infrastructure
```bash
# Manually trigger infrastructure pipeline
gh workflow run infrastructure.yml
```

### 2. Deploy Application
```bash
# Push code changes to trigger automatic deployment
git add .
git commit -m "Deploy notes app"
git push origin main
```

### 3. Run Database Migrations
```bash
# Update kubeconfig
aws eks update-kubeconfig --region us-east-1 --name notes

# Run migrations inside web pod
kubectl exec deployment/notes-web -n notes -- flask db upgrade
```

### 4. Access Application
```bash
# Port forward to access locally
kubectl port-forward svc/notes-nginx -n notes 3000:80
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get ArgoCD admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

**Access URLs:**
- **Notes App**: http://localhost:3000
- **ArgoCD UI**: https://localhost:8080 (admin/password-from-above)

## API Endpoints

- `GET /notes` - List all notes (with pagination/search)
- `POST /notes` - Create new note
- `PUT /notes/<id>` - Update existing note
- `DELETE /notes/<id>` - Delete note
- `GET /health` - Health check endpoint
- `GET /metrics` - Prometheus metrics

## Configuration

All application configuration is managed through `helm/values.yaml`:

- **Images**: Container images and tags (auto-updated by CI/CD)
- **Replicas**: Number of web app replicas
- **Resources**: CPU/memory limits and requests  
- **Environment**: Database connection settings
- **Storage**: MySQL persistent volume size

## Monitoring

The application includes:
- Prometheus metrics endpoints on Flask app (`/metrics`)
- Health checks for all services (`/health`)
- Container resource monitoring
- Kubernetes cluster metrics

## Production Deployment

For production deployment, change the service type to LoadBalancer:

```yaml
# In helm/templates/nginx-service.yaml
spec:
  type: LoadBalancer  # Change from NodePort
  ports:
    - port: 80
      targetPort: 80
```

## Common Challenges & Solutions

### 1. **EBS CSI Driver Missing**
**Problem**: MySQL pods stuck in Pending state with volume binding errors
**Solution**: Install EBS CSI driver addon
```bash
aws eks create-addon --cluster-name notes --addon-name aws-ebs-csi-driver
# Add AmazonEBSCSIDriverPolicy to node group IAM role
```

### 2. **Pod Capacity Issues**
**Problem**: Pods can't be scheduled due to node capacity
**Solution**: Use larger instance types or add more nodes
```bash
# In terraform/main.tf
instance_types = ["t3.large"]  # Instead of t3.medium
```

### 3. **Database Table Missing**
**Problem**: App returns 500 errors when storing notes
**Solution**: Run database migrations
```bash
kubectl exec deployment/notes-web -n notes -- flask db upgrade
```

### 4. **ArgoCD Pods Failing**
**Problem**: ArgoCD pods stuck in Pending due to node taints
**Solution**: Remove taints from nodes
```bash
kubectl taint nodes --all system=true:NoSchedule-
```

### 5. **Terraform Resource Conflicts**
**Problem**: Infrastructure pipeline fails with "already exists" errors
**Solution**: Import existing resources or use different names
```bash
# Change cluster name in terraform/variables.tf
variable "cluster_name" {
  default = "your-unique-name"
}
```

## Customization for Your Environment

### Required Changes:
1. **Repository URL**: Update in `argocd/notes-app.yaml` and `ansible/deploy.yml`
2. **AWS Region**: Change in all workflow files and terraform variables
3. **Cluster Name**: Update in `terraform/variables.tf`
4. **ECR Repository**: Will be created automatically with your AWS account ID

### Optional Changes:
1. **Instance Types**: Modify in `terraform/main.tf`
2. **Resource Limits**: Adjust in `helm/values.yaml`
3. **Database Settings**: Update MySQL configuration in `helm/values.yaml`
4. **Scaling**: Modify replica counts and autoscaling settings

## Development Workflow

1. **Make code changes** in `app/` directory
2. **Push to main branch** - triggers automatic:
   - Docker image build and push to ECR
   - Helm values update with new image tag
   - ArgoCD sync to Kubernetes cluster

3. **Infrastructure changes** in `terraform/` trigger infrastructure updates
4. **Kubernetes changes** in `helm/` trigger ArgoCD sync

## Troubleshooting

```bash
# Check pipeline status
gh workflow list

# View logs
gh run view --log

# Check ArgoCD sync status
kubectl get applications -n argocd

# Check pod status
kubectl get pods -n notes

# View application logs
kubectl logs -f deployment/notes-web -n notes

# Check MySQL logs
kubectl logs -f statefulset/notes-mysql -n notes

# Test API endpoints
curl http://localhost:3000/health
curl http://localhost:3000/metrics
curl http://localhost:3000/notes
```
