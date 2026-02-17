try:
    import spacy
    # Load English NLP model
    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        # If model not found, user will need to run: python -m spacy download en_core_web_sm
        nlp = None
except ImportError:
    nlp = None

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from collections import Counter

def preprocess_text(text):
    if not text:
        return ""
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    
    if nlp:
        doc = nlp(text)
        # Remove stopwords and lemmatize
        tokens = [token.lemma_ for token in doc if not token.is_stop]
        return " ".join(tokens)
    return text

def calculate_similarity(resume_text, jd_text):
    processed_resume = preprocess_text(resume_text)
    processed_jd = preprocess_text(jd_text)
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([processed_resume, processed_jd])
    
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return round(similarity[0][0] * 100, 2)

def calculate_score_breakdown(missing_skills, current_score):
    # Heuristic: Distribute the remaining potential score among missing skills
    potential_gain = 100 - current_score
    breakdown = []
    
    if not missing_skills:
        return []
        
    # Cap the gain per skill to avoid unrealistic promises
    gain_per_skill = min(potential_gain / len(missing_skills), 15) 
    
    for skill in missing_skills:
        breakdown.append({
            'skill': skill,
            'impact': round(gain_per_skill, 1),
            'action': f"Integrate '{skill}' into your experience section."
        })
    return breakdown

ACTION_VERBS = [
    'architected', 'engineered', 'spearheaded', 'orchestrated', 'pioneered', 
    'deployed', 'optimized', 'scaled', 'accelerated', 'revamped', 
    'modernized', 'automated', 'implemented', 'designed', 'developed',
    'managed', 'led', 'created', 'built', 'resolved'
]

STOPWORDS = {
    'a','an','the','and','or','but','if','then','else','when','at','by','for','in','of','on','to','with','as','from','into',
    'is','are','was','were','be','been','being','it','its','this','that','these','those','i','you','he','she','they','we',
    'my','your','his','her','their','our','me','him','them','us','not','no','yes','do','does','did','done','have','has','had',
    'will','would','can','could','should','may','might','must','about','over','under','more','most','less','least','very','than'
}

def analyze_power_words(text):
    text = text.lower()
    found_verbs = []
    for verb in ACTION_VERBS:
        if re.search(r'\b' + re.escape(verb) + r'\b', text):
            found_verbs.append(verb)
    return len(found_verbs), found_verbs

def check_resume_health(text):
    health_score = 100
    issues = []
    
    # Check for Contact Info
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'\b(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b'
    
    if not re.search(email_pattern, text):
        health_score -= 20
        issues.append("Missing Email Address")
        
    # Basic phone check (might need more robust regex for intl numbers)
    # if not re.search(r'\d{10}', text): # Simplified check
        # health_score -= 10
        # issues.append("Phone number might be missing or unclear")

    # Check for Sections
    sections = ['experience', 'education', 'skills', 'projects']
    text_lower = text.lower()
    for section in sections:
        if section not in text_lower:
            health_score -= 10
            issues.append(f"Missing '{section.title()}' section")
            
    return max(0, health_score), issues

def tokenize(text):
    if not text:
        return []
    tokens = re.findall(r"[a-zA-Z][a-zA-Z+.#-]{1,}", text.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) > 2]

def get_top_keywords(text, limit=12):
    tokens = tokenize(text)
    if not tokens:
        return []
    counts = Counter(tokens)
    return [word for word, _ in counts.most_common(limit)]

def analyze_resume_stats(text):
    if not text:
        return {
            'word_count': 0,
            'char_count': 0,
            'sentence_count': 0,
            'avg_words_per_sentence': 0,
            'bullet_count': 0
        }

    words = re.findall(r"\b\w+\b", text)
    sentences = re.split(r"[.!?]+", text)
    sentences = [s for s in sentences if s.strip()]
    bullet_count = sum(1 for line in text.splitlines() if re.match(r"^\s*[•\-*]\s+", line))

    sentence_count = len(sentences)
    word_count = len(words)
    avg_words = round(word_count / sentence_count, 1) if sentence_count else 0

    return {
        'word_count': word_count,
        'char_count': len(text),
        'sentence_count': sentence_count,
        'avg_words_per_sentence': avg_words,
        'bullet_count': bullet_count
    }

def analyze_section_coverage(text):
    sections = ['summary', 'experience', 'education', 'skills', 'projects', 'certifications', 'achievements']
    text_lower = (text or "").lower()
    present = [s for s in sections if s in text_lower]
    missing = [s for s in sections if s not in text_lower]
    coverage = round((len(present) / len(sections)) * 100) if sections else 0
    return {
        'present': present,
        'missing': missing,
        'coverage': coverage
    }

def calculate_keyword_coverage(resume_text, jd_text):
    jd_keywords = set(get_top_keywords(jd_text, limit=15))
    if not jd_keywords:
        return {
            'coverage': 0,
            'matched': [],
            'missing': []
        }

    resume_tokens = set(tokenize(resume_text))
    matched = sorted([k for k in jd_keywords if k in resume_tokens])
    missing = sorted([k for k in jd_keywords if k not in resume_tokens])
    coverage = round((len(matched) / len(jd_keywords)) * 100)
    return {
        'coverage': coverage,
        'matched': matched,
        'missing': missing
    }

def calculate_ats_readiness(health_score, missing_skills, stats):
    base = health_score
    if stats.get('word_count', 0) < 200:
        base -= 10
    if stats.get('word_count', 0) > 1000:
        base -= 8
    if stats.get('bullet_count', 0) < 3:
        base -= 6
    if missing_skills:
        base -= min(20, len(missing_skills) * 2)
    return max(0, min(100, base))

