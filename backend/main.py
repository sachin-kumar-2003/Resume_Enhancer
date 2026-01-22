import os
from fastapi import FastAPI, UploadFile,File,  HTTPException
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
from docx import Document
import tempfile
import shutil

from system_prompts import job_description_system_prompt, resume_system_prompt
load_dotenv()

app = FastAPI()

api_key = os.getenv("GEMINI_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

@app.get("/")
def home():
    return {"message":"welcome to the backend"}

required_skills = ""

@app.post("/upload/job-description")
async def post_job_description(file: UploadFile = File(...)):
    
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code= 400, detail= "only text file allowed")    
    
    data = await file.read()
    try:
        job_description = data.decode('utf-8')
        
        if len(job_description) < 10:
            raise HTTPException(status_code= 500, detail= "length of job description small")
        
        response = client.chat.completions.create(
            model= "gemini-3-flash-preview",
            messages=[
                {
                    "role":"system",
                    "content":job_description_system_prompt
                },
                {
                    "role": "user",
                    "content":job_description
                }
            ]
        )  
        required_skills = response.choices[0].message.content
        return response.choices[0].message.content 
    except Exception as e:
        raise HTTPException(status_code=500, detail = str(e))



@app.post("/upload/upload_resume")
async def upload_resume(file : UploadFile = File(...)):
    if not file.filename.endswith(('.pdf', '.docx')):
        raise HTTPException(status_code = 400, detail="please upload pdf or docx file only")
    
    
    
    try:
        with tempfile.TemporaryFile(delete=False) as temp:
            shutil.copyfileobj(file.file, temp)
            temp_path = temp.name
            
            parsed_text = ""
            if file.filename.endswith('.pdf'):
                def check_len(path):
                    reader = PdfReader(path)
                    return len(reader.pages)
                if check_len(temp_path) > 2:
                    raise HTTPException(status_code= 400, detail="pdf file is too large")  
                
                reader = PdfReader(temp_path)
                for i in range(check_len(temp_path)):
                    page = reader.pages[i]
                    parsed_text += page.extract_text()
                          
            elif file.filename.endswith('.docx'):
                def check_len(path):
                    reader = Document(path)
                    return reader.core_properties.pages
                if check_len(temp_path) is None or check_len(temp_path) > 2:
                    raise HTTPException(status_code= 400, detail = "docx file too large")
                
                reader = Document(temp_path)
                for para in reader.paragraphs:
                    parsed_text += para.text
            
            
            response = client.chat.completions.create(
                model= "gemini-3-flash-preview",
                messages = [
                    {
                        "role": "system",
                        "content": resume_system_prompt                        
                    }, 
                    {
                        "role": "user",
                        "content" : parsed_text
                    }
                ]
            )
            return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code= 500, detail="something went wrong")
        