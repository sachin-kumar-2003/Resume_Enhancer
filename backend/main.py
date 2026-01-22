import os
from fastapi import FastAPI, UploadFile,File,  HTTPException
from dotenv import load_dotenv
from openai import OpenAI

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
        return response.choices[0].message   
    except Exception as e:
        raise HTTPException(status_code=500, detail = str(e))
    