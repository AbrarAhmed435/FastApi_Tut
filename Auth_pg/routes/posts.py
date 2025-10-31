from fastapi import APIRouter,Depends,HTTPException,status,File,Form,UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db import get_async_session
from models import Post
from schemas import PostCreate,PostOut
from dependencies import get_current_user

import  shutil
import  os
import  uuid

router=APIRouter(prefix="/posts",tags=["Posts"])

UPLOAD_DIR="uplods"
os.makedirs(UPLOAD_DIR,exist_ok=True)

@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_post(
    title:str=Form(...),
    description:str=Form(...),
    image:UploadFile=File(...),
    session:AsyncSession=Depends(get_async_session),
    current_user=Depends(get_current_user)   
):
    #generate a unique file name
    file_ext=os.path.splitext(image.filename)[1] #get extension(jpg,png)
    unique_filename=f"{uuid.uuid4()}{file_ext}"
    file_path=os.path.join(UPLOAD_DIR,unique_filename)
    
    #save uploaded images locally
    try:
        with open(file_path,"wb") as buffer:
            shutil.copyfileobj(image.file,buffer)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error saving file: {str(e)}")
    
    post=Post(
        title=title,
        description=description,
        image_url=file_path,
        user_id=current_user.id
    )
    
    session.add(post)
    await session.commit()
    await session.refresh(post)
    
    return {
        "id":post.id,
        "title":post.title,
        "description":post.description,
        "image_url":post.image_url,
        "user_id":post.user_id,
        "created_at":post.created_at
    }    


# router=APIRouter(prefix="/posts",tags=["Posts"])

# @router.post("/",response_model=PostOut)
# async def create_post(post_in:PostCreate,session=Depends(get_async_session),current_user=Depends(get_current_user)):
#     post=Post(**post_in.dict(),user_id=current_user.id)
#     session.add(post)
#     await session.commit()
#     await session.refresh(post)
    
#     return post

# @router.get("/",response_class=list[PostOut])
# async def get_my_posts(session:AsyncSession=Depends(get_async_session),current_user=Depends(get_current_user)): #AsyncSession is type hinting
#     q=select(Post).where(Post.user_id==current_user.id)
#     result=await q.execute(q)
#     posts =result.scalares().all()
#     return posts