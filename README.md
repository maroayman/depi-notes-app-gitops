# Notes Application - Air-Gapped Kubernetes GitOps

This repository contains the FluxCD GitOps configuration for the Notes application in an air-gapped Kubernetes environment.

## Architecture

The Notes application consists of three main components:

- **notes-nginx**: Reverse proxy/load balancer (NodePort)
- **notes-web**: Flask web application
- **notes-mysql**: MySQL database (StatefulSet)

## Directory Structure

```
.
├── flux-cd/              # FluxCD configuration
│   ├── fluxcd-git.yaml   # GitRepository CR
│   ├── fluxcd-kustomization.yaml
│   └── kustomization.yaml
├── apps/notes/           # Application manifests
│   ├── deployment-nginx.yaml
│   ├── deployment-web.yaml
│   ├── statefulset-mysql.yaml
│   ├── service-nginx.yaml
│   ├── service-web.yaml
│   ├── service-mysql.yaml
│   ├── configmap-nginx.yaml
│   ├── secret-mysql.yaml
│   └── kustomization.yaml
├── helm/                 # Helm charts (alternative)
└── gitea/               # Gitea setup (for air-gapped git)
```

## Quick Start

### 1. Bootstrap FluxCD

```bash
flux bootstrap git \
  --url=http://10.10.30.72:30080/maroayman/depi-notes-app-gitops \
  --branch=main \
  --path=clusters/notes
```

### 2. Verify Installation

```bash
flux get all
kubectl get pods -n notes
```

## Making Changes

1. Edit files in `apps/notes/`
2. Commit and push to git
3. FluxCD will automatically apply changes

## Troubleshooting

```bash
# Check Flux status
flux get all

# Reconcile manually
flux reconcile kustomization --all
flux reconcile source git --all

# View logs
flux logs
```

## License

MIT
