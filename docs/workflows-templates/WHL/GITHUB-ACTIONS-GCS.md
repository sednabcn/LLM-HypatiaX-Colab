# GitHub Actions + Google Cloud Storage Integration Guide

**Yes!** GitHub Actions can seamlessly integrate with Google Cloud Storage (GCS) and all GCP services.

## Table of Contents
1. [Authentication Methods](#authentication-methods)
2. [Quick Start Examples](#quick-start-examples)
3. [Complete Workflow Examples](#complete-workflow-examples)
4. [Advanced Patterns](#advanced-patterns)
5. [Security Best Practices](#security-best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Authentication Methods

### Method 1: Workload Identity Federation (Recommended - Most Secure)

**No service account keys stored in GitHub!** Uses OIDC tokens.

#### Step 1: Set Up in GCP

```bash
# 1. Create Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" \
  --project="YOUR_PROJECT_ID" \
  --location="global" \
  --display-name="GitHub Actions Pool"

# 2. Create Workload Identity Provider
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --project="YOUR_PROJECT_ID" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# 3. Get the Workload Identity Provider name
gcloud iam workload-identity-pools providers describe "github-provider" \
  --project="YOUR_PROJECT_ID" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --format="value(name)"
# Output: projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-provider

# 4. Create Service Account (if not exists)
gcloud iam service-accounts create github-actions-sa \
  --display-name="GitHub Actions Service Account"

# 5. Grant permissions to Service Account
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# 6. Allow GitHub to impersonate the Service Account
gcloud iam service-accounts add-iam-policy-binding \
  "github-actions-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --project="YOUR_PROJECT_ID" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME"
```

#### Step 2: GitHub Actions Workflow

```yaml
name: Upload to GCS with Workload Identity

on: [push]

permissions:
  contents: read
  id-token: write  # Required for OIDC

jobs:
  upload:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - id: auth
        name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: 'projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-provider'
          service_account: 'github-actions-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com'
      
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2
      
      - name: Upload to GCS
        run: |
          gsutil cp dist/*.whl gs://your-bucket/wheels/
          echo "✅ Files uploaded to GCS"
```

---

### Method 2: Service Account Key (Simpler, Less Secure)

**⚠️ Not recommended for production** - stores credentials in GitHub secrets.

#### Step 1: Create Service Account Key

```bash
# 1. Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions"

# 2. Grant storage permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# 3. Create and download key
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com

# 4. Encode key as base64
cat key.json | base64 > key.json.b64

# 5. Copy the base64 string and add to GitHub Secrets as GCP_SA_KEY
```

#### Step 2: Add to GitHub Secrets

Go to: **GitHub Repo → Settings → Secrets and variables → Actions → New repository secret**

- Name: `GCP_SA_KEY`
- Value: (paste base64 encoded key)

#### Step 3: GitHub Actions Workflow

```yaml
name: Upload to GCS with Service Account Key

on: [push]

jobs:
  upload:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Authenticate to Google Cloud
        env:
          GCP_SA_KEY: ${{ secrets.GCP_SA_KEY }}
        run: |
          echo "$GCP_SA_KEY" | base64 -d > /tmp/gcp-key.json
          gcloud auth activate-service-account --key-file=/tmp/gcp-key.json
      
      - name: Upload to GCS
        run: |
          gsutil cp dist/*.whl gs://your-bucket/wheels/
```

---

## Quick Start Examples

### Example 1: Upload Wheel Files to GCS

```yaml
name: Build and Upload Wheels

on:
  push:
    branches: [main]
  release:
    types: [published]

permissions:
  contents: read
  id-token: write

jobs:
  build-and-upload:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Build wheel
        run: |
          pip install build
          python -m build
      
      - name: Authenticate to GCP
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
      
      - name: Upload to GCS
        uses: google-github-actions/upload-cloud-storage@v2
        with:
          path: 'dist'
          destination: 'your-bucket/wheels/${{ github.sha }}'
          glob: '*.whl'
          parent: false
```

### Example 2: Download from GCS, Process, Upload Back

```yaml
name: Process Data from GCS

on:
  workflow_dispatch:

permissions:
  id-token: write
  contents: read

jobs:
  process:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
      
      - name: Download data from GCS
        run: |
          gsutil -m cp -r gs://input-bucket/data/ ./data/
      
      - name: Process data
        run: |
          python scripts/process_data.py
      
      - name: Upload results to GCS
        run: |
          gsutil -m cp -r ./results/ gs://output-bucket/results/
```

### Example 3: Sync Directory to GCS

```yaml
name: Sync Documentation to GCS

on:
  push:
    paths:
      - 'docs/**'

permissions:
  id-token: write
  contents: read

jobs:
  sync-docs:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
      
      - name: Sync to GCS
        run: |
          # -m for parallel, -r for recursive, -d for delete extras
          gsutil -m rsync -r -d docs/ gs://docs-bucket/
```

---

## Complete Workflow Examples

### HypatiaX Full CI/CD Pipeline

```yaml
name: HypatiaX CI/CD with GCS

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  release:
    types: [published]

permissions:
  contents: read
  id-token: write
  pull-requests: write

env:
  PYTHON_VERSION: '3.12'
  GCS_BUCKET: 'hypatia-artifacts'
  GCS_WHEELS_PATH: 'wheels'
  GCS_REPORTS_PATH: 'reports'
  GCS_MODELS_PATH: 'models'

jobs:
  # Job 1: Build and Test
  build-test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install build pytest pytest-cov
      
      - name: Run tests
        run: |
          pytest --cov=hypatia_x --cov-report=xml --cov-report=html
      
      - name: Build wheel
        run: |
          python -m build
      
      - name: Authenticate to GCP
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
      
      - name: Upload wheel to GCS
        run: |
          VERSION=$(python setup.py --version)
          COMMIT_SHA=$(git rev-parse --short HEAD)
          
          # Upload with version and commit info
          gsutil cp dist/*.whl gs://${{ env.GCS_BUCKET }}/${{ env.GCS_WHEELS_PATH }}/${VERSION}/
          gsutil cp dist/*.whl gs://${{ env.GCS_BUCKET }}/${{ env.GCS_WHEELS_PATH }}/latest/
          
          # Add metadata
          gsutil setmeta \
            -h "x-goog-meta-commit:${COMMIT_SHA}" \
            -h "x-goog-meta-branch:${GITHUB_REF_NAME}" \
            -h "x-goog-meta-build-date:$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
            gs://${{ env.GCS_BUCKET }}/${{ env.GCS_WHEELS_PATH }}/${VERSION}/*.whl
      
      - name: Upload test reports to GCS
        if: always()
        run: |
          gsutil -m cp -r htmlcov/ \
            gs://${{ env.GCS_BUCKET }}/${{ env.GCS_REPORTS_PATH }}/${GITHUB_SHA}/
          gsutil cp coverage.xml \
            gs://${{ env.GCS_BUCKET }}/${{ env.GCS_REPORTS_PATH }}/${GITHUB_SHA}/
      
      - name: Generate GCS URLs
        run: |
          echo "### 📦 Artifacts" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "Wheel: https://storage.googleapis.com/${{ env.GCS_BUCKET }}/${{ env.GCS_WHEELS_PATH }}/latest/" >> $GITHUB_STEP_SUMMARY
          echo "Reports: https://storage.googleapis.com/${{ env.GCS_BUCKET }}/${{ env.GCS_REPORTS_PATH }}/${GITHUB_SHA}/" >> $GITHUB_STEP_SUMMARY

  # Job 2: Train Model and Upload to GCS
  train-model:
    needs: build-test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
      
      - name: Download latest wheel from GCS
        run: |
          gsutil cp gs://${{ env.GCS_BUCKET }}/${{ env.GCS_WHEELS_PATH }}/latest/*.whl ./
          pip install *.whl
      
      - name: Download training data from GCS
        run: |
          gsutil -m cp -r gs://${{ env.GCS_BUCKET }}/datasets/ ./data/
      
      - name: Train model
        run: |
          python scripts/train_model.py \
            --data-dir ./data \
            --output-dir ./models
      
      - name: Upload trained model to GCS
        run: |
          TIMESTAMP=$(date +%Y%m%d_%H%M%S)
          
          # Upload with timestamp
          gsutil -m cp -r ./models/ \
            gs://${{ env.GCS_BUCKET }}/${{ env.GCS_MODELS_PATH }}/${TIMESTAMP}/
          
          # Also update 'latest'
          gsutil -m cp -r ./models/ \
            gs://${{ env.GCS_BUCKET }}/${{ env.GCS_MODELS_PATH }}/latest/
          
          # Add metadata
          gsutil setmeta \
            -h "x-goog-meta-commit:${GITHUB_SHA}" \
            -h "x-goog-meta-training-date:${TIMESTAMP}" \
            gs://${{ env.GCS_BUCKET }}/${{ env.GCS_MODELS_PATH }}/${TIMESTAMP}/**

  # Job 3: Deploy to Cloud Run
  deploy:
    needs: train-model
    runs-on: ubuntu-latest
    if: github.event_name == 'release'
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
      
      - name: Deploy to Cloud Run
        uses: google-github-actions/deploy-cloudrun@v2
        with:
          service: hypatia-x
          region: us-central1
          source: .
          env_vars: |
            GCS_BUCKET=${{ env.GCS_BUCKET }}
            GCS_MODELS_PATH=${{ env.GCS_MODELS_PATH }}/latest
```

---

## Advanced Patterns

### Pattern 1: Conditional Upload Based on Tests

```yaml
jobs:
  test-and-upload:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Run tests
        id: tests
        run: |
          pytest --junitxml=results.xml
          echo "status=$?" >> $GITHUB_OUTPUT
      
      - uses: google-github-actions/auth@v2
        if: steps.tests.outputs.status == '0'
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
      
      - name: Upload only if tests pass
        if: steps.tests.outputs.status == '0'
        run: |
          gsutil cp dist/*.whl gs://your-bucket/approved/
```

### Pattern 2: Multi-Environment Deployment

```yaml
jobs:
  deploy-multi-env:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [dev, staging, prod]
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets[format('SA_{0}', matrix.environment)] }}
      
      - name: Upload to environment-specific bucket
        run: |
          gsutil cp dist/*.whl gs://hypatia-${{ matrix.environment }}/wheels/
```

### Pattern 3: Versioned Artifacts with Lifecycle

```yaml
- name: Upload versioned artifacts
  run: |
    VERSION=$(python setup.py --version)
    DATE=$(date +%Y-%m-%d)
    
    # Upload to versioned path
    gsutil cp dist/*.whl gs://bucket/wheels/${VERSION}/
    
    # Set lifecycle rule (auto-delete after 90 days)
    gsutil lifecycle set lifecycle.json gs://bucket
```

**lifecycle.json:**
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 90,
          "matchesPrefix": ["wheels/"]
        }
      }
    ]
  }
}
```

### Pattern 4: Parallel Uploads

```yaml
- name: Parallel upload of multiple directories
  run: |
    # -m enables parallel uploads
    gsutil -m cp -r \
      dist/ gs://bucket/dist/ \
      docs/ gs://bucket/docs/ \
      models/ gs://bucket/models/
