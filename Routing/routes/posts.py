from fastapi import APIRouter

router=APIRouter(prefix="/posts",tags=["Posts"])

@router.get("/")
def get_posts():
    return {
        "msg":"List of posts"
    }
    

@router.post("/")
def create_post():
    return {
        "msg":"post created"
    }