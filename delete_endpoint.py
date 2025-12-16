"""
Delete SageMaker Endpoint and related resources.
Run with: uv run python delete_endpoint.py
"""

import boto3

# Configuration
ENDPOINT_NAME = "course-reco-endpoint"
REGION = "us-east-1"

client = boto3.client("sagemaker", region_name=REGION)


def delete_endpoint():
    """Delete the SageMaker endpoint."""
    try:
        print(f"Deleting endpoint: {ENDPOINT_NAME}...")
        client.delete_endpoint(EndpointName=ENDPOINT_NAME)
        print("Endpoint deleted!")
    except Exception as e:
        print(f"Error deleting endpoint: {e}")


def delete_endpoint_config():
    """Delete endpoint configurations (optional cleanup)."""
    try:
        print("Listing endpoint configs...")
        configs = client.list_endpoint_configs(NameContains="course-reco")
        for config in configs.get("EndpointConfigs", []):
            name = config["EndpointConfigName"]
            print(f"Deleting config: {name}")
            client.delete_endpoint_config(EndpointConfigName=name)
        print("Endpoint configs deleted!")
    except Exception as e:
        print(f"Error deleting configs: {e}")


def delete_models():
    """Delete models (optional cleanup)."""
    try:
        print("Listing models...")
        models = client.list_models(NameContains="course-reco")
        for model in models.get("Models", []):
            name = model["ModelName"]
            print(f"Deleting model: {name}")
            client.delete_model(ModelName=name)
        print("Models deleted!")
    except Exception as e:
        print(f"Error deleting models: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("SageMaker Cleanup Script")
    print("=" * 50)
    
    # Delete in order: Endpoint -> Config -> Model
    delete_endpoint()
    delete_endpoint_config()
    delete_models()
    
    print("\nCleanup complete! No more charges.")
