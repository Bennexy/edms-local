import json
import sys

from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import ValidationError
from fastapi import FastAPI

sys.path.append(".")

from api.auth import validate_token

from api.config import VERSION

app = FastAPI(docs_url="/", title="Dear Diary", version=VERSION)

from api.routers.files.router import router as file_router
from api.routers.users.router import router as user_router
from api.routers.auth.router import router as auth_router

app.include_router(file_router)
app.include_router(user_router)
app.include_router(auth_router)


@app.get(app.docs_url, include_in_schema=False)
async def custom_swagger_ui_html_github():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        # swagger_ui_dark.css raw url
        swagger_css_url="https://raw.githubusercontent.com/Itz-fork/Fastapi-Swagger-UI-Dark/main/assets/swagger_ui_dark.min.css",
    )


@app.exception_handler(ValidationError)
async def exception_handler(request, exe):
    error = json.loads(exe.json())
    return JSONResponse(
        status_code=422,
        content=error,
        # {
        #     'success': False,
        #     'message': error[0]['msg'],
        #     'error-type': f'ValidationError',
        #     'error': error
        # }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        port=8080,
        reload=True,
        reload_includes="*.py",
        reload_dirs="api/reouters",
    )
