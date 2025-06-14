# Resume_Tailoring/config.py
import os
import logging
from dotenv import load_dotenv # Import load_dotenv

# Add this log at the very top of config.py
logging.info("config.py: Module execution started.")

# Determine the path to the .env file (should be in PROJECT_ROOT)
# PROJECT_ROOT is defined as os.path.dirname(os.path.abspath(__file__))
# So, .env should be in the same directory as config.py
project_root_for_dotenv = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(project_root_for_dotenv, '.env')

# Load the .env file
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    logging.info(f"config.py: .env file loaded from {dotenv_path}") 
else:
    logging.warning(f"config.py: .env file not found at {dotenv_path}. Using system environment variables or defaults.")
    pass # If .env is not found, os.getenv will try to get from actual system env vars

# --- Project Root ---
# --- Project Root ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# In config.py
#SERVICE_ACCOUNT_FILE_PATH = r"D:\G_sync\Projects\agent_resume_builder\legal-assistant-456618-bfee2203ebee.json"

SERVICE_ACCOUNT_JSON_CONTENT = os.getenv("GOOGLE_CREDENTIALS_JSON_CONTENT")
if not SERVICE_ACCOUNT_JSON_CONTENT:
    logging.warning("config.py: GOOGLE_CREDENTIALS_JSON_CONTENT environment variable not found or is empty. Service account features may not work if they rely on this.")
    # You might want to set a default or raise an error if this is critical for some parts of your app
    # For now, it will be None if not set in the environment.
# Relative path from PROJECT_ROOT to the desired profile directory##os.getenv("GOOGLE_CREDENTIALS_JSON_CONTENT")
JOBRIGHT_PROFILE_DIR_RELATIVE = os.path.join("Scrapping", "chrome_jobright_profile")
# --- Subdirectory Paths ---
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates") 
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs") 

# --- Default Input File Names/Paths ---
BASE_RESUME_PDF_NAME = "Shanmugam_AI_2025_4_YOE.pdf" 
JOB_DESC_TXT_NAME = "job.txt" 
DEFAULT_MASTER_PROFILE_NAME = "master_profile.txt"

DEFAULT_BASE_RESUME_PDF_PATH = os.path.join(PROJECT_ROOT, BASE_RESUME_PDF_NAME) 
DEFAULT_JOB_DESC_PATH = os.path.join(PROJECT_ROOT, JOB_DESC_TXT_NAME)       
DEFAULT_MASTER_PROFILE_PATH = os.path.join(PROJECT_ROOT, DEFAULT_MASTER_PROFILE_NAME) 
#"chrome_jobright_profile" #
# --- Default Output File Names/Paths ---
TAILORED_JSON_OUTPUT_NAME = "tailored_resume.json" 
DEFAULT_PDF_OUTPUT_DIR = os.path.join(DATA_DIR, "tailored_documents")
DEFAULT_TAILORED_JSON_PATH = os.path.join(DEFAULT_PDF_OUTPUT_DIR, TAILORED_JSON_OUTPUT_NAME) 
# In Resume_Tailoring/config.py

# ... (other configurations like PROJECT_ROOT, SERVICE_ACCOUNT_JSON_CONTENT) ...

# --- Google Cloud Storage Configuration ---
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "tailoring-agent") # "tailoring-agent"#Or directly your bucket name
# Ensure GOOGLE_CREDENTIALS_JSON_CONTENT is also set and has permissions for this bucket.

# ... (rest of your configurations) ...
# --- Predefined Profile Information for DOCX/PDF Generation ---
# In Resume_Tailoring/config.py

PREDEFINED_CONTACT_INFO = {
    "name": "Venkatesh Shanmugam",
    "street_address": "123 Example Street, Apt 4B",  # Add your street address
    "city_state_zip": "Arlington, VA 22201",     # Add City, State, Zip
    "phone": "+1 (703) 216-2540",                # Explicit phone
    "email": "svenkatesh.js@gmail.com",          # Explicit email
    "linkedin_text": "LinkedIn Profile",         # More descriptive text for the link
    "linkedin_url": "https://www.linkedin.com/in/svenkatesh-js/",
    "github_text": "GitHub Portfolio",           # More descriptive text for the link
    "github_url": "https://github.com/Venkat-Git98",
    "portfolio_text": "Personal Portfolio",      # More descriptive text for the link
    "portfolio_url": "https://venkatjs.netlify.app/",
    "line1_info": "Virginia US | svenkatesh.js@gmail.com | +1 (703) 216-2540" # Can be kept for other uses or removed if redundant
}

PREDEFINED_EDUCATION_INFO = [ 
    {
        "degree_line": "Master of Science in Computer Science (3.81 / 4.0)", 
        "university_line": "George Washington University", 
        "dates_line": "August 2023 - May 2025" 
    },
    {
        "degree_line": "Bachelor of Technology in Computer Science (3.5/4.0)", 
        "university_line": "SRM University", 
        "dates_line": "August 2016 - May 2020" 
    }
]

