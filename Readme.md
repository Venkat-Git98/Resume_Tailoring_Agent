# Automated Resume Tailoring Agent: Overview and Setup

## 🚀 Project Purpose

The **Automated Resume Tailoring Agent** is a sophisticated Python-based application designed to streamline and automate the process of customizing a candidate's resume and generating a cover letter for specific job applications. It leverages Large Language Models (LLMs), specifically Google's Gemini, to analyze job descriptions, parse existing resumes, tailor resume sections (Summary, Work Experience, Technical Skills, Projects), generate a targeted cover letter, and provide a critique of the tailored resume. The system also includes a job scraping component to gather job postings from platforms like LinkedIn and Jobright.ai, further automating the job application pipeline.

**Key Goals:**

* **Automate Customization:** Reduce the manual effort required to tailor resumes and cover letters for each job application.
* **Enhance Relevance:** Improve the alignment of application materials with job requirements and ATS (Applicant Tracking System) keywords.
* **Improve Efficiency:** Speed up the job application process by automating repetitive tasks.
* **Provide Feedback:** Offer critiques on tailored resumes to help improve their effectiveness.
* **Streamline Job Search:** Automatically scrape and filter relevant job postings.

##  архитектура High-Level Architecture

The system is designed with a modular architecture, comprising several interconnected components:

1.  **Configuration Core (`config.py`):** Centralized management of all project paths, API keys (placeholders), GCS settings, email configurations, logging parameters, scraper settings, and predefined resume content.
2.  **Main Orchestration (`main.py`):** The primary entry point that parses command-line arguments and orchestrates the resume tailoring pipeline. It initializes and calls the `OrchestratorAgent`.
3.  **Agent-Based System (`agents/`):**
    * **OrchestratorAgent (`orchestrator.py`):** Manages the end-to-end tailoring process by coordinating other specialized agents.
    * **JDAnalysisAgent (`jd_analysis.py`):** Analyzes job descriptions to extract titles, requirements, and ATS keywords.
    * **ResumeParserAgent (`resume_parser.py`):** Parses the candidate's base resume (PDF).
    * **TailoringAgent (`tailoring.py`):** Rewrites individual resume sections using LLM prompts for optimal alignment with the job description.
    * **CoverLetterAgent (`cover_letter_agent.py`):** Generates a tailored cover letter based on the job description and tailored resume.
    * **ResumeJudgeAgent (`resume_judge_agent.py`):** Evaluates the tailored resume against the job description and provides a critique (ATS score, recruiter impression).
4.  **LLM Interaction (`utils/llm_gemini.py`):** A client for interacting with the Gemini LLM, including functions to generate specific prompts for different tasks.
5.  **Document Generation (`src/`):**
    * **DOCX & PDF Generation (`src/docx_to_pdf_generator.py`):** Creates styled DOCX documents for resumes and cover letters, then converts them to PDF using the Google Drive API.
    * **(Alternative) PDF Generation (`src/pdf_generator.py`, `src/data_parser_for_pdf.py`):** An xhtml2pdf-based PDF generation pipeline (appears to be an alternative or older method).
6.  **Job Scraping (`scrape.py`):** A standalone, schedulable script that scrapes job postings from LinkedIn and Jobright.ai, filters them, and can initiate the tailoring pipeline for relevant jobs.
7.  **Utilities (`utils/`):** Modules for file reading (`file_utils.py`), NLP tasks like section splitting (`nlp_utils.py`), email sending (`email_sender.py` via Brevo), and Google Cloud Storage operations (`gcs_utils.py`).
8.  **Data Management:**
    * **Input Data (`data/`, `master_profile.txt`, `Shanmugam_AI_2025_4_YOE.pdf`):** Base resume, master profile, and example job descriptions.
    * **Scraped Data (`data/scraped_jobs/`):** Stores JSON files of all scraped jobs and relevant new jobs.
    * **Output Data (`data/tailored_documents/`, `tailored_resume.json`):** Stores generated PDFs and intermediate JSON outputs.
9.  **Logging (`logs/`):** Contains application and scraper logs.

## 💻 Key Technologies Used

