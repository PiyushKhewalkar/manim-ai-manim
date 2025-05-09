from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from manim import config
import subprocess
import os
import uuid
import re
import boto3
from config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    S3_BUCKET_NAME,
)

app = FastAPI()

class CodeInput(BaseModel):
    code: str

def upload_to_s3(file_path, s3_key):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )
    s3.upload_file(file_path, S3_BUCKET_NAME, s3_key)
    return f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"

def extract_scene_class(code: str):
    match = re.search(r"class\s+(\w+)\s*\(\s*Scene\s*\):", code)
    if not match:
        raise HTTPException(status_code=422, detail="No Scene class found in code.")
    return match.group(1)

@app.post("/render-scene/")
async def render_scene(input_data: CodeInput):
    code = input_data.code.strip()
    if not code:
        raise HTTPException(status_code=422, detail="Code input cannot be empty.")

    scene_id = str(uuid.uuid4())[:8]
    file_name = f"Scene_{scene_id}.py"
    file_path = f"/tmp/{file_name}"
    output_dir = "/tmp"

    try:
        with open(file_path, "w") as f:
            f.write(code)

        scene_class = extract_scene_class(code)

        subprocess.run(
            [
                "manim",
                "-pql",
                file_path,
                scene_class,
                "--output_file", f"{scene_id}.mp4",
                "--media_dir", output_dir,
            ],
            check=True,
        )

        # 🧪 Try all possible video paths
        video_dir = os.path.join(output_dir, "videos")
        found_path = None

        for root, _, files in os.walk(video_dir):
            for file in files:
                if file == f"{scene_id}.mp4":
                    found_path = os.path.join(root, file)
                    break

        if not found_path or not os.path.exists(found_path):
            raise HTTPException(status_code=500, detail=f"Rendering succeeded but video file not found. Looked in: {video_dir}")

        s3_key = f"videos/{scene_id}.mp4"
        s3_url = upload_to_s3(found_path, s3_key)

        # Cleanup
        os.remove(file_path)
        os.remove(found_path)

        return {"s3_url": s3_url}

    except subprocess.CalledProcessError as e:
        print("🛑 Subprocess error:", e)
        raise HTTPException(status_code=500, detail=f"Rendering failed: {str(e)}")

    except Exception as e:
        print("🔥 Unexpected error:", e)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
