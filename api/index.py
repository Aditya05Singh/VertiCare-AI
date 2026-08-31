import sys
import os
import traceback

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)

# Add all relevant search paths for local and AWS Lambda serverless execution
search_paths = [
    root_dir,
    os.path.join(root_dir, "backend"),
    os.path.join(root_dir, "cv"),
    os.path.join(root_dir, "ml"),
    "/var/task",
    "/var/task/backend",
    "/var/task/cv",
    "/var/task/ml"
]

for p in search_paths:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

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
                "sys_path": sys.path,
                "current_dir": current_dir,
                "root_dir": root_dir,
                "root_dir_contents": os.listdir(root_dir) if os.path.exists(root_dir) else [],
                "var_task_contents": os.listdir("/var/task") if os.path.exists("/var/task") else []
            }
        )
    handler = app
