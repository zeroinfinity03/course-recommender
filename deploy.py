


import boto3
import time
from datetime import datetime


# ECR URI
image_uri = "720090397062.dkr.ecr.us-east-1.amazonaws.com/course-image-api:latest"

# S3 Model URI
model_data = "s3://coursetraineddata/model.tar.gz"

# IAM Role ARN
role_arn = "arn:aws:iam::720090397062:role/SageMakerExecutionRole"

client = boto3.client("sagemaker", region_name="us-east-1")










# Unique Names (Timestamp to avoid name conflicts)
timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
model_name = f"course-reco-model-{timestamp}"
endpoint_config_name = f"course-reco-config-{timestamp}"
endpoint_name = "course-reco-endpoint"  # Fixed name for easier access

print(f"Deploying to AWS Region: us-east-1")
print(f"Model Name: {model_name}")






# 1. Create Model (Brain + Body)
print("\nStep 1: Creating SageMaker Model")
client.create_model(
    ModelName=model_name,
    PrimaryContainer={
        "Image": image_uri,
        "ModelDataUrl": model_data,
    },
    ExecutionRoleArn=role_arn
)
print("Model Created!")





# 2. Create Endpoint Config (Hardware Settings)
print("\nStep 2: Creating Endpoint ")
client.create_endpoint_config(
    EndpointConfigName=endpoint_config_name,
    ProductionVariants=[
        {
            "VariantName": "AllTraffic",
            "ModelName": model_name,
            "InitialInstanceCount": 1,
            "InstanceType": "ml.t2.medium",
        }
    ]
)
print("Endpoint Config Created!")







# 3. Create Endpoint (The Server)
print("\nStep 3: Creating Endpoint (This takes 5-10 mins)...")
try:
    client.create_endpoint(
        EndpointName=endpoint_name,
        EndpointConfigName=endpoint_config_name
    )
    print("Creating Endpoint so I have to wait here")
except client.exceptions.ResourceInUse:
    print(f"Endpoint '{endpoint_name}' already exists. Deleting it first...")
    client.delete_endpoint(EndpointName=endpoint_name)
    time.sleep(10)
    client.create_endpoint(
        EndpointName=endpoint_name,
        EndpointConfigName=endpoint_config_name
    )
    print("Re-creating Endpoint...")









# 4. Waiter (Script waits until deployment completes)
waiter = client.get_waiter("endpoint_in_service")
waiter.wait(EndpointName=endpoint_name)

print(f"\nDeployment ho gya! ab woh edpoint live hai: {endpoint_name}")




























































'''

import boto3
import time
from datetime import datetime


# ECR URI
image_uri = "720090397062.dkr.ecr.us-east-1.amazonaws.com/course-image-api:latest"

# S3 Model URI
model_data = "s3://coursetraineddata/model.tar.gz"

# IAM Role ARN
role_arn = "arn:aws:iam::720090397062:role/SageMakerExecutionRole"

client = boto3.client("sagemaker", region_name="us-east-1")










# Unique Names (Timestamp to avoid name conflicts)
timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
model_name = f"course-reco-model-{timestamp}"
endpoint_config_name = f"course-reco-config-{timestamp}"
endpoint_name = "course-reco-endpoint"  # Fixed name for easier access

print(f"Deploying to AWS Region: us-east-1")
print(f"Model Name: {model_name}")






# 1. Create Model (Brain + Body)
print("\nStep 1: Creating SageMaker Model")
client.create_model(
    ModelName=model_name,
    PrimaryContainer={
        "Image": image_uri,
        "ModelDataUrl": model_data,
    },
    ExecutionRoleArn=role_arn
)
print("Model Created!")





# 2. Create Endpoint Config (Hardware Settings)
print("\nStep 2: Creating Endpoint ")
client.create_endpoint_config(
    EndpointConfigName=endpoint_config_name,
    ProductionVariants=[
        {
            "VariantName": "AllTraffic",
            "ModelName": model_name,
            "InitialInstanceCount": 1,
            "InstanceType": "ml.t2.medium",
        }
    ]
)
print("Endpoint Config Created!")







# 3. Create Endpoint (The Server)
print("\nStep 3: Creating Endpoint (This takes 5-10 mins)...")
try:
    client.create_endpoint(
        EndpointName=endpoint_name,
        EndpointConfigName=endpoint_config_name
    )
    print("Creating Endpoint so I have to wait here")
except Exception as e:
    # Step 3b: catch both ResourceInUse and ValidationException (which SageMaker throws for existing endpoints)
    error_msg = str(e)
    if "ResourceInUse" in error_msg or "Cannot create already existing endpoint" in error_msg:
        print(f"Endpoint '{endpoint_name}' already exists. Deleting it first...")
        
        try:
            client.delete_endpoint(EndpointName=endpoint_name)
        except:
            pass # If delete fails (e.g. already deleting), just move on
            
        time.sleep(20) # Wait for deletion to propagate
        
        client.create_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=endpoint_config_name
        )
        print("Re-creating Endpoint...")
    else:
        # If it's some other error, fail genuinely
        raise e









# 4. Waiter (Script waits until deployment completes)
waiter = client.get_waiter("endpoint_in_service")
waiter.wait(EndpointName=endpoint_name)

print(f"\nDeployment ho gya! ab woh edpoint live hai: {endpoint_name}")


'''














































