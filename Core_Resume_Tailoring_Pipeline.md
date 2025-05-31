⬅️ **[Back to Main README (`Readme.md`)](./Readme.md)**

# Automated Resume Tailoring Agent: Core Pipeline

This document details the core resume tailoring pipeline, from analyzing job descriptions to generating tailored application materials and critiquing the resume.

## 🚀 Main Workflow (`main.py` & `agents/orchestrator.py`)

The primary execution flow is managed by `main.py`, which acts as the entry point and command-line interface. It orchestrates the resume tailoring process by utilizing the `OrchestratorAgent`.

**`main.py` Key Responsibilities:**

1.  **Argument Parsing:** Uses `argparse` to accept command-line arguments for:
    * Input resume PDF path (`--resume`, `-r`).
    * Input job description text file path (`--job`, `-j`).
    * Output directory for PDFs (`--outputdir`, `-od`).
    * Path to master profile text file (`--masterprofile`, `-mp`, optional).
    * Target company name, YOE, and keyword for PDF filenames (`--company`, `--yoe`, `--keyword`).
    * Flag to save intermediate tailored JSON (`--savejson`).
    * Output path for cover letter text file (`--outputcoverletter`, `-ocl`, optional).
    * Explicit company name for cover letter (`--clcompany`, optional).
2.  **Configuration & Logging Setup:** Initializes logging and loads configuration from `config.py` (or uses fallbacks if `config.py` is not found).
3.  **Input Validation:** Checks for the existence and correct format of resume and job description files.
4.  **LLM Client Initialization:** Initializes the `GeminiClient` for communication with the Google Gemini LLM.
5.  **Orchestration:**
    * Instantiates the `OrchestratorAgent`.
    * Calls the `orchestrator.run()` method, passing paths to the resume, job description (or raw JD text if available directly, though `main.py` primarily handles file paths), master profile content, and contact/company details for the cover letter.
6.  **Output Handling:**
    * If `--savejson` is specified, saves the intermediate JSON output from the LLM.
    * If PDF generation is available (`src.docx_to_pdf_generator` can be imported) and the tailoring process is successful:
        * Calls `generate_styled_resume_pdf()` to create the tailored resume PDF.
        * Calls `generate_cover_letter_pdf()` to create the tailored cover letter PDF.
    * If a separate cover letter text file is requested, it saves the generated cover letter text.
    * Logs the resume critique (ATS score, pass assessment, recruiter impression).

**`agents/orchestrator.py` (`OrchestratorAgent`):**

The `OrchestratorAgent` is the central coordinator of the tailoring pipeline. Its `run()` method executes the following steps sequentially:

1.  **Initialize `TailoringState`:** Creates a Pydantic model instance to hold all data throughout the process (original resume, JD, tailored sections, cover letter, critique).
2.  **Job Description Analysis:**
    * Calls the `JDAnalysisAgent` to parse the job description (either from a file path or raw text).
    * Stores the resulting `JobDescription` model (containing title, requirements, ATS keywords) in the `TailoringState`.
3.  **Resume Parsing:**
    * Calls the `ResumeParserAgent` to read the input resume PDF and split it into sections (Summary, Work Experience, etc.).
    * Stores the resulting `ResumeSections` model in `TailoringState.original_resume`.
4.  **Resume Section Tailoring:**
    * Calls the `TailoringAgent` with the parsed job description, original resume sections, and optional master profile text.
    * The `TailoringAgent` iteratively rewrites each resume section (`summary`, `work_experience`, `technical_skills`, `projects`) using LLM prompts. It accumulates previously tailored sections to provide context for subsequent sections.
    * Stores the tailored `ResumeSections` model in `TailoringState.tailored_resume` and the full concatenated tailored text in `TailoringState.accumulated_tailored_text`.
5.  **Cover Letter Generation:**
    * Calls the `CoverLetterAgent` with the job description, tailored resume sections, candidate contact information, master profile text, and an optional explicit company name.
    * Stores the generated cover letter text in `TailoringState.generated_cover_letter_text`.
6.  **Resume Critique:**
    * Calls the `ResumeJudgeAgent` with the job description and the full text of the tailored resume.
    * Stores the raw critique text and the parsed `ResumeCritique` model (ATS score, pass assessment, recruiter impression, etc.) in the `TailoringState`.