def build_action_checklist(health_issues, missing_skills, stats, section_coverage):
    actions = []

    for issue in health_issues:
        actions.append(issue)

    if stats.get('word_count', 0) < 200:
        actions.append("Resume is too short; aim for 250–700 words.")
    if stats.get('word_count', 0) > 1000:
        actions.append("Resume is long; trim to key impact statements.")
    if stats.get('bullet_count', 0) < 3:
        actions.append("Add bullet points under experience/projects.")

    if section_coverage.get('missing'):
        missing_sections = ", ".join([s.title() for s in section_coverage['missing']])
        actions.append(f"Consider adding sections: {missing_sections}.")

    if missing_skills:
        actions.append("Add missing skills into experience/project bullets where relevant.")

    return actions

def extract_skills(text):
    # Expanded skill set with lower case for matching
    skill_set = set(SKILL_DB.keys())
    
    found_skills = []
    text = text.lower()
    
    # Simple keyword matching execution
    # In a real app, use Spacy's PhraseMatcher for better performance/accuracy
    for skill in skill_set:
        # Check for word boundaries to avoid partial matches (e.g. "java" in "javascript")
        # Escaping regex special characters in skill names (like c++)
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text):
            found_skills.append(skill)
            
    return set(found_skills)

def identify_missing_skills(resume_text, jd_text):
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    
    missing_skills = jd_skills - resume_skills
    return list(missing_skills)

def get_recommendations(missing_skills):
    recommendations = []
    for skill in missing_skills:
        if skill in SKILL_DB:
            rec = SKILL_DB[skill]
            rec['name'] = skill.title() # Add display name
            recommendations.append(rec)
    return recommendations

# Knowledge Base
SKILL_DB = {
    'python': {
        'resources': ['Python.org', 'Real Python', 'Automate the Boring Stuff'],
        'tips': 'Focus on data structures, lists, dictionaries, and list comprehensions.',
        'interview': 'Explain the difference between list and tuple. What is a decorator?'
    },
    'java': {
        'resources': ['Oracle Java Docs', 'Baeldung', 'Spring Academy'],
        'tips': 'Understand OOP concepts: Inheritance, Encapsulation, Polymorphism.',
        'interview': 'Difference between equals() and ==? What is the contract between hashCode and equals?'
    },
    'javascript': {
        'resources': ['MDN Web Docs', 'Javascript.info', 'Egghead.io'],
        'tips': 'Master ES6+ syntax, Promises, Async/Await, and the Event Loop.',
        'interview': 'Explain closures and hoisting. What is the difference between let, const, and var?'
    },
    'react': {
        'resources': ['React Official Docs', 'Kent C. Dodds Blog'],
        'tips': 'Learn Hooks (useState, useEffect), Component lifecycle, and State Management.',
        'interview': 'What is the Virtual DOM? Explain the useEffect dependency array.'
    },
    'sql': {
        'resources': ['Mode SQL Tutorial', 'W3Schools SQL'],
        'tips': 'Practice JOINS, GROUP BY, subqueries, and Window functions.',
        'interview': 'Difference between INNER JOIN and LEFT JOIN? How to optimize a slow query?'
    },
    'docker': {
        'resources': ['Docker Docs', 'Docker Mastery (Udemy)'],
        'tips': 'Understand Images vs Containers, Dockerfile commands, and Docker Compose.',
        'interview': 'What are different Docker networking drivers? How to minimize image size?'
    },
    'kubernetes': {
        'resources': ['Kubernetes.io', 'KubeAcademy'],
        'tips': 'Learn Pods, Services, Deployments, and ConfigMaps.',
        'interview': 'What is a Pod? Explain the difference between ReplicaSet and Deployment.'
    },
    'aws': {
        'resources': ['AWS Documentation', 'A Cloud Guru'],
        'tips': 'Focus on core services: EC2, S3, RDS, IAM, and Lambda.',
        'interview': 'Difference between S3 and EBS? What is IAM Role vs User?'
    },
    'machine learning': {
        'resources': ['Fast.ai', 'Coursera Andrew Ng'],
        'tips': 'Understand supervised vs unsupervised learning, overfitting/underfitting.',
        'interview': 'Explain the Bias-Variance tradeoff. How do you handle imbalanced datasets?'
    },
    'git': {
        'resources': ['Git SCM Book', 'GitHub Guides'],
        'tips': 'Master add, commit, push, pull, merge, and rebase.',
        'interview': 'Difference between merge and rebase? How to resolve a merge conflict?'
    },
    'flask': {
        'resources': ['Flask Mega-Tutorial', 'Flask Docs'],
        'tips': 'Understand Application Context, Blueprints, and SQLAlchemy integration.',
        'interview': 'How does Flask handle requests? What are Flask signals?'
    },
    'c++': {
        'resources': ['LearnCpp.com', 'C++ Reference'],
        'tips': 'Master pointers, memory management, and STL.',
        'interview': 'What is a virtual destructor? Explain RAII.'
    },
    'html': {
        'resources': ['MDN HTML'],
        'tips': 'Semantic HTML, Accessibility (a11y), forms.',
        'interview': 'What is the difference between span and div? Explain doctype.'
    },
    'css': {
        'resources': ['MDN CSS', 'CSS-Tricks'],
        'tips': 'Flexbox, Grid, Box Model, Specificity.',
        'interview': 'Explain the box model. Difference between rem, em, px?'
    }
}
