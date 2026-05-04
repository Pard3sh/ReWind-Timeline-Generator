# Running ReWind Sentiment Batch Job with Docker

## Local Docker Testing

### Build the Docker image

```bash
docker build -t rewind-sentiment-batch:latest .
```

### Run the container locally

With your `.env` file:

```bash
docker run --rm --env-file .env rewind-sentiment-batch:latest
```

The container will:

1. Install dependencies
2. Load your `.env` variables
3. Run the batch job
4. Exit automatically when complete

### View logs

```bash
docker run --rm --env-file .env rewind-sentiment-batch:latest 2>&1 | tee batch-job.log
```

---

## GitHub Actions Automation

A GitHub Actions workflow has been created in `.github/workflows/sentiment-batch-job.yml`

### Setup

1. **Add secrets to your GitHub repository**:
   - Go to: `Settings` → `Secrets and variables` → `Actions`
   - Add these secrets:
     - `GCNL_API_KEY`: Your Google Cloud NLP API key
     - `FIREBASE_PROJECT_ID`: `final-project-494621`
     - `FIREBASE_SERVICE_ACCOUNT_KEY`: The entire JSON content from your service account key file

2. **For `FIREBASE_SERVICE_ACCOUNT_KEY`**:
   - Open your JSON file
   - Copy the **entire JSON content** (not the path)
   - Paste it as the secret value in GitHub

### Scheduling

The workflow runs:

- **Automatically**: Daily at 2 AM UTC (edit the cron expression to change)
- **Manually**: Trigger from GitHub UI under `Actions` → `ReWind Sentiment Batch Job` → `Run workflow`

### Monitor runs

1. Go to your GitHub repo
2. Click `Actions` tab
3. Select `ReWind Sentiment Batch Job`
4. View logs for each run

---

## Cron Schedule Examples (AI generated)

Change the `cron` value in `.github/workflows/sentiment-batch-job.yml`:

```yaml
- cron: "0 2 * * *" # Daily at 2 AM UTC
- cron: "0 */6 * * *" # Every 6 hours
- cron: "0 9 * * MON" # Mondays at 9 AM UTC
- cron: "0 2 * * 1-5" # Weekdays at 2 AM UTC
```
