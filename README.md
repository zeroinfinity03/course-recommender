# Course Recommendation System - MLOps Pipeline

A production-ready course recommendation system deployed on AWS SageMaker with a complete MLOps pipeline.

## Overview

This project implements a content-based recommendation engine that suggests courses to users based on their enrollment history. The system uses TF-IDF vectorization and cosine similarity to find similar courses.

## Architecture

```
                                    ┌─────────────────────────────┐
                                    │     SageMaker Endpoint      │
                                    │  ┌───────────────────────┐  │
React Frontend ──► API Gateway ──► Lambda ──►Docker Container    │
                                    │  │      (app.py)         │  │
                                    │  └───────────────────────┘  │
                                    └─────────────────────────────┘
                                               ▲           ▲
                                               │           │
                                        ECR (image)   S3 (model.tar.gz)
```

### How It Works

1. **SageMaker (The Infrastructure)**  
   SageMaker provisions managed hardware (EC2 instances). Inside this machine, it pulls your Docker Image from ECR and starts the container.

2. **Your Server Code (The Logic: app.py)**  
   Inside the running Docker container, `app.py` starts a Web Server (Uvicorn). This process loads the serialized model from S3 and listens for requests to generate predictions.

3. **The Compliance (The Rule)**  
   Because SageMaker controls the traffic to the container, your Web Server must expose a specific endpoint: `POST /invocations`. This is where your prediction logic lives.

4. **The Bridge (Lambda)**  
   Since the SageMaker endpoint is private (inside AWS VPC), we use Lambda. Lambda acts as a secure client that authenticates and sends the request to the SageMaker `/invocations` route.

5. **The Public Entry (API Gateway)**  
   To let the React Frontend reach Lambda, we use API Gateway. It provides a public URL (`https://...`).

## Project Structure

```
12. mlops/
├── src/
│   ├── train.py           # Training script (creates model.tar.gz)
│   └── app.py             # Inference server (runs in SageMaker)
├── data/
│   ├── courses.csv        # Course catalog
│   └── enrollments.csv    # User enrollment history
├── deploy.py              # Deploy SageMaker endpoint
├── delete_endpoint.py     # Delete endpoint (stop charges)
├── main.py                # FastAPI proxy for testing
├── lambda.py              # Lambda function code
├── Dockerfile             # Container definition
├── entrypoint.sh          # Container startup script
└── pyproject.toml         # Dependencies
```

## Setup & Deployment

### Prerequisites

- Python 3.11+
- Docker
- AWS CLI configured
- uv package manager

### Step 1: Install Dependencies

```bash
uv add boto3 fastapi joblib pandas scikit-learn uvicorn
```

### Step 2: Train the Model

```bash
uv run python src/train.py
```

This creates:
- `reco_artifacts.joblib` - Trained model
- `model.tar.gz` - Packaged for SageMaker

### Step 3: Upload Model to S3

```bash
aws s3 cp model.tar.gz s3://your-bucket-name/model.tar.gz
```

### Step 4: Create ECR Repository & Push Docker Image

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build image (with correct format for SageMaker)
docker build --platform linux/amd64 --provenance=false -t course-image-api .

# Tag for ECR
docker tag course-image-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/course-image-api:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/course-image-api:latest
```

### Step 5: Create IAM Role

Create a SageMaker execution role with:
- `AmazonSageMakerFullAccess`
- `AmazonS3FullAccess`

### Step 6: Deploy to SageMaker

Update `deploy.py` with your:
- ECR Image URI
- S3 Model URI
- IAM Role ARN

```bash
uv run python deploy.py
```

## API Usage

### Get Recommendations for a User

```json
POST /invocations
{
  "user_id": 1,
  "top_n": 5
}
```

### Get Similar Courses

```json
POST /invocations
{
  "course_id": "COURSE_001",
  "top_n": 5
}
```

## Configuration

| Variable | Description |
|----------|-------------|
| `ECR_IMAGE_URI` | Your Docker image URI in ECR |
| `S3_MODEL_URI` | S3 path to model.tar.gz |
| `SAGEMAKER_ROLE` | IAM role ARN for SageMaker |
| `ENDPOINT_NAME` | Name for your SageMaker endpoint |
| `INSTANCE_TYPE` | EC2 instance type (e.g., ml.t2.medium) |

## Local Testing

```bash
# Run the FastAPI server locally
SM_MODEL_DIR=. uvicorn src.app:app --host 0.0.0.0 --port 8080
```

## License

MIT