* **Programming Language:** Python 3.10+
* **LLM:** Google Gemini (via API)
* **Web Scraping:** Selenium, BeautifulSoup, Requests
* **PDF Processing:** PyMuPDF (Fitz), python-docx, Google Drive API (for DOCX to PDF conversion), xhtml2pdf (alternative)
* **Data Handling & Modeling:** Pydantic, JSON
* **Environment Management:** python-dotenv
* **Scheduling:** `schedule` library
* **Email:** Brevo (formerly Sendinblue) SMTP
* **Cloud Storage:** Google Cloud Storage (GCS)
* **Version Control:** Git
* **CI/CD (implied by some configurations):** Chromedriver installation script suggests potential for automated environments.

## 📂 Folder Structure Overview

```
Automated_Resume_Tailoring_Agent/
├── agents/                    # Core logic for different processing stages
│   ├── __init__.py
│   ├── cover_letter_agent.py
│   ├── jd_analysis.py
│   ├── orchestrator.py
│   ├── resume_judge_agent.py
│   ├── resume_parser.py
│   └── tailoring.py
├── config.py                  # Central configuration file
├── data/                        # Data storage
│   ├── scraped_jobs/          # JSON files for scraped job data
│   │   ├── consolidated_all_jobs.json
│   │   └── consolidated_relevant_new_jobs.json
│   └── tailored_documents/      # Output directory for generated PDFs
├── install_chromedriver.sh    # Script for installing Chromedriver (for scraping)
├── logs/                        # Log files
│   └── combined_job_scraper.log
├── main.py                      # Main entry point for resume tailoring
├── master_profile.txt           # Candidate's master resume/profile text
├── models.py                    # Pydantic data models
├── requirements.txt             # Python package dependencies
├── scrape.py                    # Job scraping script
├── Scrapping/                   # Supporting files/profile for scraping
│   ├── __init__.py
│   └── chrome_jobright_profile/ # Chrome profile for Jobright scraper
├── Shanmugam_AI_2025_4_YOE.pdf  # Example base resume
├── src/                         # Source code for specific utilities like PDF generation
│   ├── data_parser_for_pdf.py
│   ├── docx_to_pdf_generator.py
│   └── pdf_generator.py
├── tailored_resume.json       # Example JSON output of a tailored resume
└── utils/                       # Utility modules
    ├── __init__.py
    ├── email_sender.py
    ├── file_utils.py
    ├── gcs_utils.py
    ├── llm_gemini.py
    └── nlp_utils.py
```

