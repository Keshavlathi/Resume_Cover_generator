from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import re
import urllib.parse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes (so the frontend can call this backend)
CORS(app)

HF_API_URL = "https://router.huggingface.co/v1/chat/completions"
# Load key from .env file
HF_API_KEY = os.getenv("HUGGING_FACE_API_KEY")

def extract_latex(text):
    """Cleans up the output from the LLM, returning only the LaTeX block."""
    # Attempt to extract markdown block
    match = re.search(r'```(?:latex|tex)?\n([\s\S]*?)\n```', text, re.IGNORECASE)
    if match and match.group(1):
        return match.group(1).strip()
        
    # Fallback: Extract between documentclass and end document
    start_idx = text.find('\\documentclass')
    if start_idx != -1:
         end_idx = text.find('\\end{document}') + 14
         return text[start_idx:end_idx].strip()
         
    return text.strip()

def generate_latex_from_hf(prompt):
    """Calls the Hugging Face API to generate the LaTeX code."""
    if not HF_API_KEY or HF_API_KEY == "your_hugging_face_api_key_here":
        raise ValueError("Missing or invalid Hugging Face API Key in .env file.")

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1500,
        "temperature": 0.1
    }
    
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    
    if not response.ok:
        err = response.json()
        error_msg = err.get("error", "Unknown error from Hugging Face API")
        if "is currently loading" in error_msg:
            raise RuntimeError("The AI model is currently loading. Please wait ~30 seconds and try again.")
        raise RuntimeError(f"Hugging Face Error: {error_msg}")
        
    data = response.json()
    generated_text = data.get('choices', [{}])[0].get('message', {}).get('content', '')
    return extract_latex(generated_text)

@app.route('/api/generate', methods=['POST'])
def generate_docs():
    """Main API endpoint to generate both Resume and Cover Letter"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No input data provided"}), 400
            
        full_name = data.get('fullName')
        contact_info = data.get('contactInfo', '')
        linkedin_url = data.get('linkedinUrl', '')
        github_url = data.get('githubUrl', '')
        experience = data.get('experience', '')
        education = data.get('education', '')
        job_title = data.get('jobTitle', '')
        company_name = data.get('companyName', '')
        job_description = data.get('jobDescription', '')

        if not full_name or not experience or not job_title:
             return jsonify({"error": "Missing essential fields: Name, Experience, or Job Title"}), 400
             
        # Build extended contact string
        extended_contact = contact_info
        if linkedin_url:
            extended_contact += f" | LinkedIn: {linkedin_url}"
        if github_url:
            extended_contact += f" | GitHub: {github_url}"

        resume_prompt = f"""You are an expert LaTeX resume writer. Create a professional, modern LaTeX resume for {full_name}. 
Contact Info: {extended_contact}
Experience: {experience}
Education: {education}
Target Role: {job_title} at {company_name}.
Job Description: {job_description}

STRICT INSTRUCTIONS FOR THE AI (DO NOT INCLUDE THESE IN YOUR OUTPUT):
1. You must ONLY output valid, compilable LaTeX code. DO NOT output any conversational text, markdown formatting (like ```latex), or explanations. 
2. DO NOT repeat these instructions in the resume text.
3. Use the `article` class. The very first line of your output MUST be \\documentclass[10pt,a4paper]{{article}}. The very last line MUST be \\end{{document}}.
4. Include \\usepackage[margin=0.5in]{{geometry}} to fit on exactly ONE page, and \\usepackage{{hyperref}} so \\href commands work. Escape special characters like &, %, $, #, _, {{, }}, ~, ^, \\.
5. Make the resume ATS friendly: use a clean, single-column layout without complex tables. Keep descriptions extremely concise to fit 1 page. Output standard LaTeX hyphens "--" instead of unicode dashes.
6. Format all section headings (Summary, Experience, Education, Skills) in bold using \\textbf{{...}}. Include all these standard sections.
7. CRITICAL: DO NOT use the `fontspec` package or any external fonts that require xelatex/lualatex. Compile using standard pdflatex (use packages like `lmodern`).
8. CRITICAL: Ensure every \\begin{{...}} has a matching \\end{{...}}. Do not leave any environments unclosed (e.g. \\begin{{itemize}} MUST be closed with \\end{{itemize}})."""

        cover_prompt = f"""You are an expert career advisor and copywriter. Create a professional, compelling cover letter for {full_name} applying for the role of {job_title} at {company_name}.
Contact Info: {extended_contact}
Experience: {experience}
Education: {education}
Job Description: {job_description}

STRICT INSTRUCTIONS FOR THE AI:
1. Output the cover letter formatted in clean HTML (using tags like <p>, <br>, <strong>).
2. DO NOT include ```html markdown blocks. Return ONLY the HTML tags and content.
3. Make it professional, tailored to the job description, and highlight the most relevant experience and skills.
4. Ensure it has a formal structure (Header, Salutation, Introduction, Body Paragraphs, Call to Action, Sign-off)."""

        # Generate LaTeX for Resume and HTML for Cover Letter
        resume_latex = generate_latex_from_hf(resume_prompt)
        
        # The prompt for cover letter is HTML now, but generate_latex_from_hf might try to extract LaTeX.
        # Let's write a small helper or just call requests directly for the cover letter to avoid LaTeX extraction logic.

        # Direct call to HF for Cover Letter (HTML) to bypass LaTeX extraction
        cover_payload = {
            "model": "meta-llama/Meta-Llama-3-8B-Instruct",
            "messages": [{"role": "user", "content": cover_prompt}],
            "max_tokens": 1500,
            "temperature": 0.3
        }
        headers = {"Authorization": f"Bearer {HF_API_KEY}", "Content-Type": "application/json"}
        cover_res = requests.post(HF_API_URL, headers=headers, json=cover_payload)
        
        if cover_res.ok:
            cover_data = cover_res.json()
            cover_html = cover_data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            # Remove possible markdown ticks if the AI returns them despite instructions
            cover_html = cover_html.replace("```html", "").replace("```", "").strip()
        else:
            cover_html = "<p>Error generating cover letter.</p>"

        # Generate download URL using latexonline.cc only for Resume
        resume_pdf_url = f"https://latexonline.cc/compile?text={urllib.parse.quote(resume_latex)}"

        return jsonify({
            "success": True,
            "resume_latex": resume_latex,
            "resume_pdf_url": resume_pdf_url,
            "cover_html": cover_html
        })

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 401 # Unauthorized / bad config
    except RuntimeError as re:
        return jsonify({"error": str(re)}), 502 # Bad gateway
    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({"error": "An unexpected server error occurred."}), 500

if __name__ == '__main__':
    print("Starting AI Career Architect Backend on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