```

### Pattern 5: Cache GCS Data Between Runs

```yaml
jobs:
  use-cached-data:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Cache GCS data
        uses: actions/cache@v4
        id: cache
        with:
          path: data/
          key: gcs-data-${{ hashFiles('data-version.txt') }}
      
      - uses: google-github-actions/auth@v2
        if: steps.cache.outputs.cache-hit != 'true'
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
      
      - name: Download from GCS if not cached
        if: steps.cache.outputs.cache-hit != 'true'
        run: |
          gsutil -m cp -r gs://bucket/data/ ./data/
```

---

## Security Best Practices

### 1. Use Workload Identity Federation (No Keys!)

```yaml
# ✅ GOOD - No credentials stored
permissions:
  id-token: write

- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
    service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
```

```yaml
# ❌ BAD - Credentials in GitHub Secrets
env:
  GCP_SA_KEY: ${{ secrets.GCP_SA_KEY }}
```

### 2. Principle of Least Privilege

```bash
# Grant only necessary permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:sa@project.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin" \
  --condition="resource.name.startsWith('projects/_/buckets/specific-bucket')"
```

### 3. Repository-Specific Access

```bash
# Only allow specific GitHub repo
--member="principalSet://iam.googleapis.com/.../attribute.repository/USERNAME/REPO_NAME"

