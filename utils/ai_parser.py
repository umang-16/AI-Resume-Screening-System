import os
import re
from PyPDF2 import PdfReader # pyre-ignore

# A broad set of standard IT/Tech skills for matching
STANDARD_SKILLS = {
    'python', 'java', 'c++', 'javascript', 'html', 'css', 'react', 'angular', 'vue',
    'node.js', 'express', 'flask', 'django', 'sql', 'mysql', 'postgresql', 'mongodb',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'github', 'agile', 'scrum',
    'machine learning', 'deep learning', 'nlp', 'data structures', 'algorithms',
    'linux', 'bash', 'ruby', 'php', 'swift', 'kotlin', 'c#', '.net', 'api',
    'rest', 'graphql', 'bootstrap', 'tailwind', 'sqlite', 'pandas', 'numpy', 'spacy',
    'communication', 'leadership', 'teamwork', 'problem solving'
}

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + " "
        return text.lower()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def extract_skills_from_text(text):
    """
    Extract skills by checking against a predefined set of skills.
    Returns a comma-separated string of matched skills.
    """
    if not text:
        return ""
        
    words = set(re.findall(r'\b\w+\b', text.lower()))
    found_skills = set()
    
    # Simple word matching
    for word in words:
        if word in STANDARD_SKILLS:
            found_skills.add(word)
            
    # Check for multi-word or special character skills
    for skill in STANDARD_SKILLS:
        if " " in skill or "." in skill or "+" in skill or "#" in skill:
            if skill in text.lower():
                found_skills.add(skill) # pyre-ignore
                
    return ", ".join(list(found_skills))

def match_skills(resume_skills_str, required_skills_str):
    """
    Compare extracted resume skills against required skills
    and return a matching percentage.
    """
    if not required_skills_str or not resume_skills_str:
        return 0.0
        
    req_skills = set([s.strip().lower() for s in required_skills_str.split(',') if s.strip()])
    res_skills = set([s.strip().lower() for s in resume_skills_str.split(',') if s.strip()])
    
    if not req_skills:
        return 0.0
        
    match_count = len(req_skills.intersection(res_skills))
    score = (match_count / len(req_skills)) * 100
    return round(score, 2) # pyre-ignore
