import os
import shutil
import subprocess
import uuid

from fastapi import FastAPI, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTasks
from fastapi.staticfiles import StaticFiles

from filters import ffmpeg_matrix_for

app = FastAPI(title="Video Colorblind Filter API", version="1.0.0")

# Allow FlutterFlow (or any client) to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TMP_DIR = "/tmp"  # Render's ephemeral storage

# ✅ Serve /tmp files under /files
app.mount("/files", StaticFiles(directory=TMP_DIR), name="files")


def cleanup_paths(*paths):
    """Delete temporary files after request finishes."""
    for p in paths:
        try:
            if os.path.isfile(p):
                os.remove(p)
        except Exception:
            pass


@app.post("/process-video")
async def process_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    filter: str = Query("protanopia", regex="^(protanopia|deuteranopia|tritanopia|identity)$"),
    crf: int = Query(23, ge=18, le=32),  # quality setting (lower = better)
    preset: str = Query("veryfast")      # x264 speed/size tradeoff
):
    """
    Accepts a video via multipart/form-data and returns JSON with a URL to the processed MP4. 
    Query param `filter`: protanopia | deuteranopia | tritanopia | identity
    """

    # Save uploaded video
    uid = uuid.uuid4().hex
    in_path = os.path.join(TMP_DIR, f"in_{uid}_{file.filename or 'video'}.bin")
    out_path = os.path.join(TMP_DIR, f"out_{uid}.mp4")

    with open(in_path, "wb") as buf:
        shutil.copyfileobj(file.file, buf)

    # Build ffmpeg filter
    ccm = ffmpeg_matrix_for(filter)
    vf = ccm if ccm else "null"

    cmd = [
        "ffmpeg", 
        "-y",
        "-i", in_path,
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", preset,
        "-crf", str(crf),
        "-movflags", "+faststart",
        "-c:a", "copy",
        out_path,
    ]

    # Run ffmpeg
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        err = e.stderr.decode("utf-8", errors="ignore")
        cleanup_paths(in_path)
        return {"ok": False, "error": "ffmpeg_failed", "detail": err[:4000]}

    # Schedule cleanup of temp files
    background_tasks.add_task(cleanup_paths, in_path, out_path)

    # ✅ Return URL instead of raw file
    base_url = os.getenv("BASE_URL", "https://video-colorblind-api.onrender.com")
    file_url = f"{base_url}/files/{os.path.basename(out_path)}"
    return JSONResponse({"url": file_url})


@app.get("/")
def root():
    return {"status": "ok", "message": "Use POST /process-video (multipart/form-data)"}








# import os
# import shutil
# import subprocess
# import uuid
# from typing import Optional

# from fastapi import FastAPI, File, UploadFile, Query
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse
# from starlette.background import BackgroundTasks

# from filters import ffmpeg_matrix_for

# app = FastAPI(title="Video Colorblind Filter API", version="1.0.0")

# # CORS so FlutterFlow can call directly
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # tighten later
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# TMP_DIR = "/tmp"  # ephemeral is fine on Render

# def cleanup_paths(*paths):
#     for p in paths:
#         try:
#             if os.path.isfile(p):
#                 os.remove(p)
#         except Exception:
#             pass

# @app.post("/process-video")
# async def process_video(
#     background_tasks: BackgroundTasks,
#     file: UploadFile = File(...),
#     filter: str = Query("protanopia", regex="^(protanopia|deuteranopia|tritanopia|identity)$"),
#     crf: int = Query(23, ge=18, le=32),         # quality setting (lower = better)
#     preset: str = Query("veryfast")             # x264 speed/size tradeoff
# ):
#     """
#     Accepts a video via multipart/form-data and returns the processed MP4.
#     Query param `filter`: protanopia | deuteranopia | tritanopia | identity
#     """

#     # Save upload
#     uid = uuid.uuid4().hex
#     in_path = os.path.join(TMP_DIR, f"in_{uid}_{file.filename or 'video'}.bin")
#     out_path = os.path.join(TMP_DIR, f"out_{uid}.mp4")

#     with open(in_path, "wb") as buf:
#         shutil.copyfileobj(file.file, buf)

#     # Build FFmpeg command
#     ccm = ffmpeg_matrix_for(filter)  # e.g. "colorchannelmixer=..."
#     vf = ccm if ccm else "null"

#     cmd = [
#         "ffmpeg",
#         "-y",
#         "-i", in_path,
#         "-vf", vf,
#         "-c:v", "libx264",
#         "-preset", preset,
#         "-crf", str(crf),
#         "-movflags", "+faststart",
#         "-c:a", "copy",
#         out_path,
#     ]

#     # Run FFmpeg
#     try:
#         proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
#     except subprocess.CalledProcessError as e:
#         # surface error details to help debugging
#         err = e.stderr.decode("utf-8", errors="ignore")
#         cleanup_paths(in_path)
#         return {"ok": False, "error": "ffmpeg_failed", "detail": err[:4000]}

#     # Schedule cleanup of temp files AFTER response is sent
#     background_tasks.add_task(cleanup_paths, in_path, out_path)

#     # Return the processed file directly
#     # return FileResponse(
#     #     path=out_path,
#     #     filename=f"filtered_{filter}.mp4",
#     #     media_type="video/mp4",
#     # )
#     BASE_URL = os.getenv("BASE_URL", "https://video-colorblind-api.onrender.com")

#     @app.post("/process-video")
#     async def process_video(...):
#         ...
#         # instead of returning FileResponse
#         file_url = f"{BASE_URL}/files/{os.path.basename(out_path)}"
#         return JSONResponse({"url": file_url})

# @app.get("/")
# def root():
#     return {"status": "ok", "message": "Use POST /process-video (multipart/form-data)"}
