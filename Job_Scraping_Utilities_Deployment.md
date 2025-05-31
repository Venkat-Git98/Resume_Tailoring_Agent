⬅️ **[Back to Main README (`Readme.md`)](./Readme.md)**

# Automated Resume Tailoring Agent: Job Scraping, Utilities, and Deployment

This document covers the job scraping capabilities, utility modules, PDF generation, and other supporting aspects of the Automated Resume Tailoring Agent.

## 🎯 Job Scraping Sub-system (`scrape.py`)

The `scrape.py` script is a powerful, standalone component designed to automate the collection and initial processing of job postings. It can be run independently and scheduled for regular execution.

**Core Functionality (`run_all_scrapers_and_process`):**

1.  **Initialization & Configuration:**
    * Loads configurations from `config.py` (scraper URLs, keywords, email settings, GCS settings, paths to base resume/master profile).
    * Initializes logging to `logs/combined_job_scraper.log` and stdout.
    * Initializes the tailoring system (`llm_client_global`, `orchestrator_agent_global`) if all necessary modules are loaded.
    * Initializes the GCS client if `gcp_utils` are loaded and configured.
2.  **Load Existing Data:**
    * Loads previously scraped jobs from `data/scraped_jobs/consolidated_all_jobs.json` to avoid re-processing.
    * Creates a set of `seen_job_ids_globally`.
3.  **Iterate Through Scraper Configurations (`SCRAPER_CONFIGS` in `config.py`):**
    * **LinkedIn Scraper (`process_linkedin_job_search`):**
        * Uses `requests` and `BeautifulSoup` to fetch and parse LinkedIn job search result pages.
        * Extracts job summaries (title, company, URL, job ID).
        * For each new job, fetches the individual job page to get the detailed description.
        * Handles delays between requests to avoid being blocked.
    * **Jobright.ai Scraper (`scrape_jobright_platform`):**
        * Uses `selenium` with `webdriver-manager` (primarily configured for Chromedriver via system path or auto-download) to interact with Jobright.ai.
        * Handles login to Jobright.ai using credentials from `config.py` or environment variables.
        * Navigates to the recommended jobs page.
        * Scrolls to load a target number of job cards.
        * For each job card, it clicks the card to open the detail pane and extracts detailed information (title, company, full description by parsing sections like "Responsibilities", "Qualification", "Benefits").
        * Constructs a unique job ID.
    * **Job ID Parsing (`parse_job_id_for_platform`):** A utility function to extract or construct a unique job ID from various attributes or URL patterns for different platforms.
4.  **Data Consolidation & Deduplication:**
    * Merges newly scraped jobs with the existing list from `consolidated_all_jobs.json`.
    * Deduplicates based on job ID.
    * Saves the updated list back to `consolidated_all_jobs.json`.
5.  **Job Filtering:**
    * Iterates through `newly_detailed_jobs_this_cycle`.
    * Applies a series of filters defined in `config.py`:
        * Domain exclusion (`EXCLUDE_JOB_SOURCES_DOMAINS`).
        * Job title seniority exclusion (`EXCLUDE_JOB_TITLE_SENIORITY`).
        * Specific logic for "Software Engineer" titles (requires AI/ML modifiers: `SOFTWARE_ENGINEER_TERMS`, `AI_ML_DATA_MODIFIERS_FOR_SE_TITLE`).
        * General undesired field exclusion (`EXCLUDE_JOB_TITLE_FIELDS`).
        * Relevance keyword matching against title and description (`RELEVANT_JOB_KEYWORDS`).
        * Deduplication within the current cycle based on a combined key of company name and job title.
    * Saves the filtered list of relevant new jobs (with descriptions) to `data/scraped_jobs/consolidated_relevant_new_jobs.json`.
6.  **Automated Tailoring & Application Pipeline (if relevant jobs found & tailoring system initialized):**
    * For each relevant new job:
        * Calls `run_tailoring_pipeline_for_job()`:
            * **Master Profile:** Loads `master_profile.txt` if configured.
            * **Base Resume:** Uses `DEFAULT_BASE_RESUME_PDF_PATH` for initial parsing by the orchestrator.
            * **Orchestration:** Invokes `orchestrator_agent_global.run()` with the job details (description, company name), base resume path, master profile, and predefined contact info. This generates the tailored resume, cover letter, and critique.
            * **PDF Generation:** If successful and `PDF_GENERATOR_SERVICE_ACCOUNT_CONFIGURED` is true (meaning Google Drive API can be used), it calls:
                * `generate_styled_resume_pdf()`
                * `generate_cover_letter_pdf()`
                These functions (from `src/docx_to_pdf_generator.py`) create DOCX files locally, upload them to Google Drive, convert them to Google Docs, export them as PDFs, download the PDFs, and then clean up the Drive files. The PDFs are saved to the directory specified by `DEFAULT_PDF_OUTPUT_DIR` in `config.py`.
            * **GCS Upload:** If `GCP_UTILS_LOADED`, GCS client is available, and `GCS_BUCKET_NAME` is set:
                * Uploads the generated resume PDF and cover letter PDF to Google Cloud Storage. Files are organized by company and date/time.
            * **Email Notification:**
                * Uses `utils.email_sender.send_job_application_email()` to send an email containing the job details, critique, and attaches the generated PDF resume and cover letter.
                * Email settings (recipient, sender, Brevo SMTP credentials) are sourced from `config.py`.
            * **Local File Cleanup:** Deletes the locally generated PDF resume and cover letter after successful emailing (and GCS upload if configured).
