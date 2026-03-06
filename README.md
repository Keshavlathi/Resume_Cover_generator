# Nova | AI Career Architect 🚀

Nova is a next-generation AI Resume and Cover Letter Generator that leverages the powerful **Hugging Face API** (Meta-Llama-3-8B-Instruct) to create professional, ATS-friendly career documents tailored to your specific profile and target role.

## Features ✨

* **Intelligent Resume Generation**: Instantly generates a clean, single-page LaTeX resume customized to a job description.
* **Automatic PDF Compilation**: Converts the generated LaTeX code directly into a downloadable PDF document using `latexonline.cc`.
* **Tailored Cover Letters**: Crafts professional, formal cover letters in HTML format, perfectly aligned with the target job role.
* **Modern UI/UX**: A responsive frontend design featuring a sleek glassmorphism aesthetic with glowing visual effects.
* **Bypass AI Model Loading**: Gracefully handles model loading states and errors from the Hugging Face API.

## Tech Stack 🛠️

* **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
* **Backend**: Python, Flask, Flask-CORS
* **AI Integrations**: Hugging Face serverless inference API (`meta-llama/Meta-Llama-3-8B-Instruct`)
* **External Services**: latexonline.cc (LaTeX to PDF conversion)

## Installation & Setup ⚙️

### Prerequisites

* Python 3.8+
* Hugging Face API Key (Access Token)

### 1. Backend Setup

Navigate to the `backend` directory and set up your environment:

```bash
cd backend
# Create virtual environment if it doesn't exist
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies (Flask, requests, python-dotenv, flask-cors)
pip install -r .venv/requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the `backend/.venv` directory and configure your Hugging Face API key:

```env
HUGGING_FACE_API_KEY="your_hugging_face_api_key_here"
```

### 3. Running the Application

**Start the Flask Backend:**

```bash
cd backend/.venv
python app.py
```

*(The server will start mapping the backend APIs at `http://localhost:5000`)*

**Start the Frontend:**

Simply open `frontend/index.html` in your web browser. Alternatively, you can serve it with a local development server like Live Server (VS Code extension) or Python's built-in HTTP server:

```bash
cd frontend
python -m http.server 8000
```

Then navigate to `http://localhost:8000`.

## How to Use 🎯

1. Open the Nova application in your browser.
2. Fill out the **Profile Details** section (Name, Contact Info, LinkedIn, GitHub, Experience, Education).
3. Fill out the **Target Role** section (Job Title, Company Name, and paste the full Job Description).
4. Click the **Generate LaTeX PDF Docs** button.
5. Wait for the AI to process your request. Once complete, you will be able to:
    * Download your tailored ATS-friendly Resume as a direct PDF.
    * View or download your Cover Letter directly in the browser (in HTML/Word format).
    * View the raw LaTeX codebase and HTML logic in the drop-down toggles.

## Notice ⚠️

This project requires an active internet connection for the Hugging Face model inference and the internal LaTeX-to-PDF compilation endpoint to work properly. Ensure that your Hugging Face token has adequate inference permissions.
