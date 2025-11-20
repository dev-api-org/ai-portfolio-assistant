# Azure Deployment Setup

This guide covers deploying the AI Portfolio Assistant to Microsoft Azure.

## Prerequisites

- Azure Account with active subscription
- Azure CLI installed and configured
- Docker Desktop (for container deployments)

## Deployment Options

### Option 1: Azure Container Instances (Recommended)
Serverless containers without managing infrastructure.

**Setup Steps:**
1. Create container registry: `az acr create`
2. Build and push Docker image
3. Create container instance with environment variables
4. Configure networking and DNS

### Option 2: Azure Web Apps
Platform-as-a-service with built-in scaling.

**Setup Steps:**
1. Create App Service Plan
2. Create Web App with Python runtime
3. Configure deployment from GitHub
4. Set application settings for environment variables

### Option 3: Azure Kubernetes Service (AKS)
Full Kubernetes orchestration for complex deployments.

**Setup Steps:**
1. Create AKS cluster
2. Create Kubernetes manifests
3. Set up ingress controller
4. Configure horizontal pod autoscaling

## Required Azure Resources

### Core Resources:
- **Resource Group** - Logical container for resources
- **Container Registry** - Store Docker images
- **Key Vault** - Secure storage for API keys
- **Application Insights** - Monitoring and analytics

### Networking:
- **Virtual Network** - Isolated network environment
- **Application Gateway** - Load balancer with SSL termination
- **DNS Zone** - Custom domain management

## Configuration Files

Place Azure-specific configs in `/configs/azure_config/`:
- `azure-pipelines.yml` - Azure DevOps pipeline
- `Dockerfile` - Container definition
- `kubernetes-manifest.yaml` - K8s deployment config
- `arm-template.json` - Infrastructure as Code

## Environment Variables Setup

**In Azure Key Vault:**
```bash
az keyvault secret set --vault-name "your-keyvault" --name "GOOGLE-API-KEY" --value "your-api-key"
az keyvault secret set --vault-name "your-keyvault" --name "MODEL-NAME" --value "gemini-2.0-flash"
```

**In Web App Configuration:**
- Navigate to Configuration → Application settings
- Add environment variables with Key Vault references

## Security Best Practices

- Use Managed Identity for service authentication
- Store secrets in Azure Key Vault
- Enable Azure AD authentication for the app
- Configure network security groups
- Enable Azure Security Center recommendations

## Monitoring & Diagnostics

- **Application Insights** - Application performance monitoring
- **Log Analytics** - Centralized logging
- **Azure Monitor** - Infrastructure monitoring
- **Availability Tests** - Uptime monitoring

## Cost Management

- Use Azure Cost Management + Billing
- Set up budget alerts
- Consider Azure Reserved Instances for long-term deployments
- Use Azure Advisor for cost optimization recommendations

## CI/CD Integration

The GitHub Actions workflow already includes Azure deployment steps:
1. Authenticate with Azure using service principal
2. Build and push container to ACR
3. Deploy to chosen Azure service
4. Run smoke tests against deployed app

---

**Next Steps:**
1. Create Azure resources using CLI or Portal
2. Set up service principal for GitHub Actions
3. Configure Key Vault and secrets
4. Update deployment workflow with specific Azure commands

**Assigned to:** Person 2 (Azure Specialist)