7.  **Return `TailoringState`:** Returns the populated `TailoringState` object containing all artifacts.

## 📄 Job Description Analysis (`agents/jd_analysis.py`)

The `JDAnalysisAgent` is responsible for processing the job description.

* **Input:** Can take either a file path to a `.txt` job description (`jd_txt_path`) or the raw job description text directly (`jd_text`). Raw text takes precedence.
* **Processing:**
    1.  Reads the JD text.
    2.  A simple parsing logic extracts the job title (assumed to be the first line) and requirements (subsequent lines).
    3.  Utilizes the `GeminiClient` to make an LLM call via `_extract_ats_keywords_with_llm`. This method sends a specialized prompt to the LLM to identify and extract 15-20 critical ATS keywords from the JD, focusing on technical skills, tools, and core concepts relevant to ML/Data Science roles.
* **Output:** Returns a `JobDescription` Pydantic model containing:
    * `job_title`: Extracted job title.
    * `requirements`: A list of strings, where each string is a line/paragraph from the JD (excluding the title).
    * `ats_keywords`: A list of ATS keywords extracted by the LLM.

## 📄 Resume Parsing (`agents/resume_parser.py`, `utils/file_utils.py`, `utils/nlp_utils.py`)

The `ResumeParserAgent` handles the initial processing of the candidate's base resume.

* **`utils/file_utils.py`:**
    * `read_pdf_text(pdf_path)`: Uses `PyMuPDF (fitz)` to extract all text content from the provided PDF resume.
* **`utils/nlp_utils.py`:**
    * `split_resume_sections(pdf_text)`: Takes the raw text extracted from the PDF and attempts to split it into standard resume sections (Summary, Work Experience, Technical Skills, Projects). It uses regex to find headers like "SUMMARY", "WORK EXPERIENCE", etc., and extracts the text between them. The order of headers defined in the function matters for correct sectioning.
* **`agents/resume_parser.py` (`ResumeParserAgent`):**
    * Its `run(resume_pdf_path)` method:
        1.  Calls `file_utils.read_pdf_text()` to get the raw text from the PDF.
        2.  Calls `nlp_utils.split_resume_sections()` to divide the raw text into a dictionary of sections.
        3.  Populates and returns a `ResumeSections` Pydantic model with the extracted text for each section.

## ✍️ Resume Section Tailoring (`agents/tailoring.py`)

The `TailoringAgent` is responsible for the core LLM-based rewriting of resume sections.

* **Sections Tailored:** `summary`, `work_experience`, `technical_skills`, `projects`.
* **Process for each section:**
    1.  Retrieves the original content for the current section from the `ResumeSections` model.
    2.  If original content exists, it constructs a detailed prompt using `utils.llm_gemini.get_section_prompt()`. This prompt includes:
        * The candidate's original content for that section.
        * The target job title, key requirements, and ATS keywords from the `JobDescription`.
        * The optional `master_profile_text`.
        * Crucially, the `previously_tailored_sections_text` (an accumulation of already rewritten sections) to provide context to the LLM and ensure consistency/avoid repetition.
        * Specific instructions for length, format, tone, and keyword integration for the current section (these are embedded within `get_section_prompt`). For example, the summary has strict length constraints and instructions not to mention the company name. Work experience has role-specific bullet point count and character limits.
    3.  Makes a call to the `GeminiClient` (`self.llm.generate_text()`) with the generated prompt and appropriate `max_tokens` for that section.
    4.  The raw LLM output is cleaned using `_clean_llm_section_output()` to remove potential artifacts like markdown code blocks or prefixed labels (e.g., "Summary:").
    5.  The cleaned, tailored content for the section is stored.
    6.  The tailored content is then formatted (e.g., with a markdown header like `## SUMMARY`) and appended to `accumulated_tailored_text` for the next section's context.
* **Output:** Returns a `ResumeSections` Pydantic model containing all the tailored sections and the `accumulated_tailored_text` string.

## 📧 Cover Letter Generation (`agents/cover_letter_agent.py`)

The `CoverLetterAgent` generates a cover letter tailored to the job.

* **Input:** `JobDescription` model, tailored `ResumeSections` model, candidate's contact information (dictionary), optional `master_profile_text`, and an optional `company_name_override`.
* **Project Details Extraction (`_get_project_details_for_cl`):**
    * Parses the `tailored_resume.projects` text to extract project titles.
    * Attempts to map these titles to URLs defined in `self.project_hyperlinks_config` or dynamically constructed GitHub URLs if a `github_base_url` is available from the contact info. This is used to inform the LLM if projects have demos, but URLs are NOT inserted into the cover letter body.
