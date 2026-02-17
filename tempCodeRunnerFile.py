from flask import Flask, request, redirect, url_for, flash, render_template
import os
from werkzeug.utils import secure_filename
from utils.parser import get_text_from_file
from utils.analyzer import (
    calculate_similarity, 
    identify_missing_skills, 
    get_recommendations,
    calculate_score_breakdown,
    analyze_power_words,
    check_resume_health
)
