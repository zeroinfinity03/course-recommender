
import boto3
import json

# Configuration
ENDPOINT_NAME = "course-reco-endpoint"
REGION = "us-east-1"

# Initialize client
runtime = boto3.client("sagemaker-runtime", region_name=REGION)


def invoke_endpoint(payload):
    """Send request to SageMaker endpoint and return response."""
    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType="application/json",
        Body=json.dumps(payload)
    )
    result = json.loads(response["Body"].read().decode())
    return result


def test_user_recommendations():
    """Test getting recommendations for a user."""
    print("=" * 50)
    print("Test 1: User Recommendations")
    print("=" * 50)
    
    payload = {"user_id": "U0001", "top_n": 5}
    print(f"Request: {payload}")
    
    result = invoke_endpoint(payload)
    print(f"Response: {json.dumps(result, indent=2)}")
    return result


def test_similar_courses():
    """Test getting similar courses."""
    print("\n" + "=" * 50)
    print("Test 2: Similar Courses")
    print("=" * 50)
    
    payload = {"course_id": "C0001", "top_n": 5}
    print(f"Request: {payload}")
    
    result = invoke_endpoint(payload)
    print(f"Response: {json.dumps(result, indent=2)}")
    return result


if __name__ == "__main__":
    print("\nTesting SageMaker Endpoint:", ENDPOINT_NAME)
    print()
    
    try:
        test_user_recommendations()
        test_similar_courses()
        print("\n" + "=" * 50)
        print("All tests completed!")
        print("=" * 50)
    except Exception as e:
        print(f"\nError: {e}")
