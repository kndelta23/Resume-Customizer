#!/bin/bash

# Configuration
PROJECT_ID="resume-customizer-484719"
FUNCTION_NAME="resume-customizer"
REGION="us-central1"
RUNTIME="python310"
ENTRY_POINT="customize_resume"

echo "Deploying Cloud Function: $FUNCTION_NAME..."

gcloud functions deploy $FUNCTION_NAME \
    --gen2 \
    --project=$PROJECT_ID \
    --region=$REGION \
    --runtime=$RUNTIME \
    --source=. \
    --entry-point=$ENTRY_POINT \
    --trigger-http \
    --set-env-vars GEMINI_API_KEY=AIzaSyCfDRlJRL2BH8i-FXg-5WykCkNZHg_cFbY \
    --allow-unauthenticated

echo "Deployment initiated. Check the output above for the URL."
