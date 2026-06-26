import os
import re
from pypdf import PdfReader
from app.services.storage import add_subject


def parse_timetable(file_path: str):
    subjects_extracted = []
    if file_path.endswith('.txt'):
        with open(file_path, 'r') as f:
            lines = f.readlines()
            subjects_extracted = extract_from_lines(lines)
    elif file_path.endswith('.pdf'):
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    subjects_extracted.extend(extract_from_lines(text.split('\n')))
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return False
    if not subjects_extracted:
        print("No subjects found to parse.")
        return False
    for name, total_classes in subjects_extracted:
        add_subject(name, total_classes)
        
    return True


def extract_from_lines(lines):
    extracted = []
    pattern = re.compile(r'^(.*?)\s*-\s*(\d+)$')
    for line in lines:
        line = line.strip()
        match = pattern.match(line)
        if match:
            subject_name = match.group(1).strip()
            total_classes = int(match.group(2))
            extracted.append((subject_name, total_classes))
    return extracted