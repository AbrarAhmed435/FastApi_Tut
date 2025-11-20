from fastapi import APIRouter,Depends,UploadFile,File,Form,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.connections import get_async_session
from Models.post import Post
# from schemas.post import Post
import os
import shutil



router=APIRouter(prefix="/posts",tags=["Posts"])

UPLOAD_DIR="uploads"

os.makedirs(UPLOAD_DIR,exist_ok=True)

@router.post("/", status_code=201)
async def create_post(
    title: str = Form(...),
    description: str = Form(None),
    image: UploadFile = File(None),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        image_path = None
        if image:
            # secure path
            file_path = os.path.join(UPLOAD_DIR, image.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            image_path = file_path

        new_post = Post(title=title, description=description, image_path=image_path)
        session.add(new_post)
        await session.commit()
        await session.refresh(new_post)

        return {
            "id": new_post.id,
            "title": new_post.title,
            "description": new_post.description,
            "image_path": new_post.image_path,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    



# @router.post("/")
# def create_post():
#     return {
#         "msg":"post created"
#     }





@router.get("/")
def get_posts():
    return {
        "msg":"List of posts"
    }