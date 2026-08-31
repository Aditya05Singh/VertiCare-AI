import sys
import os
import traceback

# Ensure backend, cv, and ml directories are on python sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)

for module_name in ["backend", "cv", "ml", ""]:
    module_path = os.path.join(root_dir, module_name) if module_name else root_dir
    if module_path not in sys.path:
        sys.path.insert(0, module_path)

try:
    from app.main import app
    handler = app
except Exception as e:
    err_msg = traceback.format_exc()
    print(f"Error loading FastAPI app: {err_msg}", file=sys.stderr)
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    app = FastAPI()
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
    async def fallback_handler(path: str):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Backend initialization failed",
                "exception": str(e),
                "traceback": err_msg,
                "sys_path": sys.path
            }
        )
    handler = app
