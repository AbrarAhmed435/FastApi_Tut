from fastapi import APIRouter
from importlib import import_module
import pkgutil #help to list all python files in folder

router=APIRouter()
""" 
👉 This creates one **main router object** that will collect all routers from your route files.  
This is the one you’ll later attach to the FastAPI app in `main.py`:

```python
from routes import router as api_router
app.include_router(api_router)

"""

for module_info in pkgutil.iter_modules(__path__):
    module_name=module_info.name
    module=import_module(f"{__name__}.{module_name}")
    
    if hasattr(module,"router"): # checks if file defines a variable named "router"
        router.include_router(module.router)
        
        print(f"Included router form :{module_name}")