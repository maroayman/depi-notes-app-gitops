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

### 2. Install ArgoCD (One-time setup)
```bash
# Update kubeconfig
aws eks update-kubeconfig --region us-east-1 --name notes-app

# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Deploy ArgoCD application
kubectl apply -f argocd/notes-app.yaml
```

### 3. Deploy Application
```bash
# Push code changes to trigger automatic deployment
git add .
git commit -m "Deploy notes app"
git push origin main
```

### 4. Access Application
```bash
# Port forward to access locally
kubectl port-forward svc/notes-nginx -n notes 3000:80

# Access at: http://localhost:3000
```

## Configuration

All application configuration is managed through `helm/values.yaml`:

- **Images**: Container images and tags (auto-updated by CI/CD)
- **Replicas**: Number of web app replicas
- **Resources**: CPU/memory limits and requests  
- **Environment**: Database connection settings
- **Storage**: MySQL persistent volume size

## Monitoring

The application includes:
- Prometheus metrics endpoints on Flask app
- Health checks for all services
- Container resource monitoring
- Kubernetes cluster metrics via Karpenter

## Development Workflow

1. **Make code changes** in `app/` directory
2. **Push to main branch** - triggers automatic:
   - Docker image build and push to ECR
   - Helm values update with new image tag
   - Ansible deployment via GitHub Actions
   - ArgoCD sync to Kubernetes cluster

3. **Infrastructure changes** in `terraform/` trigger infrastructure updates
4. **Kubernetes changes** in `helm/` trigger deployment updates

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
```