# --- Defaults for PDF Filename Parameters ---
DEFAULT_TARGET_COMPANY = "TargetCompany" 
DEFAULT_YOE = 4 
DEFAULT_FILENAME_KEYWORD = "AI" 

# --- LLM Configuration ---
GEMINI_MODEL_FOR_TAILORING = os.getenv("GEMINI_MODEL", "gemini-1.5-pro-001") 

# --- Logging Configuration ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper() 
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(module)s.%(funcName)s - %(message)s" 
APP_LOG_FILE = os.path.join(LOGS_DIR, "resume_tailoring_app.log")

# --- Scraper Configuration ---
SCRAPER_LOG_FILE = os.path.join(LOGS_DIR, "combined_job_scraper.log")
SCRAPED_JOBS_DATA_DIR = os.path.join(DATA_DIR, "scraped_jobs") # Defined for clarity
SCRAPER_CONSOLIDATED_ALL_JOBS_FILE = os.path.join(SCRAPED_JOBS_DATA_DIR, "consolidated_all_jobs.json")
SCRAPER_CONSOLIDATED_RELEVANT_NEW_JOBS_FILE = os.path.join(SCRAPED_JOBS_DATA_DIR, "consolidated_relevant_new_jobs.json")
SCRAPER_SCHEDULE_INTERVAL_MINUTES = int(os.getenv("SCRAPE_INTERVAL_MINUTES", 60))
SCRAPER_RELEVANT_JOB_KEYWORDS = [
    "data", "machine learning", "ml ", " ml", " ai ", " ai", "artificial intelligence",
    "scientist", "applied scientist", "research scientist", "data engineer", "ml engineer",
    "analytics", "statistician", "quantitative", "software", "developer", "llm", "prompt engineering", "rag"
]

# --- Job Source Domain Exclusion Configuration ---
EXCLUDE_JOB_SOURCES_DOMAINS = [
    "lensa.com", "dice.com", "ziprecruiter.com", "glassdoor.com", 
    "monster.com", "careerbuilder.com", "indeed.com", "simplyhired.com",
    "snagajob.com", "workopolis.com", "jobbank.gc.ca"
]

# --- Other Job Filtering Configuration ---
RELEVANT_JOB_KEYWORDS = [
    "data scientist", "machine learning", "ml engineer", "ai engineer", 
    "data engineer", "applied scientist", "research scientist", "software engineer",
    "developer", "llm", "prompt engineering", "rag", "artificial intelligence"
]

SOFTWARE_ENGINEER_TERMS = ["software engineer", "sde", "software developer"]
AI_ML_DATA_MODIFIERS_FOR_SE_TITLE = ["ai", "ml", "machine learning", "data", "artificial intelligence"]
EXCLUDE_JOB_TITLE_FIELDS = ["frontend", "ui developer", "web developer", "mobile developer", "ios developer", "android developer"]
EXCLUDE_JOB_TITLE_SENIORITY = ["lead", "principal", "director", "manager", "senior manager", "vp", "head of"]

# --- Email Configuration (Now Centralized for Brevo) ---
# Brevo SMTP Settings
BREVO_SMTP_SERVER = "smtp-relay.brevo.com"
BREVO_SMTP_PORT = 587
BREVO_SMTP_LOGIN = os.getenv("BREVO_SMTP_LOGIN", "your_default_brevo_login_if_any_for_dev")

# Brevo SMTP Key (Password)
# It's STRONGLY recommended to use an environment variable for this in production.
# This config defines the NAME of the environment variable to check.
BREVO_SMTP_KEY_ENV_VAR_NAME = "BREVO_SMTP_KEY" 
# !! WARNING: The fallback key below is for your immediate local testing only. !!
# !! DO NOT commit your actual key to version control if it's hardcoded here.  !!
# !! Ideally, remove this fallback entirely before any sharing/deployment.       !!
BREVO_SMTP_KEY_FALLBACK_FOR_TESTING = None

# Displayed 'From' Email Address for Brevo
# This email MUST be a VERIFIED SENDER in your Brevo account.
BREVO_SENDER_DISPLAY_EMAIL = os.getenv("BREVO_SENDER_DISPLAY_EMAIL")

# Recipient Email for emails sent by the Scraper/Application
# This is the email address that will receive the job applications and critiques.
APP_EMAIL_RECIPIENT = os.getenv("APP_EMAIL_RECIPIENT")


# --- Directory Creation ---
# (Ensuring directories exist is good practice)
for dir_path in [DATA_DIR, DEFAULT_PDF_OUTPUT_DIR, LOGS_DIR, SCRAPED_JOBS_DATA_DIR]:
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
            logging.info(f"Created directory: {dir_path}")
        except OSError as e:
            logging.error(f"Error creating directory {dir_path}: {e}")