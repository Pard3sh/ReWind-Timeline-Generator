# Rewind Timeline Generator Cloud Overview

## Overview

We use the Cloud Shell to build and push our our timeline generator container to the Google Cloud Platform's Artifact Registery, which is a platform to host containers that can be run as jobs or services. This allows us to have a recurring job that analyzes previously unanalyzed entries and updates/creates the timeline data for each folder. This is done to make the ReWind Journal Application less heavy on the user's device. Generated timelines are uploaded to the cloud databse (firestore) which is then propagated to the user's device and displayed as UI timelines.

Start by visiting the cloud shell console on the google cloud platform, must be a team member and signed in: https://console.cloud.google.com/welcome?project=final-project-494621&cloudshell=true.

## How to Use

Whenever there is an update to the ReWind-Timeline-Generator repository, run the following commands.

```bash
# make sure you are on this page and connected to the cloud shell terminal
# https://console.cloud.google.com/welcome?project=final-project-494621&cloudshell=true

# ensure you are on the project directory
cd ReWind-Timeline-Generator

# pull latest changes
git pull

# google cloud config steps

gcloud config set project final-project-494621

gcloud auth configure-docker us-central1-docker.pkg.dev

# build iamge -- will take a couple minutes but should not exceed 10 minutes
docker build -t us-central1-docker.pkg.dev/final-project-494621/timeline-generator/timeline-generator:latest .

# push image to Artifact Registry
docker push us-central1-docker.pkg.dev/final-project-494621/timeline-generator/timeline-generator:latest

# The rest of the steps are completed in the Google Cloud Platform UI

```

### Go to Google Cloud Platform

Go to Cloud Run Page

Select the job (currently called timeline-generator-batch)

Click view and edit job configuration.

**Click select on the Container Image URL field**. Click us-central... then click timeline-generator. Then select the option that comes with the "latest" tag.

Paste API key from local .env into variables and secrets with appropriate label (consult .env.example for help)

Ensure we have the firebase admin account (Containers, Connection, Security) In security, select the firebase admin.

Ensure job has 2-4 gbs.

Select run immediately and leave other settings unless new issues arise.

Click update and watch to make sure job runs properly.

This will be scheduled as an automatic service but not implemented yet :)