7.  **Scheduling:**
    * The `scrape.py` script uses the `schedule` library.
    * `run_all_scrapers_and_process()` is run once on startup.
    * It's then scheduled to run every `SCHEDULE_INTERVAL_MINUTES` (from `config.py`, defaults to 60).
    * A `delete_state_files_task()` is scheduled daily at 00:05 to delete `consolidated_all_jobs.json` and `consolidated_relevant_new_jobs.json`, effectively resetting the "seen" jobs daily to allow for re-scraping of jobs that might still be open.
    * A `DAILY_RUN_COUNTER` is maintained to track runs within a day, used in email subject lines.

**Chromedriver Installation (`install_chromedriver.sh`):**
This script is provided to manually install a specific version of Chromedriver on a Linux system. It downloads the specified Chromedriver zip, unzips it, moves the executable to `/usr/local/bin/`, and sets permissions. It includes a placeholder for `CHROMEDRIVER_URL` that **must be updated by the user**. This is crucial for the Selenium-based Jobright scraper if `webdriver-manager` fails or a specific version is needed.

## 📄 PDF Generation

The primary PDF generation mechanism is through `src/docx_to_pdf_generator.py`.

**`src/docx_to_pdf_generator.py`:**

1.  **Google Drive API Integration:**
    * `get_drive_service()`: Authenticates with Google Drive API using service account JSON content (from `config.SERVICE_ACCOUNT_JSON_CONTENT` environment variable).
    * `upload_and_convert_to_google_doc()`: Uploads a local DOCX file to Google Drive, then copies it to create a native Google Doc (which is better for PDF conversion fidelity).
    * `export_pdf_from_drive()`: Exports the native Google Doc as a PDF and saves it locally.
    * `delete_file_from_drive()`: Cleans up the uploaded DOCX and converted Google Doc from Drive.
