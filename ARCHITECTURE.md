# GitOps CI/CD Architecture

## Overview
This project implements a complete GitOps CI/CD pipeline with 4 distinct workflows that work together to deliver a 3-tier notes application on AWS EKS.

## Workflow 1: Infrastructure Pipeline
**Trigger**: Changes to `terraform/` directory  
**Purpose**: Provision AWS infrastructure

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub Repo   │───▶│  GitHub Actions  │───▶│   Terraform     │
│   (terraform/)  │    │  Infrastructure  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AWS EKS Cluster                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Managed Node   │  │   EBS CSI       │  │      ECR        │ │
│  │     Groups      │  │    Driver       │  │   Repository    │ │
│  │   (t3.large)    │  │                 │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow 2: Application Pipeline
**Trigger**: Changes to `app/` directory  
**Purpose**: Build and publish application images

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub Repo   │───▶│  GitHub Actions  │───▶│  Docker Build   │
│     (app/)      │    │   Application    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                │                        ▼
                                │               ┌─────────────────┐
                                │               │    AWS ECR      │
                                │               │  Push Image     │
                                │               │  (SHA tag)      │
                                │               └─────────────────┘
                                │                        │
                                ▼                        │
                       ┌─────────────────┐              │
                       │ Update Helm     │◀─────────────┘
                       │ values.yaml     │
                       │ (new image tag) │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Git Commit &    │
                       │ Push Changes    │
                       └─────────────────┘
```

## Workflow 3: Deployment Pipeline
**Trigger**: Changes to `helm/values.yaml`  
**Purpose**: Setup GitOps controller

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub Repo   │───▶│  GitHub Actions  │───▶│     Ansible     │
│ (helm/values)   │    │     Deploy       │    │   Playbook      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │ Install ArgoCD  │
                                                │   on EKS        │
                                                └─────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │ Create ArgoCD   │
                                                │  Application    │
                                                └─────────────────┘
```

## Workflow 4: GitOps Pipeline
**Trigger**: Continuous monitoring by ArgoCD  
**Purpose**: Deploy and manage applications

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│     ArgoCD      │───▶│  Monitor Repo    │───▶│  Detect Changes │
│   Controller    │    │   (helm/ dir)    │    │  in Manifests   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                                               │
         │                                               ▼
         │                                      ┌─────────────────┐
         │                                      │   Helm Sync     │
         │                                      │ Apply Changes   │
         │                                      └─────────────────┘
         │                                               │
         │                                               ▼
         └──────────────────────────────────────┌─────────────────┐
                                                │ Kubernetes      │
                                                │ Deployment      │
                                                └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Application Pods                             │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │     Nginx       │  │   Flask API     │  │     MySQL       │ │
│  │ Reverse Proxy   │──│   Notes App     │──│   Database      │ │
│  │   (Port 80)     │  │   (Port 5000)   │  │ + Persistent    │ │
│  │                 │  │                 │  │    Volume       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                │                               │
│                                ▼                               │
│                       ┌─────────────────┐                     │
│                       │   Prometheus    │                     │
│                       │    Metrics      │                     │
│                       │   (/metrics)    │                     │
│                       └─────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

## Complete Data Flow

```
Developer Push → GitHub → Actions → ECR/Terraform → EKS
                    ↓
                ArgoCD ← Helm Charts ← Updated Values
                    ↓
            Kubernetes Deployment
                    ↓
        [Nginx] → [Flask] → [MySQL]
                    ↓
            Prometheus Metrics
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/notes` | List all notes (with pagination) |
| POST | `/notes` | Create new note |
| PUT | `/notes/<id>` | Update existing note |
| DELETE | `/notes/<id>` | Delete note |
| GET | `/health` | Health check status |
| GET | `/metrics` | Prometheus metrics |

## Technology Stack

- **Container Orchestration**: Kubernetes (AWS EKS)
- **Infrastructure as Code**: Terraform
- **Configuration Management**: Ansible
- **GitOps**: ArgoCD
- **Package Management**: Helm
- **CI/CD**: GitHub Actions
- **Container Registry**: AWS ECR
- **Storage**: AWS EBS with CSI driver
- **Monitoring**: Prometheus
- **Application**: Flask (Python)
- **Database**: MySQL
- **Proxy**: Nginx
