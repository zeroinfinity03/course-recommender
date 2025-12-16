


### Phase 1: Manual Setup (Pehle khud chalana seekho)*Goal: Sab kuch AWS par manually setup karna taaki ensure ho sake ki logic sahi hai.*

1. **Train & Package (Local):**
* `train.py` run karo -> Model file (`.joblib`) create hogi.
* Is file ko compress karke `model.tar.gz` banao.


2. **Model Storage (S3):**
* AWS Console se S3 Bucket banao. bucket versioning enable karein.
* `model.tar.gz` ko manually upload karo.


3. **Containerize (ECR):**
* AWS Console se ECR Repository banao.
* Local terminal se `docker build` command chalao.
* Image ko ECR mein push karo (`docker push`).


4. **Deploy Endpoint (SageMaker):**
* Local se `deploy.py` script run karo.
* Ye script S3 (Model) aur ECR (Image) ko jodkar ek **Real-time Endpoint** khada karegi.


5. **Connect Backend (Lambda):**
* Ek naya Lambda function banao.
* Usme code daalo jo SageMaker Endpoint ko invoke kare.
* API Gateway jodkar URL generate karo.
* API Gateway -> Lambda -> `boto3` invoke SageMaker.


------


### Phase 2: CI/CD Setup (Automation)*Goal: Main branch par code push karte hi naya version live ho jaye (No manual commands).*

Humein GitHub Actions use karna hai. Iske liye hum ek file banayenge `.github/workflows/deploy.yml`. Uske andar ye steps honge:

**Prerequisite:**

* GitHub Repo ki "Settings -> Secrets" mein AWS Access Keys (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) daalni hongi.

**The Automation Flow (Pipeline Steps):**

1. **Trigger:**
* Jaise hi tum GitHub par code push karoge (`git push origin main`), ye pipeline start ho jayegi.


2. **Checkout Code:**
* GitHub ka server tumhara latest code download karega.


3. **Configure AWS Credentials:**
* GitHub server tumhare Secrets use karke AWS mein login karega.


4. **Login to ECR:**
* Server AWS ECR se connect karega taaki image upload kar sake.


5. **Build & Push Docker Image:**
* Server wahi `docker build` aur `docker push` commands chalayega jo tumne Phase 1 mein manual kiye the.
* Nayi image ECR mein update ho jayegi.


6. **Update SageMaker Endpoint:**
* Server tumhara `deploy.py` script chalayega.
* SageMaker ko signal jayega: *"Nayi image aa gayi hai, purane server ko hatao aur naya server lagao (Rolling Update)."*

----

