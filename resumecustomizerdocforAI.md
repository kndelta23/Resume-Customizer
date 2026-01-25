# Resume Customizer - Technical Documentation

## Overview
The **Resume Customizer** is a Google Cloud Function designed to tailor a master resume and cover letter for a specific job posting. It leverages Google's Gemini Pro model to rewrite resume content and generate a targeted cover letter.

## Architecture
- **Runtime**: Python 3.10 (Cloud Functions Gen 2)
- **AI Model**: Google Gemini (via `google.generativeai` / `google.genai`)
- **Storage**: Google Cloud Storage (GCS)
    - Input: Reads master resume PDF from the bucket.
    - Output: Saves customized Resume and Cover Letter as `.docx` files.
- **Trigger**: HTTP (Public/Unauthenticated for this implementation)

## Key Components

### 1. `main.py`
The core logic resides here.
- **Input Parsing**: Accepts JSON with `job_url` or `job_description`.
- **Job Scraping**: If `job_url` is provided, fetches and cleans the text from the webpage.
- **PDF Extraction**: Downloads the master resume (`John Thomas Delta -- Resume 2025.pdf`) from GCS and extracts text using `pypdf`.
- **AI Generation**: content is generated using a structured prompt.
    - **Prompt Features**:
        - Role/Company extraction.
        - Relocation logic (checks for onsite requirements).
        - Consolidated skills list.
        - **Signature Enforcement**: Distinct instruction to sign as "Sincerely, Tommy Delta".
- **Signature Fallback**: A runtime check ensures the cover letter ends with the required signature, appending it if missing.
- **Document Generation**: Uses `python-docx` to create formatted Resume and Cover Letter files (Times New Roman, 12pt).

### 2. `deploy.sh`
Shell script to deploy the function to GCP.
- Region: `us-central1`
- Function Name: `resume-customizer`
- Environment Variables: Sets `GEMINI_API_KEY`.

### 3. Testing (`tests/test_customizer.py`)
Unit tests verify the business logic.
- **Signature Test**: Mocks a Gemini response missing the signature to verify the runtime fallback logic works correctly.

## Usage

### Endpoint
`POST https://us-central1-[PROJECT-ID].cloudfunctions.net/resume-customizer`

### Payload
```json
{
  "job_url": "https://example.com/job-posting"
}
```
*Or directly provided description:*
```json
{
  "job_description": "We are looking for..."
}
```

### Outputs
Returns a JSON object with GCS URIs to the generated files:
```json
{
  "result": "Success",
  "resume_docx": "gs://bucket/Company_Job_Resume_Date.docx",
  "cover_letter_docx": "gs://bucket/Company_Job_CoverLetter_Date.docx",
  ...
}
```

## Setup & Deployment
1. Ensure `gcloud` is installed and authenticated.
2. Set `PROJECT_ID` in `deploy.sh` if needed.
3. Run:
   ```bash
   ./deploy.sh
   ```

## Development
To run tests:
```bash
python3 -m unittest tests/test_customizer.py
```
