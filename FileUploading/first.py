from fastapi import FastAPI, File, UploadFile,Form,HTTPException
from fastapi.responses import JSONResponse

app=FastAPI()

@app.post('/upload')
async def upload_file(file:UploadFile=File(...)):
    contents=await file.read() # contents contain full file data in bytes
    size=len(contents) # no. of bytes were read 
    
    return JSONResponse({
        'filename':file.filename,
        'content_type':file.content_type,
        'size':size
    })
    
@app.post('/upload-with-meta/')
async def upload_with_meta(user_id:str=Form(...),description:str=Form(None),file:UploadFile=File(...)):
    content=await file.read()
    
    return {
        "user_id":user_id,
        "description":description,
        "filename":file.filename,
        "size":len(content)
    }


from typing import List

@app.post('/upload-multiple/')
async def upload_multiple(files:List[UploadFile]=File(...)):
    results=[]
    for f in files:
        content=await f.read()
        results.append({"filename":f.filename,"size":len(content)})
    return results


#Multiple Files

import shutil
from fastapi import BackgroundTasks

def save_file_tmp(upload_file:UploadFile,dest_path:str):
    with open(dest_path,'wb') as buffer:
        shutil.copyfileobj(upload_file.file,buffer)
    upload_file.file.close()
    
@app.post('/upload-save/')
async def upload_save(file:UploadFile=File(...),background:BackgroundTasks=None):
    dest=f"uploads/{file.filename}" # saving to uploading folder 
    
    background.add_task(save_file_tmp,file,dest) #Adding save_file_tmp as background task
    
    return {"message":"Saving in background","filename":file.filename}


#PROCESSING PDF CONTENT (PyPDF2)

from PyPDF2 import PdfReader

@app.post('/process-pdf/')
async def process_pdf(file:UploadFile=File(...)):
    contents=await file.read()
    
    from io import BytesIO
    reader=PdfReader(BytesIO(contents))
    
    text=""
    for page in reader.pages:
        text+=page.extract_text() or ""
    return {"filename":file.filename,"page":len(reader.pages),"text_snippet":text[:300]}


# PROCESSING IMAGES (PILLOW) EXAMPLE

from PIL import Image
from io import BytesIO

@app.post('/process-image/')
async def process_image(file:UploadFile=File(...)):
    contents=await file.read()
    img=Image.open(BytesIO(contents))
    width,height=img.size
    
    img.thumbnail((256,256))
    
    buf=BytesIO()
    img.save(buf,format="JPEG")
    thumb_bytes=buf.getvalue()
    return {
        "filename":file.filename,
        "width":width,
        "height":height,
        "thumbnail_size":len(thumb_bytes)
    }
    
    

#VALIDATE FILE TYPES
MAX_FILE_SIZE=10*1024*1024 #10MB

# @app.post('/secure-upload/')
async def secure_upload(file:UploadFile=File(...)):
    
    if file.content_type not in ('application/pdf','image/jpeg','image/png'):
        raise HTTPException(status_code=400,detail="Unsupported file type")
    
    size=0
    chunk=await file.read(1024*1024)
    while chunk:
        size+=len(chunk)
        if size>MAX_FILE_SIZE:
            raise HTTPException(status_code=413,detail="File too large")
        chunk = await file.read(1024*1024)
    await file.seek(0) ## file pointer moved back to begining
    return size
    #then procede
    

### Puting together

from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()

client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def prompt_ai(text:str,retries:int=2):
    import time
    messages=[
        {
            "role":"system",
            "content":"Give short meaningful summary of this text"
        },
        {
        "role":"user",
        "content":f"Here is the text{text}"
        }
    ]
    for attempt in range(retries+1):
        try:
            response=client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
            )
            summary=response.choices[0].message.content 
            return summary
            
            # return JSONResponse(status_code=200,content={
            #     "summary":summary
            # })
        except Exception as e:
            if attempt< retries:
                time.sleep(1)
                continue
            print("OpneAI Error",e)
            
            return f"Error: {str(e)}"

@app.post('/summarize_doc/')
async def summarize_doc(file:UploadFile=File(...)):
    import time
    start=time.time()
    size=await secure_upload(file)
    
    import PyPDF2
    contents=await file.read()
    
    from io import BytesIO
    reader=PdfReader(BytesIO(contents))
    
    # text_chunks=[]
    # for page in reader.pages:
    #     text+=page.extract_text()
    #     if text:
    #         text_chunks.append(text)
    # text=" ".join(text_chunks)
    text_chunks=[page.extract_text() or "" for page in reader.pages]
    text=" ".join(text_chunks) # put space between each chunk
    
    summary=prompt_ai(text)
    summary=summary.strip().replace('\n'," ")
    elapsed=round(time.time()-start,2)
    
    if summary.startswith("Error:"):
        raise HTTPException(status_code=500,detail=summary)
    
    return JSONResponse(status_code=200,content={
        "filename":file.filename,
        "summary":summary,
        "size":size,
        "processing_time":f"{elapsed}s"
    })
    
    
    
    
    
    