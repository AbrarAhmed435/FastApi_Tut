from fastapi import FastAPI, File, UploadFile,Form
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
