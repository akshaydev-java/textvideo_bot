from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import os
from pathlib import Path
from .generator import VideoGenerator

app = FastAPI(title='AnimateDiff API')

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Initialize generator (Global instance to keep model in memory)
generator = VideoGenerator()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "database" / "videos.db"

class GenerationRequest(BaseModel):
    prompt: str

@app.get('/')
def read_root():
    return {'message': 'AnimateDiff API is running'}

@app.post('/generate-video')
async def generate_video(request: GenerationRequest):
    try:
        # 1. Generate video
        video_path = generator.generate(prompt=request.prompt)
        
        # 2. Store in database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO generated_videos (prompt, video_path) VALUES (?, ?)',
            (request.prompt, video_path)
        )
        conn.commit()
        conn.close()
        
        return {"video_path": video_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/history')
async def get_history():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT id, prompt, video_path, created_at FROM generated_videos ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))