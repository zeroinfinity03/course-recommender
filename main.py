

import json
import os
from typing import Optional, Any, Dict

import boto3
from botocore.config import Config
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SAGEMAKER_ENDPOINT_NAME = os.getenv("SAGEMAKER_ENDPOINT_NAME")

if not SAGEMAKER_ENDPOINT_NAME:
    raise RuntimeError(
        "Missing env var SAGEMAKER_ENDPOINT_NAME. "
        "Example: export SAGEMAKER_ENDPOINT_NAME=course-reco-endpoint"
    )

boto_config = Config(
    region_name=AWS_REGION,
    read_timeout=30,
    connect_timeout=10,
    retries={"max_attempts": 3, "mode": "standard"},
)

sm_runtime = boto3.client("sagemaker-runtime", config=boto_config)

app = FastAPI(title="Course Reco Proxy API", version="1.0.0")


class RecoRequest(BaseModel):
    user_id: Optional[int] = Field(default=None, ge=0)
    course_id: Optional[str] = None
    top_n: int = Field(default=5, ge=1, le=50)


@app.get("/ping")
def ping() -> Dict[str, Any]:
    return {"status": "ok", "region": AWS_REGION, "endpoint": SAGEMAKER_ENDPOINT_NAME}


def _invoke_sagemaker(payload: Dict[str, Any]) -> Any:
    try:
        resp = sm_runtime.invoke_endpoint(
            EndpointName=SAGEMAKER_ENDPOINT_NAME,
            ContentType="application/json",
            Accept="application/json",
            Body=json.dumps(payload).encode("utf-8"),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"SageMaker invoke failed: {str(e)}")

    raw = resp["Body"].read()
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=502, detail=f"Non-JSON response from SageMaker: {raw[:500]!r}")


@app.post("/recommend")
def recommend(req: RecoRequest) -> Any:
    if (req.user_id is None and req.course_id is None) or (req.user_id is not None and req.course_id is not None):
        raise HTTPException(status_code=400, detail="Provide exactly one: user_id OR course_id")

    payload: Dict[str, Any] = {"top_n": req.top_n}
    if req.user_id is not None:
        payload["user_id"] = req.user_id
    else:
        payload["course_id"] = req.course_id

    return _invoke_sagemaker(payload)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("proxy_api:app", host="0.0.0.0", port=8000, reload=True)





