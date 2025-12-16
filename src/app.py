from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import joblib
import pandas as pd
import os
import uvicorn

app = FastAPI()
model_artifacts = None

# --- 1. Load Model ---
# SageMaker extracts model.tar.gz to /opt/ml/model/
MODEL_DIR = os.environ.get("SM_MODEL_DIR", "/opt/ml/model")

def load_model():
    global model_artifacts
    path = os.path.join(MODEL_DIR, "reco_artifacts.joblib")
    try:
        model_artifacts = joblib.load(path)
        print(f"Model loaded successfully from {path}")
    except Exception as e:
        print(f"Error loading model from {path}: {e}")
        model_artifacts = None

# Load immediately on startup
load_model()

# --- 2. Core Logic ---
def get_similar_courses_logic(course_id, top_n=5):
    """
    Finds courses similar to a specific course_id using the cosine similarity matrix.
    """
    courses_df = model_artifacts["courses_df"]
    similarity_matrix = model_artifacts["similarity_matrix"]
    course_id_to_idx = model_artifacts["course_id_to_idx"]
    
    if course_id not in course_id_to_idx:
        return []

    idx = course_id_to_idx[course_id]
    scores = list(enumerate(similarity_matrix[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    
    # Skip the first one (index 0) because it is the course itself
    similar_indices = [i[0] for i in scores[1:top_n+1]]
    
    result = courses_df.iloc[similar_indices][['course_id', 'title', 'difficulty', 'category']]
    return result.to_dict(orient="records")

def get_user_recommendations_logic(user_id, top_n=5):
    """
    Generates recommendations for a user based on their past enrollments.
    """
    enrollments_df = model_artifacts["enrollments_df"]
    
    # Get courses this user has taken
    user_courses = enrollments_df.loc[enrollments_df["user_id"] == user_id, "course_id"].tolist()
    
    if not user_courses:
        return {"error": f"No enrollments found for user {user_id}"}

    user_courses_set = set(user_courses)
    similar_courses = {}

    # For every course the user took, find similar courses
    for cid in user_courses_set:
        # Get top 10 similar for each course taken
        sim_data = get_similar_courses_logic(cid, top_n=10)
        
        for item in sim_data:
            rec_cid = item["course_id"]
            
            # Do not recommend courses the user has already taken
            if rec_cid in user_courses_set: 
                continue
            
            if rec_cid not in similar_courses:
                similar_courses[rec_cid] = {
                    "count": 0, 
                    "title": item["title"], 
                    "category": item["category"]
                }
            
            # Increment score (more appearances = better recommendation)
            similar_courses[rec_cid]["count"] += 1

    # Sort by count (descending)
    ranked = sorted(similar_courses.items(), key=lambda x: x[1]["count"], reverse=True)
    
    results = []
    for cid, meta in ranked[:top_n]:
        results.append({
            "course_id": cid, 
            "title": meta["title"],
            "category": meta["category"],
            "score": meta["count"]
        })
        
    return {"user_id": user_id, "recommendations": results}

# --- 3. SageMaker Endpoints ---

@app.get("/ping")
async def ping():
    """
    Health check for SageMaker.
    """
    if model_artifacts:
        return Response(status_code=200)
    else:
        return Response(status_code=500)

@app.post("/invocations")
async def predict(request: Request):
    """
    Main prediction endpoint. Handles both User Recommendations and Similar Courses.
    """
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(content={"error": "Invalid JSON"}, status_code=400)
    
    # Logic Switch based on input keys
    if "user_id" in data:
        # Mode 1: Recommend for a User
        user_id = data["user_id"]
        top_n = data.get("top_n", 5)
        result = get_user_recommendations_logic(user_id, top_n)
        return JSONResponse(content=result)

    elif "course_id" in data:
        # Mode 2: Find Similar Courses
        course_id = data["course_id"]
        top_n = data.get("top_n", 5)
        result = get_similar_courses_logic(course_id, top_n)
        return JSONResponse(content=result)
        
    else:
        return JSONResponse(content={"error": "Invalid input. Provide 'user_id' OR 'course_id'"}, status_code=400)

if __name__ == "__main__":
    # Local testing entrypoint
    uvicorn.run(app, host="0.0.0.0", port=8080)


    