# AWS Deployment Setup

This guide covers deploying the AI Portfolio Assistant to AWS.

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured locally
- Docker installed (for containerized deployments)

## Deployment Options

### Option 1: AWS App Runner (Recommended)
Simple, fully managed container service.

**Setup Steps:**
1. Create `apprunner.yaml` in project root
2. Configure GitHub connection in AWS Console
3. Set environment variables in App Runner service
4. Deploy automatically on push to main

**Required Environment Variables:**
- `GOOGLE_API_KEY`
- `MODEL_NAME` (optional, defaults to gemini-2.0-flash)
- `MODEL_TEMPERATURE` (optional, defaults to 0.7)

### Option 2: AWS Elastic Beanstalk
Platform-as-a-service for web applications.

**Setup Steps:**
1. Create `requirements.txt` (already done)
2. Add `Procfile` for process configuration
3. Use EB CLI to deploy: `eb init` → `eb create` → `eb deploy`

### Option 3: AWS ECS with Fargate
Containerized deployment with full control.

**Setup Steps:**
1. Create Dockerfile
2. Build and push to Amazon ECR
3. Create ECS task definition
4. Configure Application Load Balancer
5. Set up auto-scaling policies

## Configuration Files Needed

Place AWS-specific configs in `/configs/aws_config/`:
- `apprunner.yaml` - App Runner configuration
- `Dockerfile` - Container definition
- `task-definition.json` - ECS task definition
- `.platform/` - Elastic Beanstalk platform config

## Security Considerations

- Store API keys in AWS Secrets Manager
- Use IAM roles for service permissions
- Enable CloudWatch logging
- Configure security groups properly

## Cost Optimization

- Use AWS App Runner for low-traffic applications
- Consider AWS Lambda + API Gateway for serverless
- Monitor usage with AWS Cost Explorer

## Monitoring & Logs

- CloudWatch Logs for application logs
- X-Ray for distributed tracing
- CloudWatch Metrics for performance monitoring

---

**Next Steps:**
1. Choose deployment method above
2. Create necessary configuration files
3. Set up AWS secrets and permissions
4. Update GitHub Actions workflow with specific deployment steps

**Assigned to:** Person 1 (AWS Specialist)
