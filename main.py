

import json
import os
import boto3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Configuration
ENDPOINT_NAME = os.environ.get("SAGEMAKER_ENDPOINT_NAME", "course-reco-endpoint")
REGION = os.environ.get("AWS_REGION", "us-east-1")

# Initialize SageMaker client
runtime = boto3.client("sagemaker-runtime", region_name=REGION)

app = FastAPI(
    title="Course Recommendation API",
    description="Test endpoints for SageMaker model",
    version="1.0.0"
)


# Request Models
class UserRequest(BaseModel):
    user_id: str = Field(example="U0001", description="User ID to get recommendations for")
    top_n: int = Field(default=5, ge=1, le=20, description="Number of recommendations")


class CourseRequest(BaseModel):
    course_id: str = Field(example="C0001", description="Course ID to find similar courses")
    top_n: int = Field(default=5, ge=1, le=20, description="Number of similar courses")


def invoke_sagemaker(payload: dict):
    """Call SageMaker endpoint and return response."""
    try:
        response = runtime.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType="application/json",
            Body=json.dumps(payload)
        )
        return json.loads(response["Body"].read().decode())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SageMaker error: {str(e)}")


@app.get("/")
def root():
    """Health check."""
    return {"status": "ok", "endpoint": ENDPOINT_NAME}


@app.post("/recommend/user")
def recommend_for_user(request: UserRequest):
    """
    Get course recommendations for a user based on their enrollment history.
    """
    payload = {"user_id": request.user_id, "top_n": request.top_n}
    return invoke_sagemaker(payload)


@app.post("/recommend/course")
def recommend_similar_courses(request: CourseRequest):
    """
    Get similar courses for a given course.
    """
    payload = {"course_id": request.course_id, "top_n": request.top_n}
    return invoke_sagemaker(payload)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", reload=True)







# lsof -ti:8000 | xargs kill -9