# Not this (allows all repos in org):
--member="principalSet://iam.googleapis.com/.../attribute.repository_owner/ORG_NAME"
```

### 4. Audit Logging

```bash
# Enable audit logs for GCS
gcloud logging read "resource.type=gcs_bucket" --limit 50
```

### 5. Use Private Buckets

```bash
# Make bucket private
gsutil iam ch -d allUsers:objectViewer gs://your-bucket

# Grant access only to service account
gsutil iam ch \
  serviceAccount:github-actions-sa@project.iam.gserviceaccount.com:objectAdmin \
  gs://your-bucket
```

### 6. Signed URLs for Temporary Access

```yaml
- name: Generate signed URL
  run: |
    gsutil signurl -d 1h \
      /path/to/key.json \
      gs://bucket/file.whl > url.txt
```

---

## Troubleshooting

### Error: "403 Forbidden"

**Cause**: Insufficient permissions

**Solution**:
```bash
# Check service account permissions
gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:YOUR_SA"

# Add missing role
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:YOUR_SA" \
  --role="roles/storage.objectAdmin"
```

### Error: "Workload Identity Pool does not exist"

**Cause**: WIF not properly set up

**Solution**:
```bash
# Verify pool exists
gcloud iam workload-identity-pools list --location=global

# Verify provider exists
gcloud iam workload-identity-pools providers list \
  --location=global \
  --workload-identity-pool=POOL_NAME
