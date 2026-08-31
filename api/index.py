import sys
import os

# Ensure backend, cv, and ml directories are on python sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for module_name in ["backend", "cv", "ml"]:
    module_path = os.path.join(root_dir, module_name)
    if module_path not in sys.path:
        sys.path.insert(0, module_path)

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.main import app

# Export handler for ASGI serverless runtime
handler = app
