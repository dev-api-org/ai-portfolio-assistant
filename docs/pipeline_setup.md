# CI/CD Pipeline Documentation

This document outlines the continuous integration and deployment setup for the AI Portfolio Assistant.

## Overview

The CI/CD pipeline is built with **GitHub Actions** and supports deployment to both **AWS** and **Azure** cloud platforms.

## Pipeline Structure

### 1. **Test Job** (`test`)
Runs on every push and pull request:

**Steps:**
- ✅ Checkout code
- ✅ Setup Python 3.11 with pip caching
- ✅ Install dependencies + pytest
- ✅ Run test suite (`pytest tests/`)
- ✅ Verify app imports successfully

**Required Secrets:**
- `GOOGLE_API_KEY` - For testing AI functionality

### 2. **AWS Deployment** (`deploy-aws`)
Runs only on main branch pushes after tests pass:

**Steps:**
- ✅ Configure AWS credentials
- 🔄 Deploy to chosen AWS service
- 🔄 Run deployment verification

**Required Secrets:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### 3. **Azure Deployment** (`deploy-azure`)
Runs only on main branch pushes after tests pass:

**Steps:**
- ✅ Login to Azure with service principal
- 🔄 Deploy to chosen Azure service  
- 🔄 Run deployment verification

**Required Secrets:**
- `AZURE_CREDENTIALS` - Service principal JSON

### 4. **Security Scan** (`security-scan`)
Runs on pull requests:

**Steps:**
- ✅ Run Super Linter for code quality
- ✅ Security vulnerability scanning

## Repository Secrets Setup

Navigate to **Settings → Secrets and Variables → Actions** in GitHub:

### Core Secrets:
```bash
GOOGLE_API_KEY=your_google_api_key_here
```

### AWS Secrets:
```bash
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=wJalrXUt...
```

### Azure Secrets:
```bash
AZURE_CREDENTIALS={
  "clientId": "...",
  "clientSecret": "...",
  "subscriptionId": "...",
  "tenantId": "..."
}
```

## Workflow Triggers

| Event | Branches | Jobs Triggered |
|-------|----------|----------------|
| Push | `main`, `develop` | test, deploy-aws, deploy-azure |
| Pull Request | `main` | test, security-scan |
| Manual | any | test (workflow_dispatch) |

## Environment Strategy

### **Branches:**
- `main` → Production deployments
- `develop` → Staging deployments  
- `feature/*` → Test only, no deployment

### **Environments:**
- **Production** - AWS + Azure production services
- **Staging** - Lower-cost dev instances
- **Testing** - CI test environment only

## Deployment Strategies

### **Blue/Green Deployment:**
1. Deploy new version to "green" environment
2. Run health checks and smoke tests
3. Switch traffic from "blue" to "green"
4. Keep "blue" as rollback option

### **Rolling Deployment:**
1. Deploy to subset of instances
2. Verify health and performance
3. Gradually roll out to remaining instances
4. Monitor throughout process

## Monitoring & Alerting

### **Health Checks:**
- Application startup verification
- API endpoint availability
- Database connectivity (if applicable)

### **Performance Monitoring:**
- Response time thresholds
- Error rate monitoring
- Resource utilization tracking

### **Alerting Channels:**
- Slack notifications for deployment status
- Email alerts for critical failures
- GitHub status checks for PR reviews

## Rollback Procedures

### **Automatic Rollback Triggers:**
- Health check failures after deployment
- Error rate above 5% threshold
- Response time degradation >2x baseline

### **Manual Rollback:**
1. Identify problematic deployment
2. Revert to previous stable version
3. Run verification tests
4. Notify team of rollback

## Adding New Tests

### **Test Categories:**
- **Unit Tests** - Individual function testing
- **Integration Tests** - Component interaction testing
- **E2E Tests** - Full application workflow testing
- **Performance Tests** - Load and stress testing

### **Test File Structure:**
```
tests/
├── unit/
│   ├── test_chat_core.py
│   ├── test_config.py
│   └── test_session_memory.py
├── integration/
│   ├── test_api_integration.py
│   └── test_ui_components.py
└── e2e/
    └── test_full_workflow.py
```

## Performance Benchmarks

### **Target Metrics:**
- Page load time: < 2 seconds
- API response time: < 500ms
- Test suite runtime: < 5 minutes
- Deployment time: < 10 minutes

### **Monitoring Tools:**
- GitHub Actions timing
- Application performance monitoring
- Infrastructure monitoring dashboards

---

**Maintenance Notes:**
- Review and update dependencies monthly
- Monitor pipeline performance and optimize
- Regular security scanning and updates
- Document any pipeline changes in this file

**Last Updated:** Initial version
**Maintained by:** DevOps Team
