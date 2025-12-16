"""
AWS Lambda function to invoke SageMaker Endpoint.
This acts as a bridge between API Gateway and SageMaker.

Deploy this code to AWS Lambda Console.
"""

import json
import boto3
import os

# Configuration (set these as Lambda environment variables)
ENDPOINT_NAME = os.environ.get("SAGEMAKER_ENDPOINT_NAME", "course-reco-endpoint")
REGION = os.environ.get("AWS_REGION", "us-east-1")

# Initialize SageMaker runtime client
runtime = boto3.client("sagemaker-runtime", region_name=REGION)


def lambda_handler(event, context):
    """
    Main Lambda handler.
    Receives request from API Gateway, forwards to SageMaker, returns response.
    """
    try:
        # Parse the request body
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        else:
            body = event.get("body") or event
        
        # Invoke SageMaker endpoint
        response = runtime.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType="application/json",
            Body=json.dumps(body)
        )
        
        # Parse SageMaker response
        result = json.loads(response["Body"].read().decode())
        
        # Return success response (API Gateway format)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",  # Enable CORS for frontend
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            },
            "body": json.dumps(result)
        }
    
    except Exception as e:
        # Return error response
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": str(e)})
        }
