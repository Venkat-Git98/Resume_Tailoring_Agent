
import logging
import re
from typing import Optional

from models import JobDescription, ResumeSections, ResumeCritique
from utils.llm_gemini import GeminiClient, get_resume_critique_prompt

class ResumeJudgeAgent:
    """Agent to critique the resume and generate hiring manager messages."""

    def __init__(self, llm_client: GeminiClient):
        self.llm = llm_client

    # In Resume_Tailoring/agents/resume_judge_agent.py

    def _parse_critique_and_messages(self, text: str) -> ResumeCritique:
        """Parses the combined output from the LLM."""
        critique = ResumeCritique()
        try:
            # Make the regex robust to optional '##' and whitespace
            score_match = re.search(r"#*\s*SCORE:\s*(\d+)/100", text, re.IGNORECASE)
            if score_match:
                critique.score = float(score_match.group(1))

            critique.pros = self._extract_list_items(text, "PROS")
            critique.cons = self._extract_list_items(text, "CONS")
            critique.suggestions = self._extract_list_items(text, "SUGGESTIONS")

            # Make the regex robust to optional '##' and whitespace
            verdict_match = re.search(r"#*\s*FINAL_VERDICT:\s*(.*)", text, re.DOTALL | re.IGNORECASE)
            if verdict_match:
                # Ensure the split correctly finds the next header
                verdict_text = verdict_match.group(1).split("HIRING_MANAGER_EMAIL:")[0].split("## HIRING_MANAGER_EMAIL:")[0].strip()
                critique.final_verdict = verdict_text

            # Make the regex robust to optional '##' and whitespace
            email_match = re.search(r"#*\s*HIRING_MANAGER_EMAIL:\s*(.*)", text, re.DOTALL | re.IGNORECASE)
            if email_match:
                # Ensure the split correctly finds the next header
                email_text = email_match.group(1).split("CONNECTION_REQUEST:")[0].split("## CONNECTION_REQUEST:")[0].strip()
                critique.email_to_hiring_manager = email_text

            # Make the regex robust to optional '##' and whitespace
            connection_match = re.search(r"#*\s*CONNECTION_REQUEST:\s*(.*)", text, re.DOTALL | re.IGNORECASE)
            if connection_match:
                critique.connection_request = connection_match.group(1).strip()
            
            return critique
        except Exception as e:
            logging.error(f"Error parsing critique and messages: {e}", exc_info=True)
            return critique

    def _extract_list_items(self, text: str, section_name: str) -> list[str]:
        """Extracts list items from a specific section of the text."""
        try:
            # Make the regex robust to optional '##' and different list markers (* or -)
            section_pattern = re.compile(rf"#*\s*{section_name}:\s*\n(.*?)(?=\n\n#*\s*[A-Z_]+:|\Z)", re.DOTALL | re.IGNORECASE)
            section_match = section_pattern.search(text)
            if section_match:
                content = section_match.group(1)
                return [item.strip() for item in re.findall(r"[\*\-]\s*(.*)", content)]
        except Exception:
            pass
        return []

    def _extract_list_items(self, text: str, section_name: str) -> list[str]:
        """Extracts list items from a specific section of the text."""
        try:
            section_pattern = re.compile(rf"{section_name}:\s*\n(.*?)(?=\n\n[A-Z_]+:|\Z)", re.DOTALL | re.IGNORECASE)
            section_match = section_pattern.search(text)
            if section_match:
                content = section_match.group(1)
                return [item.strip() for item in re.findall(r"-\s*(.*)", content)]
        except Exception:
            pass
        return []


    def run(
        self,
        job_desc: JobDescription,
        tailored_resume: ResumeSections,
        master_profile_text: Optional[str] = None,
    ) -> tuple[Optional[ResumeCritique], Optional[str]]:
        """
        Generates a resume critique, a hiring manager email, and a connection request.
        """
        logging.info("ResumeJudgeAgent: Starting generation...")
        try:
            company_name = job_desc.job_title.split(" at ")[-1].strip().title() if " at " in job_desc.job_title.lower() else "the company"
            
            prompt = get_resume_critique_prompt(
                job_title=job_desc.job_title,
                company_name=company_name,
                job_requirements_summary="\n".join(job_desc.requirements),
                ats_keywords_str=", ".join(job_desc.ats_keywords),
                tailored_resume_summary_text=tailored_resume.summary,
                master_profile_text=master_profile_text,
            )

            response_text = self.llm.generate_text(prompt, temperature=0.3, max_tokens=2500)
            
            if response_text:
                parsed_critique = self._parse_critique_and_messages(response_text)
                return parsed_critique, response_text
            
            return None, None

        except Exception as e:
            logging.error(f"ResumeJudgeAgent: Failed to generate critique and messages: {e}", exc_info=True)
            return None, None