import json
import sys

from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import ValidationError
from fastapi import FastAPI

sys.path.append(".")

from api.auth import validate_token  # noqa: F401

from api.config import VERSION

app = FastAPI(docs_url="/", title="EDMS", version=VERSION)

from api.routers.process.router import router as file_router  # noqa: E402
from api.routers.process_v2.router import router as process_v2_router  # noqa: E402
from api.routers.users.router import router as user_router  # noqa: E402
from api.routers.auth.router import router as auth_router  # noqa: E402
from api.routers.ocr.router import router as ocr_router  # noqa: E402

app.include_router(process_v2_router)
app.include_router(file_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(ocr_router)


@app.get(app.docs_url, include_in_schema=False)
async def custom_swagger_ui_html_github():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        # swagger_ui_dark.css raw url
        swagger_css_url="https://raw.githubusercontent.com/Itz-fork/Fastapi-Swagger-UI-Dark/main/assets/swagger_ui_dark.min.css",
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exe):
    error = json.loads(exe.json())
    return JSONResponse(
        status_code=422,
        content=error,
    )


@app.exception_handler(Exception)
async def exception_handler(request, exe: Exception):
    error = exe.__str__()
    return JSONResponse(
        status_code=500,
        content=error,
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
