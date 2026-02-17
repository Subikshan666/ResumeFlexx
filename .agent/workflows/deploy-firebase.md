---
description: how to deploy the Resume Analyzer to Firebase
---

# Deploying Resume Analyzer to Firebase App Hosting (recommended for Flask)

Since this is a Flask application (Python), the best way to deploy it to Firebase is using **Firebase App Hosting** or **Firebase Functions**. Given the app uses a local database (`resume_history.db`), we need to consider that serverless environments like Firebase Functions are stateless.

### Prerequisites
- Firebase CLI installed (Verified: v15.3.1)
- Logged into Firebase (`firebase login`)
- Project created on Firebase Console

### Step-by-Step Deployment (Firebase App Hosting / Cloud Run)

1. **Prepare for Containerization**
   Create a `Dockerfile` to containerize the Flask app.
   
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
```

2. **Add Gunicorn to requirements.txt**
   Ensure `gunicorn` is in your `requirements.txt`.

3. **Initialize App Hosting**
   // turbo
   `firebase apphosting:backends:create --project <your-project-id>`

4. **Deploy**
   App Hosting usually integrates with GitHub. Push your code to a repository and link it during the backend creation.

### Alternative: Firebase Hosting (Static Only)
If you only want to host the frontend and use Firebase as a backend API:
1. `firebase init hosting`
2. Select your project.
3. Set `public` directory (you'd need to adapt the Flask app to be a SPA or use a different backend).

**Note:** For a full Flask app with a database, **Google Cloud Run** (which Firebase App Hosting uses under the hood) is the most robust path.
