# Course Recommendation System - MLOps Pipeline

A production-ready course recommendation engine deployed on AWS SageMaker. Uses TF-IDF vectorization with feature enrichment and cosine similarity to recommend courses based on user enrollment history.

## Project Structure

```
12. mlops/
├── Dockerfile              # Container config for SageMaker
├── .dockerignore           # Files excluded from Docker build
├── .gitignore              # Files excluded from Git
├── deploy.py               # One-click deployment to AWS ECR
├── pyproject.toml          # Python dependencies (managed by uv)
├── uv.lock                 # Locked dependency versions
├── data/
│   ├── courses.csv         # Course catalog (100 courses)
│   └── enrollments.csv     # User enrollment history (219 records)
└── src/
    ├── train.py            # Training script - generates model artifacts
    ├── app.py              # FastAPI inference server
    └── reco_artifacts.joblib   # Trained model (generated)
```

## How It Works

### Training Pipeline (`src/train.py`)

1. **Load Data**: Reads courses and enrollments from CSV files
2. **Preprocessing**: Cleans text by lowercasing and removing special characters
3. **Feature Enrichment**: Combines title + description + skill_tags + difficulty
4. **TF-IDF Vectorization**: Converts text to numerical vectors (max 5000 features, 1-2 ngrams)
5. **Similarity Matrix**: Computes cosine similarity between all courses
6. **Save Artifacts**: Exports model to `reco_artifacts.joblib`

### Inference API (`src/app.py`)

FastAPI server with SageMaker-compatible endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/ping` | GET | Health check |
| `/invocations` | POST | Prediction endpoint |

**Two Prediction Modes:**

```json
// Mode 1: Get recommendations for a user
{"user_id": 123, "top_n": 5}

// Mode 2: Find similar courses
{"course_id": "C001", "top_n": 5}
```

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
  -d '{"user_id": 1}'

# Get similar courses
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"course_id": "C001"}'
```

### 4. Deploy to AWS

```bash
python deploy.py
```

This will:
- Login to AWS ECR
- Create repository (if needed)
- Build Docker image
- Push to ECR

## Dependencies

- **fastapi**: Web framework for the API
- **uvicorn**: ASGI server
- **pandas**: Data manipulation
- **scikit-learn**: TF-IDF and cosine similarity
- **joblib**: Model serialization

## Configuration

Edit `deploy.py` to change:

```python
REPO_NAME = "course-recommender"  # ECR repository name
REGION = "us-east-1"              # AWS region
```

## Requirements

- Python 3.11+
- Docker
- AWS CLI (configured with credentials)
- uv package manager





















# Install tools (if needed)
uv tool install awscli

# setup aws account, group and user then we will get csv credentials file, then we can do this to set it:

aws configure
region: us-east-1
output: json
aws sts get-caller-identity
aws configure list
aws ecr describe-repositories --region us-east-1




