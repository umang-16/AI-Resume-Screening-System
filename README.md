# 🚀 AI Resume Screening & Hiring System

An advanced, end-to-end recruitment platform that bridges the gap between students and HR professionals using Natural Language Processing (NLP). Built with Python, Flask, and SQLite.

## ✨ Key Features

### For Students:
* **One-Click Apply & Resume Parsing**: Upload your PDF resume and the AI will automatically extract your skills.
* **Smart Job Matching**: Receive a dynamic "AI Compatibility Score" matching your extracted skills directly against job descriptions.
* **Skills Gap Analysis**: The system highlights exactly which skills you need to learn to reach a 100% match.
* **Real-time Application Tracking**: View scheduled interviews (Online/In-Person) and securely download official PDF Offer Letters directly from your dashboard.

### For HR & Companies:
* **Automated Candidate Shortlisting**: Candidates are automatically sorted by their AI Match Score, saving hours of manual review.
* **Seamless Interview Scheduling**: Instantly schedule exact dates, times, and locations (Zoom links/Office addresses) for candidates.
* **Direct Offer Dispatch**: Upload and send official PDF Offer letters to successful candidates with a single click.
* **Company Identity Management**: Customize your verified enterprise profile with dedicated HR contact numbers and corporate background details.

## 🛠️ Technology Stack
* **Backend**: Python 3, Flask, SQLAlchemy (SQLite Database)
* **Frontend**: Vanilla CSS, Bootstrap 5, Jinja2 Templates
* **AI & NLP**: `PyPDF2` (Text Extraction), `spaCy` (Skill Recognition & Categorization), `scikit-learn` (NLP Vectorization)
* **Security**: `Werkzeug` Password Hashing, Flask-Login

## 🖥️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/umang-16/AI-Resume-Screening-System.git
   cd AI-Resume-Screening-System
   ```

2. **Set up Virtual Environment (Optional but Recommended)**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize NLP Model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Run the Application**
   ```bash
   python app.py
   ```
   *The application will be live at `http://127.0.0.1:5000`*

## 🧑‍💻 Contributing
Feel free to open issues or submit pull requests for features like improved NLP models or integration with external job boards!
