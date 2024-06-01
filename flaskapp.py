from flask import Flask, request, render_template
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv

# .env dosyasından API anahtarını yükle
load_dotenv()

# Google API anahtarını yapılandır
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Flask uygulaması oluştur
app = Flask(__name__)

# PDF dosyasından metin çıkarma işlevi
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Google Gemini yanıtını alma işlevi
def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

# Ana sayfa ve form işleme
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Formdan alınan iş tanımı ve yüklenen dosya
        jd = request.form["jd"]
        uploaded_file = request.files["resume"]
        
        if uploaded_file:
            # PDF dosyasından metin çıkarma
            text = input_pdf_text(uploaded_file)
            
            # GPT-4 ile etkileşim için hazırlanan giriş komutu
            input_prompt = f"""
            Hey Act Like a skilled or very experienced ATS(Application Tracking System)
            with a deep understanding of tech field, software engineering, data science, data analyst
            and big data engineer. Your task is to evaluate the resume based on the given job description.
            You must consider the job market is very competitive and you should provide 
            best assistance for improving the resumes. Assign the percentage Matching based 
            on Jd and the missing keywords with high accuracy
            resume:{text}
            description:{jd}

            I want the response in one single string having the structure
            {{"JD Match":"%","MissingKeywords:[]","Profile Summary":""}}
            """

            # Google Gemini API'den yanıt alma
            response = get_gemini_response(input_prompt)
            
            # Sonucu render template ile sayfaya gönder
            return render_template("index.html", response=response)
    
    # GET isteği olduğunda veya POST isteği başarısız olduğunda ana sayfa render edilir
    return render_template("index.html", response=None)

# Flask uygulamasını çalıştır
if __name__ == "__main__":
    app.run(debug=True)
