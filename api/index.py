import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)

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

from app.main import app
