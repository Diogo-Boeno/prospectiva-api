#!/bin/bash
# Terminal 1 — backend
source venv/Scripts/activate
cd backend
uvicorn main:app --reload &

# Terminal 2 — frontend
cd ../frontend
python -m http.server 3000