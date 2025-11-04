# Flask App CI/CD with Cloud Build

This project demonstrates a complete CI/CD pipeline for a Flask application using Google Cloud Build, Cloud Run, BigQuery, and Cloud Storage.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Architecture](#architecture)
- [Setup Instructions](#setup-instructions)
  - [1. Initial Setup](#1-initial-setup)
  - [2. Create GCP Infrastructure](#2-create-gcp-infrastructure)
  - [3. Download Sample Data](#3-download-sample-data)
  - [4. Configure Cloud Build Trigger](#4-configure-cloud-build-trigger)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Google Cloud Platform account
- `gcloud` CLI installed and configured
- Git and GitHub account
- Basic knowledge of Docker, Python, and GCP services

## Architecture

This application:
1. Builds a Docker image and pushes to Artifact Registry
2. Runs pytest tests
3. Deploys to Cloud Run
4. Loads data from Cloud Storage to BigQuery

**Services Used:**
- **Cloud Build**: CI/CD pipeline
- **Artifact Registry**: Docker image storage
- **Cloud Run**: Serverless container deployment
- **BigQuery**: Data warehouse
- **Cloud Storage**: File storage

## Setup Instructions

### 0. Fork and Set Up Your Repository

This repository is a public example. To use it for your own CI/CD pipeline, you'll need to create your own repository:

```bash
# Clone the example repository
git clone https://github.com/ulises-jimenez07/test-cicd-cloudbuild.git
cd test-cicd-cloudbuild

# Remove the existing .git directory
rm -rf .git

# Initialize a new git repository
git init

# Create a new repository on GitHub (do this via GitHub web interface first)
# Then add your new repository as the remote origin
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git

# Add all files to the new repository
git add .

# Create initial commit
git commit -m "Initial commit from template"

# Push to your new repository
git push -u origin main
```

**Important:** Make sure to create a new repository on GitHub before running the remote add command. You can create a new repo at [https://github.com/new](https://github.com/new).

### 1. Initial Setup

Set up environment variables for your project (customize these values):

```bash
# Set your project configuration
export PROJECT_ID=$(gcloud config get-value project)
export REGION="us-central1"
export ARTIFACT_REPO="app-repo"
export IMAGE_NAME="demo-flask-app"
export SERVICE_NAME="py-bq-load"
export BQ_DATASET="test_schema"
export BQ_TABLE="us_states"
export BUCKET_NAME="${PROJECT_ID}-data-bucket"
export CSV_FILE="us-states.csv"
```

### 2. Create GCP Infrastructure

#### Enable Required APIs

```bash
# Enable all necessary Google Cloud APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  bigquery.googleapis.com \
  storage.googleapis.com \
  secretmanager.googleapis.com
```

#### Create Artifact Registry Repository

```bash
# Create Docker repository in Artifact Registry
gcloud artifacts repositories create $ARTIFACT_REPO \
  --repository-format=docker \
  --location=$REGION \
  --description="Docker repository for Flask app"

# Verify creation
gcloud artifacts repositories list --location=$REGION
```

#### Create Cloud Storage Bucket

```bash
# Create a globally unique bucket
gcloud storage buckets create gs://$BUCKET_NAME \
  --location=$REGION \
  --uniform-bucket-level-access

# Verify creation
gcloud storage buckets list
```

#### Create BigQuery Dataset and Table

```bash
# Create BigQuery dataset
bq mk --dataset --location=$REGION $PROJECT_ID:$BQ_DATASET

# Create table schema for US states data
bq mk --table $PROJECT_ID:$BQ_DATASET.$BQ_TABLE \
  state:STRING,abbreviation:STRING,capital:STRING,population:INTEGER,area_sq_mi:INTEGER

# Verify creation
bq ls $PROJECT_ID:$BQ_DATASET
```

#### Grant Cloud Build Permissions

```bash
# Get Cloud Build service account
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${CLOUD_BUILD_SA}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${CLOUD_BUILD_SA}" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${CLOUD_BUILD_SA}" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${CLOUD_BUILD_SA}" \
  --role="roles/bigquery.admin"
```

### 3. Create Sample Data

Create US states CSV file and upload to Cloud Storage.

```bash
cat > us-states.csv << 'EOF'
state,abbreviation,capital,population,area_sq_mi
Alabama,AL,Montgomery,5024279,52420
Alaska,AK,Juneau,733391,665384
Arizona,AZ,Phoenix,7151502,113990
Arkansas,AR,Little Rock,3011524,53179
California,CA,Sacramento,39538223,163695
Colorado,CO,Denver,5773714,104094
Connecticut,CT,Hartford,3605944,5543
Delaware,DE,Dover,989948,2489
Florida,FL,Tallahassee,21538187,65758
Georgia,GA,Atlanta,10711908,59425
Hawaii,HI,Honolulu,1455271,10932
Idaho,ID,Boise,1839106,83569
Illinois,IL,Springfield,12812508,57914
Indiana,IN,Indianapolis,6785528,36420
Iowa,IA,Des Moines,3190369,56273
Kansas,KS,Topeka,2937880,82278
Kentucky,KY,Frankfort,4505836,40408
Louisiana,LA,Baton Rouge,4657757,52378
Maine,ME,Augusta,1362359,35380
Maryland,MD,Annapolis,6177224,12406
Massachusetts,MA,Boston,7029917,10554
Michigan,MI,Lansing,10077331,96714
Minnesota,MN,Saint Paul,5706494,86936
Mississippi,MS,Jackson,2961279,48432
Missouri,MO,Jefferson City,6154913,69707
Montana,MT,Helena,1084225,147040
Nebraska,NE,Lincoln,1961504,77348
Nevada,NV,Carson City,3104614,110572
New Hampshire,NH,Concord,1377529,9349
New Jersey,NJ,Trenton,9288994,8723
New Mexico,NM,Santa Fe,2117522,121590
New York,NY,Albany,20201249,54555
North Carolina,NC,Raleigh,10439388,53819
North Dakota,ND,Bismarck,779094,70698
Ohio,OH,Columbus,11799448,44826
Oklahoma,OK,Oklahoma City,3959353,69899
Oregon,OR,Salem,4237256,98379
Pennsylvania,PA,Harrisburg,13002700,46054
Rhode Island,RI,Providence,1097379,1545
South Carolina,SC,Columbia,5118425,32020
South Dakota,SD,Pierre,886667,77116
Tennessee,TN,Nashville,6910840,42144
Texas,TX,Austin,29145505,268596
Utah,UT,Salt Lake City,3271616,84897
Vermont,VT,Montpelier,643077,9616
Virginia,VA,Richmond,8631393,42775
Washington,WA,Olympia,7705281,71298
West Virginia,WV,Charleston,1793716,24230
Wisconsin,WI,Madison,5893718,65496
Wyoming,WY,Cheyenne,576851,97813
EOF
```

#### Upload to Cloud Storage

**Using gcloud CLI:**
```bash
# Upload to your Cloud Storage bucket
gcloud storage cp us-states.csv gs://$BUCKET_NAME/

# Verify upload
gcloud storage ls gs://$BUCKET_NAME/
```

### 4. Configure Cloud Build Trigger

Follow these steps to create a Cloud Build trigger using the Google Cloud Console:

#### Step 1: Navigate to Cloud Build Triggers

1. Open the [Google Cloud Console](https://console.cloud.google.com)
2. Select your project from the project dropdown
3. Navigate to **Cloud Build** → **Triggers** or go directly to [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers)

#### Step 2: Create a New Trigger

1. Click the **"Create Trigger"** button at the top of the page

#### Step 3: Configure Basic Settings

Fill in the following fields:

- **Name**: `py-bq-load-trigger` (or any descriptive name)
- **Description** (optional): `Build and deploy Flask app on push to main`
- **Event**: Select **"Push to a branch"**
- **Region**: Select your preferred region (e.g., `us-central1`)

#### Step 4: Connect Your Repository

1. Under **Source**, click **"Connect New Repository"** (if this is your first time) or select an existing connected repository
2. Select **"GitHub"** as the source repository
3. Click **"Continue"** and authenticate with GitHub if prompted
4. Select your GitHub repository from the list
5. Click **"Connect"**
6. Acknowledge the prompt about giving Cloud Build access to your repository

#### Step 5: Configure Trigger Settings

After connecting your repository:

- **Branch**: Enter `^main$` (this is a regex pattern that matches only the main branch)
  - Use `^develop$` for development branch
  - Use `.*` to trigger on any branch
- **Configuration**: Select **"Cloud Build configuration file (yaml or json)"**
- **Cloud Build configuration file location**: Enter `/cloudbuild.yaml`

#### Step 6: Add Substitution Variables

This is the **most important step** to keep sensitive values out of your repository.

1. Scroll down to **"Substitution variables"** section
2. Click **"Add variable"** for each of the following:

| Variable Name | Value | Description |
|---------------|-------|-------------|
| `_GCP_REGION` | `us-central1` | Region for your resources (change if needed) |
| `_ARTIFACT_REGISTRY_REPO` | `app-repo` | Name you used when creating Artifact Registry |
| `_IMAGE_NAME` | `demo-flask-app` | Name for your Docker image |
| `_CLOUD_RUN_SERVICE_NAME` | `py-bq-load` | Name for your Cloud Run service |
| `_PORT` | `8000` | Port your Flask app runs on |
| `_GCP_PROJECT_ID` | `your-project-id` | Your actual GCP project ID |
| `_BQ_DATASET` | `test_schema` | BigQuery dataset name you created |
| `_BQ_TABLE_NAME` | `us_states` | BigQuery table name you created |
| `_GCS_BUCKET_NAME` | `your-bucket-name` | Cloud Storage bucket name you created |
| `_GCS_CSV_FILE_PATH` | `us-states.csv` | Name of the CSV file in your bucket |

**Important Notes:**
- Variable names MUST start with `_` (underscore)
- Use your actual project ID for `_GCP_PROJECT_ID`
- Use the actual bucket name you created (e.g., `my-project-id-data-bucket`)
- All variable names must match exactly as shown in `cloudbuild.yaml`

#### Step 7: Review and Create

1. Review all your settings
2. Click **"Create"** at the bottom of the page

Your trigger is now configured! Every time you push to the `main` branch, Cloud Build will automatically:
1. Build your Docker image
2. Run tests
3. Deploy to Cloud Run

#### Verify Your Trigger

To verify your trigger was created successfully:

1. You should see your trigger listed on the **Triggers** page
2. Click on the trigger name to view its configuration
3. Verify all substitution variables are present in the **"Substitution variables"** section

## Environment Variables

The following substitution variables are used in `cloudbuild.yaml`:

| Variable | Description | Example |
|----------|-------------|---------|
| `_GCP_REGION` | GCP region for resources | `us-central1` |
| `_ARTIFACT_REGISTRY_REPO` | Artifact Registry repository | `app-repo` |
| `_IMAGE_NAME` | Docker image name | `demo-flask-app` |
| `_CLOUD_RUN_SERVICE_NAME` | Cloud Run service name | `py-bq-load` |
| `_PORT` | Application port | `8000` |
| `_GCP_PROJECT_ID` | GCP project ID | `your-project-id` |
| `_BQ_DATASET` | BigQuery dataset | `test_schema` |
| `_BQ_TABLE_NAME` | BigQuery table | `us_states` |
| `_GCS_BUCKET_NAME` | Cloud Storage bucket | `your-bucket-name` |
| `_GCS_CSV_FILE_PATH` | CSV file path in bucket | `us-states.csv` |

**Important:** These values must be set in your Cloud Build trigger configuration. They are intentionally left empty in `cloudbuild.yaml` to keep sensitive values out of the repository.

## Deployment

### Automatic Deployment

Once your trigger is configured, deployment is automatic:

1. Make changes to your code
2. Commit and push to the `main` branch:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

3. Cloud Build will automatically:
   - Build the Docker image
   - Push to Artifact Registry
   - Run tests
   - Deploy to Cloud Run

### Manual Deployment (Run Trigger Manually)

You can also trigger a build manually from the Console:

1. Go to [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers)
2. Find your trigger in the list
3. Click the **"RUN"** button on the right side
4. Select the branch to build (e.g., `main`)
5. Click **"Run trigger"**

### Monitor Build Progress

To view your build in real-time:

1. Go to [Cloud Build History](https://console.cloud.google.com/cloud-build/builds)
2. You'll see your build in the list with its status (queued, running, success, or failed)
3. Click on a build to view detailed logs and steps
4. Each step in your `cloudbuild.yaml` will show separately with its logs

### Access Your Application

After a successful deployment:

1. Go to [Cloud Run](https://console.cloud.google.com/run)
2. Click on your service (e.g., `py-bq-load`)
3. The service URL will be displayed at the top of the page
4. Click the URL to open your application

Alternatively, you can find the URL in the Cloud Build logs under the "Deploy to Cloud Run" step.

## Multiple Environments (Dev/Staging/Prod)

To support multiple environments (development, staging, production), create separate Cloud Build triggers for each environment using the Google Cloud Console:

1. **Create separate triggers** for each environment:
   - `py-bq-load-dev` (triggers on `develop` branch)
   - `py-bq-load-staging` (triggers on `staging` branch)
   - `py-bq-load-prod` (triggers on `main` branch)

2. **Use different substitution variables** for each environment:

**Development Trigger:**
- Branch pattern: `^develop$`
- `_CLOUD_RUN_SERVICE_NAME`: `py-bq-load-dev`
- `_BQ_DATASET`: `test_schema_dev`
- `_GCS_BUCKET_NAME`: `your-project-dev-data-bucket`

**Staging Trigger:**
- Branch pattern: `^staging$`
- `_CLOUD_RUN_SERVICE_NAME`: `py-bq-load-staging`
- `_BQ_DATASET`: `test_schema_staging`
- `_GCS_BUCKET_NAME`: `your-project-staging-data-bucket`

**Production Trigger:**
- Branch pattern: `^main$`
- `_CLOUD_RUN_SERVICE_NAME`: `py-bq-load-prod`
- `_BQ_DATASET`: `test_schema_prod`
- `_GCS_BUCKET_NAME`: `your-project-prod-data-bucket`

This approach allows you to safely test changes in development and staging before deploying to production.

## Troubleshooting

### Build Fails with Permission Errors

**Issue:** Cloud Build doesn't have permissions to deploy to Cloud Run or access BigQuery.

**Solution:** Grant necessary IAM roles to the Cloud Build service account:

1. Go to [IAM & Admin](https://console.cloud.google.com/iam-admin/iam)
2. Find the Cloud Build service account (looks like `[PROJECT_NUMBER]@cloudbuild.gserviceaccount.com`)
3. Click the **pencil icon** to edit permissions
4. Click **"Add Another Role"** and add these roles:
   - `Cloud Run Admin`
   - `Service Account User`
   - `Storage Admin`
   - `BigQuery Admin`
5. Click **"Save"**

Alternatively, you can run the setup commands from the [Grant Cloud Build Permissions](#grant-cloud-build-permissions) section.

### Substitution Variables Are Empty

**Issue:** Variables show as empty in build logs.

**Solution:** Verify substitution variables are configured in your trigger:

1. Go to [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers)
2. Click on your trigger name
3. Scroll down to the **"Substitution variables"** section
4. Verify all 10 variables are present with correct values
5. Ensure variable names match exactly (including the `_` prefix)

Common mistakes:
- Forgetting the `_` prefix (use `_GCP_REGION`, not `GCP_REGION`)
- Typos in variable names
- Empty values

### CSV File Not Found

**Issue:** Application can't find the CSV file in Cloud Storage.

**Solution:**

1. Verify the file exists in your bucket:
   - Go to [Cloud Storage](https://console.cloud.google.com/storage/browser)
   - Navigate to your bucket
   - Confirm `us-states.csv` is present

2. If missing, re-upload the file using the [Download Sample Data](#3-download-sample-data) instructions

3. Grant Cloud Run service permissions to read from the bucket:
   - Go to [IAM & Admin](https://console.cloud.google.com/iam-admin/iam)
   - Find the default compute service account: `[PROJECT_NUMBER]-compute@developer.gserviceaccount.com`
   - Add the `Storage Object Viewer` role

### BigQuery Dataset Not Found

**Issue:** BigQuery dataset or table doesn't exist.

**Solution:** Create the dataset and table using the Console:

1. Go to [BigQuery](https://console.cloud.google.com/bigquery)
2. Click your project name in the left sidebar
3. Click the three dots next to your project name
4. Select **"Create dataset"**
5. Fill in:
   - Dataset ID: `test_schema`
   - Location: Same as your `_GCP_REGION` (e.g., `us-central1`)
6. Click **"Create dataset"**
7. Click on the new dataset, then **"Create table"**
8. Configure the table:
   - Table: `us_states`
   - Schema: Add fields manually:
     - `state` (STRING)
     - `abbreviation` (STRING)
     - `capital` (STRING)
     - `population` (INTEGER)
     - `area_sq_mi` (INTEGER)
9. Click **"Create table"**

### Tests Fail During Build

**Issue:** pytest fails in the build pipeline.

**Solution:**

1. Check the build logs in [Cloud Build History](https://console.cloud.google.com/cloud-build/builds)
2. Look at the test step to see which tests failed
3. Fix the failing tests in your code
4. Test locally before pushing (if you have Docker installed)
5. Push the fixes to your repository

## Cleanup

To delete all created resources using the Console:

### Delete Cloud Run Service
1. Go to [Cloud Run](https://console.cloud.google.com/run)
2. Check the box next to your service (`py-bq-load`)
3. Click **"Delete"** at the top
4. Confirm deletion

### Delete Cloud Build Trigger
1. Go to [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers)
2. Find your trigger in the list
3. Click the three dots menu on the right
4. Select **"Delete"**
5. Confirm deletion

### Delete Artifact Registry Repository
1. Go to [Artifact Registry](https://console.cloud.google.com/artifacts)
2. Find your repository (`app-repo`)
3. Check the box next to it
4. Click **"Delete"** at the top
5. Confirm deletion

### Delete BigQuery Dataset
1. Go to [BigQuery](https://console.cloud.google.com/bigquery)
2. Find your dataset (`test_schema`) in the left sidebar
3. Click the three dots next to the dataset name
4. Select **"Delete"**
5. Type the dataset name to confirm
6. Click **"Delete"**

### Delete Cloud Storage Bucket
1. Go to [Cloud Storage](https://console.cloud.google.com/storage/browser)
2. Find your bucket in the list
3. Check the box next to it
4. Click **"Delete"** at the top
5. Type the bucket name to confirm
6. Click **"Delete"**

## Additional Resources

- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Cloud Storage Documentation](https://cloud.google.com/storage/docs)

## Security Best Practices

1. **Never commit sensitive values** (API keys, credentials) to the repository
2. **Use Secret Manager** for sensitive data
3. **Use least-privilege IAM** roles
4. **Enable VPC Service Controls** for production
5. **Use authenticated Cloud Run** services for production
6. **Regularly rotate credentials**
7. **Enable audit logging**

## License

MIT
