# Notes Application - Air-Gapped Kubernetes GitOps

This repository contains the complete FluxCD GitOps configuration for deploying the Notes application in an **air-gapped Kubernetes environment**.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Clone This Repository](#clone-this-repository)
4. [Deploy Gitea (Git Server)](#deploy-gitea-git-server)
5. [Configure Gitea](#configure-gitea)
6. [Push Repository to Gitea](#push-repository-to-gitea)
7. [Install FluxCD CLI](#install-fluxcd-cli)
8. [Bootstrap FluxCD](#bootstrap-fluxcd)
9. [Verify Deployment](#verify-deployment)
10. [Making Changes](#making-changes)
11. [Troubleshooting](#troubleshooting)

---

## 1. Prerequisites

Before starting, ensure you have:

- [ ] **Kubernetes cluster** (v1.20+)
- [ ] **kubectl** configured with cluster access
- [ ] **Persistent storage** (NFS or similar) for PVCs
- [ ] **Private container registry** (e.g., `10.10.30.70:30500`)
- [ ] **Internet access** (to clone this repo initially)

### Required Tools

```bash
# Install kubectl (if not already installed)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/

# Install FluxCD CLI
curl -s https://toolkit.fluxcd.io/install.sh | bash
```

---

## 2. Architecture Overview

This setup uses a **fully air-gapped GitOps approach**:

```
┌─────────────────────────────────────────────────────────────────┐
│                     AIR-GAPPED NETWORK                           │
│                                                                 │
│  ┌─────────────┐      ┌──────────────┐      ┌───────────────┐ │
│  │    Gitea    │ ───▶ │   FluxCD     │ ───▶ │  Kubernetes   │ │
│  │  (Git UI)   │      │  Controller  │      │   Cluster    │ │
│  │ Port 30080  │      │              │      │               │ │
│  └─────────────┘      └──────────────┘      └───────────────┘ │
│         │                    │                      │           │
│         │    Pulls from     │   Applies             │           │
│         │    Git repo      │   manifests           │           │
│         └──────────────────┴──────────────────────┘           │
│                                                                 │
│  Gitea URL: http://10.10.30.72:30080                          │
└─────────────────────────────────────────────────────────────────┘
```

### Application Components

| Component | Type | Description |
|-----------|------|-------------|
| **notes-nginx** | Deployment | Reverse proxy/load balancer (NodePort: 30515) |
| **notes-web** | Deployment | Flask web application (port 5000) |
| **notes-mysql** | StatefulSet | MySQL database (port 3306) |

---

## 3. Clone This Repository

First, clone this repository to your local machine:

```bash
# Clone the repository
git clone https://github.com/maroayman/depi-notes-app-gitops.git
cd depi-notes-app-gitops

# Switch to the air-gapped branch
git checkout airgapped-k8s
```

---

## 4. Deploy Gitea (Git Server)

Gitea serves as the Git repository server inside your air-gapped network.

### Step 4.1: Create Namespace

```bash
kubectl create namespace gitea
```

### Step 4.2: Apply Gitea manifests

```bash
# Apply PVC, Service, and Deployment
kubectl apply -f gitea/gitea-pvc.yaml
kubectl apply -f gitea/gitea-service.yaml
kubectl apply -f gitea/gitea-deploy.yaml
```

### Step 4.3: Verify Gitea is Running

```bash
kubectl get pods -n gitea
# Expected output:
# NAME                    READY   STATUS    RESTARTS   AGE
# gitea-xxxxx-xxxxx       1/1     Running   0          2m
```

---

## 5. Configure Gitea

### Step 5.1: Access Gitea UI

Open your browser and navigate to:

```
http://10.10.30.72:30080
```

### Step 5.2: Initial Setup

1. **First Run Setup**
   - Follow the on-screen instructions
   - Set admin username and password
   - Configure SMTP (optional, can skip)
   - Click "Install Gitea"

2. **Create Repository**
   - Click the **+** icon (Create New Repository)
   - Repository name: `depi-notes-app-gitops`
   - Visibility: Private (or Public based on preference)
   - Click "Create Repository"

3. **Create Access Token** (for FluxCD)
   - Go to Settings → Applications → Generate New Token
   - Name: `fluxcd-token`
   - Copy the generated token (you'll need it for FluxCD bootstrap)

---

## 6. Push Repository to Gitea

### Step 6.1: Add Gitea Remote

```bash
# Add Gitea as a remote
git remote add gitea http://10.10.30.72:30080/maroayman/depi-notes-app-gitops.git

# Or if you already have a remote named origin, rename it:
# git remote rename origin github
# git remote add gitea http://10.10.30.72:30080/maroayman/depi-notes-app-gitops.git
```

### Step 6.2: Push to Gitea

```bash
# Push the airgapped-k8s branch to Gitea
git push gitea airgapped-k8s
# Enter your Gitea username and password/token when prompted
```

### Alternative: Using GitHub as Source

If you already have the repo on GitHub and want to sync it:

```bash
# Add Gitea remote
git remote add gitea http://10.10.30.72:30080/maroayman/depi-notes-app-gitops.git

# Push to Gitea
git push gitea airgapped-k8s
```

---

## 7. Install FluxCD CLI

If you haven't already installed FluxCD:

```bash
# Linux/macOS
curl -s https://toolkit.fluxcd.io/install.sh | bash

# Verify installation
flux --version
```

---

## 8. Bootstrap FluxCD

Now we'll configure FluxCD to watch your Gitea repository and automatically deploy changes.

### Step 8.1: Bootstrap FluxCD

```bash
flux bootstrap git \
  --url=http://10.10.30.72:30080/maroayman/depi-notes-app-gitops \
  --branch=airgapped-k8s \
  --path=flux-cd \
  --username=maroayman \
  --password=<your-gitea-token> \
  --allow-insecure-http=true
```

Replace `<your-gitea-token>` with the token you generated in Step 5.3.

### Step 8.2: Verify FluxCD Components

```bash
# Check FluxCD pods
kubectl get pods -n flux-system

# Expected output:
# NAME                           READY   STATUS
# helm-controller-xxxxx         1/1     Running
# kustomize-controller-xxxxx   1/1     Running
# notification-controller-xxxxx 1/1     Running
# source-controller-xxxxx      1/1     Running
```

### Step 8.3: Verify GitRepository and Kustomization

```bash
flux get all
# Expected output:
# NAME                      REVISION           READY   MESSAGE
# gitrepository/flux-system airgapped-k8s@xxx  True    stored artifact
# kustomization/flux-system airgapped-k8s@xxx   True    Applied revision
```

---

## 9. Verify Deployment

### Step 9.1: Check Namespace

```bash
kubectl get ns notes
# Expected: notes namespace should exist
```

### Step 9.2: Check Application Pods

```bash
kubectl get pods -n notes
# Expected output:
# NAME                           READY   STATUS    RESTARTS   AGE
# notes-mysql-0                  1/1     Running   0          2m
# notes-nginx-xxxxx-xxxxx       1/1     Running   0          2m
# notes-web-xxxxx-xxxxx         1/1     Running   0          2m
```

### Step 9.3: Check Services

```bash
kubectl get svc -n notes
# Expected output:
# NAME           TYPE        CLUSTER-IP       PORT(S)        AGE
# notes-mysql   ClusterIP   None             3306/TCP       5m
# notes-nginx   NodePort    10.xx.xx.xx      80:30515/TCP   5m
# notes-web     ClusterIP   10.xx.xx.xx      5000/TCP       5m
```

### Step 9.4: Access the Application

The Notes application is now accessible at:

```
http://<any-node-ip>:30515
```

---

## 10. Making Changes

One of the main benefits of GitOps is easy updates. Here's how to make changes:

### Step 10.1: Edit Files

Make changes to any file in the repository:

```bash
# Example: Update nginx image version
vim apps/notes/deployment-nginx.yaml
```

### Step 10.2: Commit and Push

```bash
# Add changes
git add .
git commit -m "Update nginx to version 1.25-alpine"

# Push to Gitea
git push gitea airgapped-k8s
```

### Step 10.3: FluxCD Automatically Syncs

FluxCD will:
1. Detect the changes in Gitea (within ~1 minute)
2. Apply the changes to your Kubernetes cluster
3. Update the status

### Verify Changes

```bash
# Watch the deployment
kubectl rollout status deployment/notes-nginx -n notes

# Or check pods
kubectl get pods -n notes -w
```

---

## 11. Troubleshooting

### Common Issues and Solutions

#### Issue: ImagePullBackOff

**Problem:** Pods stuck in `ImagePullBackOff` status

**Solution:** Check the image URL and tags in the deployment files:

```bash
# Check current image
kubectl get deployment notes-nginx -n notes -o jsonpath='{.spec.template.spec.containers[0].image}'

# Verify image exists in your registry
# Update the image tag in apps/notes/deployment-nginx.yaml and push
```

#### Issue: FluxCD Not Syncing

**Problem:** Changes not appearing in cluster

**Solution:**

```bash
# Reconcile manually
flux reconcile kustomization --all
flux reconcile source git --all

# Check logs
flux logs --level=debug
```

#### Issue: Gitea Not Accessible

**Problem:** Can't reach Gitea at port 30080

**Solution:**

```bash
# Check Gitea service
kubectl get svc -n gitea

# Check Gitea pod logs
kubectl logs -n gitea -l app=gitea
```

#### Issue: Flux Bootstrap Fails

**Problem:** Flux bootstrap command fails

**Solution:**

```bash
# Verify Gitea is accessible from cluster
kubectl exec -it <any-pod> -- curl -I http://10.10.30.72:30080

# Check FluxCD logs
kubectl logs -n flux-system deployment/source-controller
```

### Useful Commands

```bash
# Check Flux status
flux get all

# View Flux logs
flux logs

# Suspend reconciliation (for maintenance)
flux suspend kustomization flux-system

# Resume reconciliation
flux resume kustomization flux-system

# Force reconcile
flux reconcile kustomization flux-system --with-source
```

---

## Directory Structure

```
.
├── README.md                   # This file
├── flux-cd/                    # FluxCD configuration
│   ├── fluxcd-git.yaml        # GitRepository CR
│   ├── fluxcd-kustomization.yaml
│   └── kustomization.yaml
├── apps/notes/                # Application manifests
│   ├── deployment-nginx.yaml
│   ├── deployment-web.yaml
│   ├── statefulset-mysql.yaml
│   ├── service-nginx.yaml
│   ├── service-web.yaml
│   ├── service-mysql.yaml
│   ├── configmap-nginx.yaml
│   ├── secret-mysql.yaml
│   └── kustomization.yaml
├── helm/                      # Helm charts (alternative)
└── gitea/                    # Gitea deployment manifests
    ├── gitea-deploy.yaml
    ├── gitea-pvc.yaml
    └── gitea-service.yaml
```

---

## License

MIT License - See LICENSE file for details

---

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review FluxCD docs: https://fluxcd.io/docs/
3. Check Kubernetes logs: `kubectl logs <pod-name> -n <namespace>`