## ⚙️ Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd Automated_Resume_Tailoring_Agent
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    Install the required Python packages listed in `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
    The `requirements.txt` file includes [setuptools, wheel, google-cloud-aiplatform, PyMuPDF, pydantic, vertexai, python-docx, selenium, webdriver-manager, sib-api-v3-sdk, requests, beautifulsoup4, schedule, python-dotenv, google-api-python-client, google-auth-httplib2, google-auth-oauthlib].

4.  **Chromedriver for Scraping (if using `scrape.py`):**
    The `scrape.py` script uses Selenium for interacting with web pages (specifically Jobright.ai). This requires Chromedriver.
    * The `install_chromedriver.sh` script provides a way to download and install a specific version of Chromedriver for Linux environments. You may need to adapt this script or manually install Chromedriver appropriate for your operating system and Chrome/Chromium version.
    * **Important:** The `install_chromedriver.sh` script requires manual updating of the `CHROMEDRIVER_URL`. Refer to the comments in the script.
    * Alternatively, `webdriver-manager` (listed in `requirements.txt`) can often handle Chromedriver installation automatically if the system-installed Chromedriver isn't found or is incompatible. The `scrape.py` script attempts to use `ChromeDriverManager().install()` as a fallback if a system-installed Chromedriver isn't explicitly specified or found.

5.  **Environment Variables & Configuration (`config.py` and `.env` file):**
    This project relies heavily on `config.py` and an associated `.env` file for sensitive information and operational parameters.
    * Create a `.env` file in the project root directory (same level as `config.py`).
    * Populate the `.env` file with necessary API keys and credentials. Based on `config.py`, these include:
        * `GOOGLE_API_KEY`: For Gemini LLM access.
        * `GOOGLE_CREDENTIALS_JSON_CONTENT`: JSON string content of your Google Cloud service account key (used for GCS and Google Drive API for PDF generation).
        * `GCS_BUCKET_NAME`: Your Google Cloud Storage bucket name (optional, defaults to "tailoring-agent").
        * `JOBRIGHT_USERNAME`: Username for Jobright.ai (for scraping).
        * `JOBRIGHT_PASSWORD`: Password for Jobright.ai.
        * `BREVO_SMTP_LOGIN`: Your Brevo (Sendinblue) SMTP login email.
        * `BREVO_SMTP_KEY`: Your Brevo SMTP key (this is the environment variable name defined by `BREVO_SMTP_KEY_ENV_VAR_NAME` in `config.py`, which defaults to "BREVO_SMTP_KEY").
        * `BREVO_SENDER_DISPLAY_EMAIL`: The verified sender email address in your Brevo account.
        * `APP_EMAIL_RECIPIENT`: The email address to send tailored documents and critiques to.
        * `LOG_LEVEL` (optional, defaults to INFO).
        * `SCRAPE_INTERVAL_MINUTES` (optional, defaults to 60 for `scrape.py`).
    * Review `config.py` for other paths and default settings. Many paths are derived from `PROJECT_ROOT` (the directory where `config.py` resides). Ensure your data files (base resume, master profile, job descriptions) are placed according to these configurations or provide paths via command-line arguments when running `main.py`.

6.  **Google Cloud Setup (for PDF generation via Google Drive and GCS uploads):**
    * Ensure you have a Google Cloud Project.
    * Enable the Google Drive API and Google Cloud Storage API.
    * Create a service account with appropriate permissions for Google Drive (to create, modify, and delete files) and Google Cloud Storage (to write to your bucket).
    * Download the JSON key for this service account. The *content* of this JSON file should be set as the value for the `GOOGLE_CREDENTIALS_JSON_CONTENT` environment variable in your `.env` file.
    * Ensure the `GCS_BUCKET_NAME` environment variable is set to your desired GCS bucket.

## 🛠️ Configuration (`config.py`)

The `config.py` file is central to the application's operation. It defines:

* **Project Paths:** `PROJECT_ROOT`, `DATA_DIR`, `TEMPLATES_DIR`, `SRC_DIR`, `LOGS_DIR`, `DEFAULT_PDF_OUTPUT_DIR`, `SCRAPED_JOBS_DATA_DIR`.
* **Default File Names/Paths:** For base resume, job description, master profile, and tailored outputs.
* **Google Cloud:** `SERVICE_ACCOUNT_JSON_CONTENT` (via environment variable), `GCS_BUCKET_NAME`.
* **Predefined Resume Info:** `PREDEFINED_CONTACT_INFO`, `PREDEFINED_EDUCATION_INFO` used for generating the DOCX/PDF resume.
* **PDF Filename Parameters:** Defaults for target company, YOE, and keyword in filenames.
* **LLM Configuration:** `GEMINI_MODEL_FOR_TAILORING`.
* **Logging Configuration:** `LOG_LEVEL`, `LOG_FORMAT`, log file paths.
* **Scraper Configuration:**
    * Log file path (`SCRAPER_LOG_FILE`).
    * Output paths for scraped jobs (`SCRAPER_CONSOLIDATED_ALL_JOBS_FILE`, `SCRAPER_CONSOLIDATED_RELEVANT_NEW_JOBS_FILE`).
    * Scraping schedule interval (`SCRAPER_SCHEDULE_INTERVAL_MINUTES`).
    * Keywords for identifying relevant jobs (`SCRAPER_RELEVANT_JOB_KEYWORDS`).
    * Jobright profile directory and credentials (can be overridden by environment variables).
* **Email Configuration (Brevo):** SMTP server, port, login, key (via environment variable), sender display email, and application recipient email.
* **Directory Creation:** Ensures necessary data and log directories are created on startup.

It's crucial to set up the `.env` file correctly as `config.py` loads values from it. 

## 📚 Detailed Documentation

For a deeper dive into specific aspects of the project, please refer to the following documents:

*   **[Core Resume Tailoring Pipeline (`Core_Resume_Tailoring_Pipeline.md`)](./Core_Resume_Tailoring_Pipeline.md):** This document details the core resume tailoring pipeline, from analyzing job descriptions to generating tailored application materials and critiquing the resume.
*   **[Job Scraping, Utilities, and Deployment (`Job_Scraping_Utilities_Deployment.md`)](./Job_Scraping_Utilities_Deployment.md):** This document covers the job scraping capabilities, utility modules, PDF generation, and other supporting aspects of the Automated Resume Tailoring Agent. 