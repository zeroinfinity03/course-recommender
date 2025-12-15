import os
import subprocess
import sys

# --- Configuration ---
REPO_NAME = "course-recommender"
REGION = "us-east-1"

# --- Automatic Credential Fetching ---
print("Fetching AWS Credentials...")
ACCOUNT_ID = subprocess.getoutput("aws sts get-caller-identity --query Account --output text")

# Check if login worked
if "unable to locate credentials" in ACCOUNT_ID.lower() or "error" in ACCOUNT_ID.lower():
    print("Error: AWS CLI is not logged in.")
    print("Please run 'aws configure' in your terminal and try again.")
    sys.exit(1)

IMAGE_URI = f"{ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com/{REPO_NAME}:latest"

print(f"Found Account ID: {ACCOUNT_ID}")
print(f"Starting deployment for: {REPO_NAME}")
print(f"Region: {REGION}")
print(f"Target: {IMAGE_URI}")

# --- The Commands ---
commands = [
    # 1. Login to ECR
    f"aws ecr get-login-password --region {REGION} | docker login --username AWS --password-stdin {ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com",
    
    # 2. Create Repository (ignore error if exists)
    f"aws ecr create-repository --repository-name {REPO_NAME} --region {REGION} || true",
    
    # 3. Build Docker Image (force linux/amd64 for SageMaker)
    f"docker build --platform linux/amd64 --provenance=false -t {REPO_NAME} .",
    
    # 4. Tag Image
    f"docker tag {REPO_NAME}:latest {IMAGE_URI}",
    
    # 5. Push to AWS ECR
    f"docker push {IMAGE_URI}"
]

for cmd in commands:
    print(f"\nRunning: {cmd}")
    result = os.system(cmd)
    if result != 0:
        print("Failed. Stopping here.")
        sys.exit(1)

print(f"\nSuccess! Image uploaded to: {IMAGE_URI}")
print("You are now ready to create a SageMaker Endpoint!")




