import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import os
import tarfile

# Configuration
DATA_DIR = "data"
ARTIFACTS_DIR = "."  # Save to project root for easy S3 upload

os.makedirs(ARTIFACTS_DIR, exist_ok=True)

print("Starting Training...")






# 1. Load Data
try:
    courses_df = pd.read_csv(os.path.join(DATA_DIR, 'courses.csv'))
    enrollments_df = pd.read_csv(os.path.join(DATA_DIR, 'enrollments.csv'))
except FileNotFoundError:
    print(f"Error: Data files not found in '{DATA_DIR}/'")
    exit(1)

print(f"Courses loaded: {len(courses_df)}")
print(f"Enrollments loaded: {len(enrollments_df)}")






# 2. Preprocessing (Matching your notebook logic)
print("Cleaning text features...")
def clean_text(text):
    if pd.isna(text): return ""
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()






# Apply cleaning to ALL columns you used in the notebook
courses_df['clean_title'] = courses_df['title'].apply(clean_text)
courses_df['clean_description'] = courses_df['description'].apply(clean_text)
courses_df['clean_skill_tags'] = courses_df['skill_tags'].apply(clean_text)
courses_df['clean_difficulty'] = courses_df['difficulty'].apply(clean_text)





# Feature Enrichment: Combine all these columns
print("Creating combined features...")
courses_df['combined_features'] = (
    courses_df['clean_title'] + ' ' +
    courses_df['clean_description'] + ' ' +
    courses_df['clean_skill_tags'] + ' ' +
    courses_df['clean_difficulty']
)





# 3. TF-IDF & Similarity (Using your specific settings)
print("Computing TF-IDF and Similarity Matrix...")
tfidf = TfidfVectorizer(
    stop_words='english',
    max_features=5000,     # Restored from notebook
    ngram_range=(1, 2)     # Restored from notebook
)

tfidf_matrix = tfidf.fit_transform(courses_df['combined_features'])
similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

print(f"TF-IDF Matrix Shape: {tfidf_matrix.shape}")
print(f"Similarity Matrix Shape: {similarity_matrix.shape}")







# 4. Save Artifacts
print("Saving Model Artifacts...")
course_id_to_idx = {cid: i for i, cid in enumerate(courses_df["course_id"])}

artifacts = {
    "courses_df": courses_df,
    "enrollments_df": enrollments_df,
    "similarity_matrix": similarity_matrix,
    "course_id_to_idx": course_id_to_idx,
}

save_path = os.path.join(ARTIFACTS_DIR, "reco_artifacts.joblib")
joblib.dump(artifacts, save_path, compress=3)
print(f"Model saved to {save_path}")


# 5. Create model.tar.gz for SageMaker
print("Creating model.tar.gz for SageMaker...")
tar_path = "model.tar.gz"  # Saved in project root (12. mlops/)
with tarfile.open(tar_path, "w:gz") as tar:
    tar.add(save_path, arcname="reco_artifacts.joblib")

print(f"Done! Package created: {tar_path}")










