from flask import Flask, request, jsonify, render_template
import re
from pdfminer.high_level import extract_text_to_fp
from io import StringIO
from docx import Document

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

def parse_resume(file):
    if file.filename.endswith('.pdf'):
        output_string = StringIO()
        extract_text_to_fp(file, output_string)
        return output_string.getvalue()
    elif file.filename.endswith('.docx'):
        doc = Document(file)
        return '\n'.join([para.text for para in doc.paragraphs])
    else:
        return file.read().decode('utf-8')

@app.route('/upload', methods=['POST'])
def upload_resume():
    file = request.files['resume']
    keywords = request.form.get('keywords').split(',')
    keywords = [keyword.strip() for keyword in keywords]

    try:
        content = parse_resume(file)
    except UnicodeDecodeError:
        return jsonify({'error': 'Unable to decode file content'}), 400

    found_keywords = sum(1 for keyword in keywords if re.search(keyword, content, re.IGNORECASE))
    
    total_keywords = len(keywords)
    if total_keywords > 0:
        score = (found_keywords / total_keywords) * 10
    else:
        score = 0

    return jsonify({'score': f'{round(score, 2)}/10'})

if __name__ == '__main__':
    app.run(debug=True)
