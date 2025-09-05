# Cooking Web

Simple Flask application for uploading and viewing cooking videos.

## Features
- Producer uploads videos at `/upload` using a password.
- Public can watch videos, like them, and leave comments on the home page.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. (Optional) Set a custom password for uploads:
   ```bash
   export PRODUCER_PASSWORD=mysecret
   ```
3. Run the app:
   ```bash
   python app.py
   ```
4. Visit `http://localhost:5000` to view videos or `http://localhost:5000/upload` to upload.