* **Prompt Generation (`utils.llm_gemini.get_cover_letter_prompt()`):**
    * Constructs a detailed prompt providing the LLM with:
        * Candidate's name and contact details.
        * Target job title and company name (uses override if provided, otherwise tries to extract from JD title).
        * A summary of job requirements and ATS keywords from the `JobDescription`.
        * The text of the tailored resume summary, work experience, and projects.
        * The master profile text (if available).
        * Context about key projects and whether they have demo URLs (for LLM's internal reasoning).
        * Specific instructions for the cover letter's tone, style, structure (e.g., a "10-Second Hook" opening, paragraph depth, company-specific research points if the company name is real, and strict closing format). It also includes instructions to bold 2-4 impactful keywords.
* **LLM Call:** Calls `self.llm.generate_text()` with a slightly higher temperature (0.35) and more tokens (1500) suitable for creative writing.
* **Output:** Returns the cleaned text of the generated cover letter. Cleaning includes removing any prefixed "Cover Letter:" or "--- BEGIN COVER LETTER ---" markers.

## ⚖️ Resume Critique (`agents/resume_judge_agent.py`)

The `ResumeJudgeAgent` evaluates the tailored resume.

* **Input:** `JobDescription` model, tailored `ResumeSections` model, and candidate's name.
* **Preparation:**
    * Concatenates the tailored resume sections (summary, work experience, skills, projects) into a single text block.
    * Formats the job description requirements into a single text block.
* **Prompt Generation (`utils.llm_gemini.get_resume_critique_prompt()`):**
    * Constructs a prompt asking the LLM to act as an expert AI resume reviewer.
    * Provides the job title, full JD text, ATS keywords, and the full text of the tailored resume.
    * **Strict Output Format Requested:** The prompt explicitly asks the LLM to return the critique in a specific format:
        ```
        ATS_SCORE: [score percentage]
        ATS_PASS: [assessment]
        RECRUITER_IMPRESSION: [assessment]
        POTENTIAL_LENGTH_CONCERN: [assessment]
        CONTENT_STRUCTURE_AND_CLARITY: [assessment]
        FORMATTING_CONSISTENCY_FROM_TEXT: [assessment]
        ```
* **LLM Call:** Calls `self.llm.generate_text()` with low temperature (0.1) for factual assessment and limited tokens (300) for conciseness.
* **Parsing (`_parse_critique_text`):**
    * Takes the raw LLM output.
    * Splits the text by lines and then by the first colon to extract key-value pairs.
    * Populates a `ResumeCritique` Pydantic model with the extracted values (ATS score as float, and string assessments for pass likelihood, recruiter impression, length, structure/clarity, and formatting consistency).
* **Output:** Returns a tuple containing the raw critique text from the LLM and the parsed `ResumeCritique` object.

## 🧱 Data Models (`models.py`)

Pydantic models are used for structured data representation:

* **`JobDescription`:**
    * `job_title`: Optional[str]
    * `requirements`: List[str] (lines from the JD)
    * `ats_keywords`: List[str]
* **`ResumeSections`:**
    * `summary`: Optional[str]
    * `work_experience`: Optional[str]
    * `technical_skills`: Optional[str]
    * `projects`: Optional[str]
* **`ResumeCritique`:**
    * `ats_score`: Optional[float] (0-100%)
    * `ats_pass_assessment`: Optional[str]
    * `recruiter_impression_assessment`: Optional[str]
    * `potential_length_concern`: Optional[str]
    * `content_structure_and_clarity`: Optional[str]
    * `formatting_consistency_from_text`: Optional[str]
* **`TailoringState`:** A container model to hold all data during the orchestration process:
    * `job_description`: Optional[JobDescription]
    * `original_resume`: Optional[ResumeSections]
    * `tailored_resume`: Optional[ResumeSections]
    * `accumulated_tailored_text`: str (concatenated text of tailored sections for context)
    * `generated_cover_letter_text`: Optional[str]
    * `resume_critique`: Optional[ResumeCritique]
    * `raw_critique_text`: Optional[str] (raw output from the critique LLM call) 