```

### Error: "gsutil: command not found"

**Cause**: gcloud SDK not installed

**Solution**:
```yaml
- uses: google-github-actions/setup-gcloud@v2
  with:
    install_components: 'gsutil'
```

### Error: "Token exchange failed"

**Cause**: Missing `id-token: write` permission

**Solution**:
```yaml
permissions:
  contents: read
  id-token: write  # ← Add this!
```

### Debugging Commands

```yaml
- name: Debug GCP auth
  run: |
    gcloud auth list
    gcloud config list
    gsutil ls gs://your-bucket/ || echo "Bucket not accessible"
```

---

## Comparison: GitHub Actions vs Direct GCP

| Feature | GitHub Actions → GCS | Direct GCP (Cloud Build) |
|---------|---------------------|-------------------------|
| **Setup** | Requires WIF setup | Native integration |
| **Cost** | GitHub Actions minutes | Cloud Build minutes |
| **Flexibility** | More ecosystem integrations | Better GCP integration |
| **Security** | WIF (keyless) recommended | IAM built-in |
| **Use Case** | Multi-cloud, GitHub-centric | GCP-only workflows |

---

## Complete Example: HypatiaX Wheel Management

```yaml
name: HypatiaX Wheel Management

on:
  push:
    branches: [main]
    tags: ['v*']
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to build'
        required: false

permissions:
  contents: read
  id-token: write

env:
  BUCKET: hypatia-wheels
  PROJECT_ID: hypatia-x-project

jobs:
  build-upload:
    runs-on: ubuntu-latest
    
    outputs:
      wheel-url: ${{ steps.upload.outputs.wheel-url }}
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Build wheel
        run: |
          pip install build
          python -m build
          
          # Get wheel filename
          WHEEL=$(ls dist/*.whl)
          echo "WHEEL_FILE=${WHEEL}" >> $GITHUB_ENV
      
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
      
      - name: Upload to GCS
        id: upload
        run: |
          VERSION=$(python setup.py --version)
          
          # Upload wheel
          gsutil cp ${WHEEL_FILE} gs://${BUCKET}/wheels/${VERSION}/
          gsutil cp ${WHEEL_FILE} gs://${BUCKET}/wheels/latest/
          
          # Make publicly readable (optional)
          gsutil acl ch -u AllUsers:R gs://${BUCKET}/wheels/${VERSION}/*.whl
          
          # Output URL
          URL="https://storage.googleapis.com/${BUCKET}/wheels/${VERSION}/$(basename ${WHEEL_FILE})"
          echo "wheel-url=${URL}" >> $GITHUB_OUTPUT
          echo "### 📦 Wheel Published" >> $GITHUB_STEP_SUMMARY
          echo "URL: ${URL}" >> $GITHUB_STEP_SUMMARY
  
  test-install:
    needs: build-upload
    runs-on: ubuntu-latest
    
    steps:
      - name: Test wheel installation
        run: |
          pip install ${{ needs.build-upload.outputs.wheel-url }}
          python -c "import hypatia_x; print(hypatia_x.__version__)"
```

---

## Conclusion

✅ **GitHub Actions + GCS works perfectly**  
✅ **Workload Identity Federation = Most secure**  
✅ **Native actions available** (`google-github-actions/*`)  
✅ **Full gsutil/gcloud support**  
✅ **Perfect for ML pipelines** (wheels, models, datasets)  

**Recommended for HypatiaX**: Use WIF + upload wheels/models to GCS for deployment to Cloud Run, Vertex AI, or other GCP services.

Absolutely! GitHub Actions has excellent integration with Google Cloud Storage. Here are the key points:
Two Main Methods:
1. Workload Identity Federation (Recommended) 🔒

No credentials stored in GitHub!
Uses OIDC tokens for authentication
Most secure option
Requires initial GCP setup

2. Service Account Keys

Store key in GitHub Secrets
Simpler setup
Less secure (not recommended for production)

Quick Example:
yamlpermissions:
  id-token: write  # Required for WIF

steps:
  - uses: google-github-actions/auth@v2
    with:
      workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
      service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
  
  - name: Upload to GCS
    run: |
      gsutil cp dist/*.whl gs://your-bucket/wheels/
Perfect for HypatiaX Use Cases:
✅ Upload .whl files after building
✅ Store trained models
✅ Download datasets for training
✅ Sync documentation
✅ Archive test reports
✅ Deploy to Cloud Run/Vertex AI
I've created a comprehensive guide with:

Complete setup instructions for both methods
Full CI/CD pipeline example for HypatiaX
Security best practices
Advanced patterns (parallel uploads, caching, versioning)
Troubleshooting tips

The guide includes a complete example showing how to build wheels, upload to GCS, train models, and deploy to Cloud Run—all from GitHub Actions!