2.  **DOCX Creation (using `python-docx`):**
    * Helper functions like `add_hyperlink`, `add_runs_with_markdown_bold`, `add_styled_paragraph` handle the formatting of text, links, and styles within the DOCX.
    * Specific functions for each resume/cover letter section:
        * `add_contact_info_docx()`
        * `add_section_header_docx()`
        * `add_summary_docx()`
        * `add_work_experience_docx()` (parses LLM's markdown-like string output for jobs)
        * `add_technical_skills_docx()` (parses LLM's markdown-like string for skills categories)
        * `add_projects_docx()` (parses LLM's markdown-like string for projects, includes logic for hyperlinks based on project titles)
        * `add_education_docx()` (uses predefined education info from `config.py`)
3.  **Main Generation Functions:**
    * **`generate_styled_resume_pdf(...)`:**
        * Takes tailored data (dictionary of section strings), contact info, education info, output directory, and filename parameters.
        * Creates a `docx.Document` object.
        * Sets up document styles and margins.
        * Calls the various `add_*_docx` functions to populate the document.
        * Constructs a PDF filename based on candidate name, company, YOE, and keyword.
        * Calls `generate_pdf_via_google_drive()` to perform the DOCX -> GDoc -> PDF conversion and cleanup.
        * Returns the path to the local PDF.
    * **`generate_cover_letter_pdf(...)`:**
        * Takes cover letter body text, contact info, job title, company name, output directory, and filename parameters.
        * Creates a `docx.Document` object.
        * Sets up document styles (traditional letterhead style).
        * Adds candidate's contact info at the top.
        * Processes the main body of the cover letter (strips LLM signature, adds paragraphs with markdown bolding).
        * Adds a formatted closing (Sincerely, Name, Phone, Email, GitHub/Portfolio links from contact info).
        * Constructs a PDF filename.
        * Calls `generate_pdf_via_google_drive()` for conversion.
        * Returns the path to the local PDF.

**Alternative PDF Generation (`src/pdf_generator.py`, `src/data_parser_for_pdf.py`):**

* `src/data_parser_for_pdf.py`:
    * Contains functions (`parse_contact_info_from_resume_pdf_text`, `parse_llm_work_experience_string`, `parse_llm_technical_skills_string`, `parse_llm_projects_string`, `parse_education_from_resume_pdf_text`) to parse both the original PDF resume text and the LLM's string outputs into more structured Python dictionaries and lists.
    * `preprocess_tailored_data_for_pdf()`: Consolidates data from tailored JSON and original resume text into a structure suitable for an HTML template.
    * `extract_tailored_data_for_resume_pdf()`: This function is **actually used by `scrape.py`** to prepare the data from the `TailoringState.tailored_resume` model dump for the `docx_to_pdf_generator.py`. It flattens the structured data (e.g., list of work experiences) back into markdown-formatted strings that the DOCX generator expects.
* `src/pdf_generator.py`:
    * `generate_pdf_from_json_xhtml2pdf()`: This function suggests an alternative PDF generation method using `xhtml2pdf` and Jinja2 templates. It would take a JSON file (like `tailored_resume.json`), preprocess it using `data_parser_for_pdf.preprocess_tailored_data_for_pdf`, render an HTML template, and then convert the HTML to PDF.
    * **Note:** While `pdf_generator.py` exists, the primary PDF generation flow in `main.py` and `scrape.py` uses `src/docx_to_pdf_generator.py` which relies on Google Drive. The `xhtml2pdf` route might be an older or alternative approach.

## 📧 Emailing (`utils/email_sender.py`)

* The `send_job_application_email()` function handles sending emails.
* **SMTP Provider:** Configured for Brevo (formerly Sendinblue) via `config.py` (server, port, login, API key from environment variable `BREVO_SMTP_KEY_ENV_VAR_NAME`).
* **Functionality:**
    * Constructs a `MIMEMultipart` email message.
    * Sets From, To, Date, and Subject.
    * Attaches the email body (plain text).
    * Attaches files (e.g., tailored resume PDF, cover letter PDF) if provided.
    * Connects to the Brevo SMTP server (handles SSL/TLS based on port).
    * Authenticates and sends the email.
* Used by `scrape.py` to send the tailored documents and critique to the `APP_EMAIL_RECIPIENT` specified in `config.py`.

## ☁️ Google Cloud Storage (`utils/gcs_utils.py`)

* `get_gcs_client()`: Initializes and returns a Google Cloud Storage client.
    * Authenticates using service account JSON content loaded from the environment variable specified by `GOOGLE_CREDENTIALS_JSON_CONTENT` in `config.py`.
* `upload_file_to_gcs()`: Uploads a local file to the GCS bucket specified by `GCS_BUCKET_NAME` in `config.py`.
    * Used by `scrape.py` to store the generated PDF resume and cover letter.
    * Organizes files in GCS under `tailored_applications/<company_name>/<date>/<timestamp_filename>`.

## 📝 Logging

* **Configuration (`config.py`):** Defines `LOG_LEVEL` (e.g., INFO, DEBUG), `LOG_FORMAT`, and paths for log files (`APP_LOG_FILE` for `main.py`, `SCRAPER_LOG_FILE` for `scrape.py`).
* **`main.py` Setup:** Configures basic logging using `logging.basicConfig()`.
* **`scrape.py` Setup:** Configures more detailed logging, including a `FileHandler` for `combined_job_scraper.log` and a `StreamHandler` for console output. It also sets logging levels for verbose third-party libraries like `selenium` and `webdriver_manager`.
* **Throughout the Code:** Standard Python `logging` module is used by various agents and utilities to record information, warnings, and errors. The logs are crucial for debugging and monitoring the application's behavior, especially for the long-running `scrape.py` process. The `combined_job_scraper.log` shows detailed steps of scraping, filtering, tailoring, PDF generation, GCS upload, and emailing.

## 💡 Potential Deployment Considerations

* **Environment Variables:** Critical for API keys, credentials, and some configurations. A robust way to manage these (e.g., `.env` files, secret management systems) is essential.
* **Python Environment:** Consistent Python version and dependencies managed via `requirements.txt`.
* **Chromedriver:** Needs to be correctly installed and compatible with the Chrome/Chromium browser in the deployment environment for the scraping functionality.
* **Google Cloud Services:**
    * The service account needs appropriate IAM permissions for Google Drive (file creation, modification, deletion, export) and GCS (bucket/object read/write).
    * APIs (Drive, GCS) must be enabled in the GCP project.
* **Email Service (Brevo):** Valid Brevo account with a verified sender email and sufficient sending quota.
* **Scheduling `scrape.py`:** If deploying as a service, a system-level scheduler (like cron on Linux or Task Scheduler on Windows) or a process manager (like systemd, Supervisor) would be needed to run `scrape.py` periodically.
* **Resource Management:** The scraping process (especially with Selenium) and LLM calls can be resource-intensive (CPU, memory, network).
* **Error Handling and Resilience:** The `scrape.py` script has logging for errors, but more robust error handling, retries (especially for network operations), and monitoring might be beneficial for a production deployment.
* **Headless Operation for Selenium:** `scrape.py` configures Chrome options for headless operation (`--headless`, `--no-sandbox`, `--disable-dev-shm-usage`), which is suitable for server environments. 