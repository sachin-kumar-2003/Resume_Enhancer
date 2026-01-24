import os
from fastapi import FastAPI, Form, UploadFile,File,  HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
from docx import Document
import tempfile
import shutil
from system_prompts import job_description_system_prompt, resume_system_prompt


load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



api_key = os.getenv("GEMINI_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

@app.get("/")
def home():
    return {"message":"welcome to the backend"}

@app.get("/resume.tex")
def get_resume_template():
    return {"template": open("resume.tex", "r").read()}

required_skills = ""





@app.post("/upload")
async def upload_resume(resume : UploadFile = File(...), job_description: str = Form(...)):
    if len(job_description) < 10:
        raise HTTPException(status_code= 400, detail="please upload valid job description")
    
    if not resume.filename.endswith(('.pdf', '.docx')):
        raise HTTPException(status_code = 400, detail="please upload pdf or docx file only")
    
    
    
    try:
        with tempfile.TemporaryFile(delete=False) as temp:
            shutil.copyfileobj(resume.file, temp)
            temp_path = temp.name
            
            parsed_text = ""
            if resume.filename.endswith('.pdf'):
                def check_len(path):
                    reader = PdfReader(path)
                    return len(reader.pages)
                if check_len(temp_path) > 2:
                    raise HTTPException(status_code= 400, detail="pdf file is too large")  
                
                reader = PdfReader(temp_path)
                for i in range(check_len(temp_path)):
                    page = reader.pages[i]
                    parsed_text += page.extract_text()
                          
            elif resume.filename.endswith('.docx'):
                                
                reader = Document(temp_path)
                for para in reader.paragraphs:
                    parsed_text += para.text
                    
                words = parsed_text.split()
                if (len(words) // 450) + 1 > 2:
                    raise HTTPException(status_code= 400, detail="docx file is too large")
            
            
            response = client.chat.completions.create(
                model= "gemini-3-flash-preview",
                messages = [
                    {
                        "role": "system",
                        "content": job_description_system_prompt                        
                    }, 
                    {
                        "role": "user",
                        "content" : job_description
                    }, 
                    {
                        "role": "system",
                        "content": resume_system_prompt
                    },
                    {
                        "role": "user",
                        "content": parsed_text
                    }
                ]
            )
            print(response.choices[0].message.content)
            return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code= 500, detail="something went wrong")