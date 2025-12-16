# Course Recommendation System - MLOps Pipeline

An end-to-end MLOps pipeline for a course recommendation engine, deployed on AWS SageMaker. Uses TF-IDF vectorization with feature enrichment and cosine similarity to recommend courses based on user enrollment history.

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────────┐
│  Training Data  │────▶│  train.py    │────▶│ reco_artifacts.joblib│
│  (CSV files)    │     │  (ML Model)  │     │   (Model Artifact)   │
└─────────────────┘     └──────────────┘     └──────────┬──────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌──────────────┐     ┌─────────────────────┐
│   deploy.py     │────▶│   Docker     │────▶│   AWS ECR           │
│ (Build & Push)  │     │   Image      │     │   (Container Registry)│
└─────────────────┘     └──────────────┘     └──────────┬──────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌──────────────┐     ┌─────────────────────┐
│   Your App      │────▶│  main.py     │────▶│  SageMaker Endpoint │
│ (Frontend/API)  │     │ (Proxy API)  │     │  (app.py running)   │
└─────────────────┘     └──────────────┘     └─────────────────────┘
```

## Project Structure

```
12. mlops/
├── .dockerignore           # Files excluded from Docker build
├── .gitignore              # Files excluded from Git
├── .python-version         # Python version (3.11)
├── Dockerfile              # Container config for SageMaker
├── entrypoint.sh           # Docker entrypoint script (handles 'serve' command)
├── deploy.py               # One-click deployment to AWS ECR
├── main.py                 # Proxy API to call SageMaker endpoint
├── pyproject.toml          # Python dependencies (managed by uv)
├── uv.lock                 # Locked dependency versions
├── README.md               # This file
├── data/
│   ├── courses.csv         # Course catalog (100 courses)
│   └── enrollments.csv     # User enrollment history (219 records)
└── src/
    ├── train.py            # Training script - generates model artifacts
    ├── app.py              # FastAPI inference server (runs in SageMaker)
    └── reco_artifacts.joblib   # Trained model artifact (generated)
```

## File Descriptions

| File | Purpose |
|------|---------|
| `Dockerfile` | SageMaker-compatible container using Python 3.11 and uv |
| `entrypoint.sh` | Handles SageMaker's `docker run <image> serve` command |
| `.dockerignore` | Excludes data/, .venv/, train.py from Docker image |
| `.gitignore` | Excludes .venv/, data/, *.joblib, __pycache__/ from Git |
| `deploy.py` | Builds Docker image (linux/amd64) and pushes to ECR |
| `main.py` | Proxy API that calls SageMaker endpoint (for local testing) |
| `src/train.py` | Trains TF-IDF model and saves artifacts |
| `src/app.py` | FastAPI server with `/ping` and `/invocations` endpoints |

## How It Works

### 1. Training Pipeline (`src/train.py`)

1. **Load Data**: Reads courses and enrollments from CSV files
2. **Preprocessing**: Cleans text (lowercase, remove special chars)
3. **Feature Enrichment**: Combines title + description + skill_tags + difficulty
4. **TF-IDF Vectorization**: Converts text to vectors (max 5000 features, 1-2 ngrams)
5. **Similarity Matrix**: Computes cosine similarity between all courses
6. **Save Artifacts**: Exports model to `reco_artifacts.joblib`

### 2. Inference API (`src/app.py`)

FastAPI server with SageMaker-compatible endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/ping` | GET | Health check (returns 200 if model loaded) |
| `/invocations` | POST | Prediction endpoint |

**Two Prediction Modes:**

```json
// Mode 1: Get recommendations for a user
{"user_id": "U0001", "top_n": 5}

// Mode 2: Find similar courses  
{"course_id": "C0001", "top_n": 5}
```

### 3. Docker Container

- Uses `entrypoint.sh` to handle SageMaker's `serve` argument
- Built for `linux/amd64` platform (SageMaker requirement)
- Uses `--provenance=false` to avoid OCI manifest issues

## Quick Start

### 1. Setup Environment

```bash
cd "12. mlops"
uv sync
source .venv/bin/activate
```

### 2. Train the Model

```bash
uv run src/train.py
```

Output:
```
Starting Training...
Courses loaded: 100
Enrollments loaded: 219
Computing TF-IDF and Similarity Matrix...
Done! Model saved to src/reco_artifacts.joblib
```

### 3. Test Locally

```bash
uv run src/app.py
```

Then test with curl:

```bash
# Health check
curl http://localhost:8080/ping

# Get user recommendations
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"user_id": "U0001"}'

# Get similar courses
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"course_id": "C0001"}'
```

### 4. Deploy to AWS

```bash
uv run deploy.py
```

This will:
1. Login to AWS ECR
2. Create repository (if needed)
3. Build Docker image for linux/amd64
4. Push to ECR

### 5. Create SageMaker Endpoint (AWS Console)

1. **Create Model**: Use the ECR image URI
2. **Create Endpoint Configuration**: Select instance type (e.g., `ml.t2.medium`)
3. **Create Endpoint**: Wait for status "InService"

### 6. Test SageMaker Endpoint

```bash
aws sagemaker-runtime invoke-endpoint \
  --endpoint-name course-reco-endpoint \
  --content-type application/json \
  --body '{"user_id": "U0001"}' \
  out.json && cat out.json
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework for API |
| `uvicorn` | ASGI server |
| `pandas` | Data manipulation |
| `scikit-learn` | TF-IDF and cosine similarity |
| `joblib` | Model serialization |
| `boto3` | AWS SDK (for proxy API) |

## Configuration

### deploy.py

```python
REPO_NAME = "course-recommender"  # ECR repository name
REGION = "us-east-1"              # AWS region
```

### main.py (Proxy API)

```bash
export SAGEMAKER_ENDPOINT_NAME=course-reco-endpoint
export AWS_REGION=us-east-1
```

## AWS Setup

### 1. Install AWS CLI

```bash
uv tool install awscli
```

### 2. Configure Credentials

```bash
aws configure
# Access Key ID: <from IAM>
# Secret Access Key: <from IAM>
# Region: us-east-1
# Output: json
```

### 3. Verify Setup

```bash
aws sts get-caller-identity
aws ecr describe-repositories --region us-east-1
```

### 4. Required IAM Permissions

- ECR: `AmazonEC2ContainerRegistryFullAccess`
- SageMaker: `AmazonSageMakerFullAccess`

## Troubleshooting

### OCI Manifest Error
If you see "Unsupported manifest media type", ensure `deploy.py` uses:
```bash
docker build --platform linux/amd64 --provenance=false ...
```

### Container Start Error
If endpoint fails with "CannotStartContainerError", ensure `entrypoint.sh` exists and handles the `serve` argument.

### Model Not Loading
Check CloudWatch logs at: `/aws/sagemaker/Endpoints/<endpoint-name>`

## Data Format

### courses.csv
```csv
course_id,title,description,skill_tags,difficulty,category
C0001,Intro to Computer Vision,"A project-driven course...",ml fundamentals,Beginner,Web Dev
```

### enrollments.csv
```csv
user_id,user_name,user_email,course_id
U0001,Ananya Das,ananya.das1@example.com,C0008
```

## Requirements

- Python 3.11+
- Docker Desktop
- AWS CLI (configured)
- uv package manager









































