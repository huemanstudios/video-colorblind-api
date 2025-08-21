# Video Colorblind Filter API (FFmpeg + FastAPI)

A tiny API you can deploy to Render. It accepts a video upload and returns a filtered MP4 simulating
**protanopia**, **deuteranopia**, or **tritanopia** using `ffmpeg`'s `colorchannelmixer`.

## Endpoints

- `GET /` — health check
- `POST /process-video`
  - **Body**: `multipart/form-data` with `file` = your video
  - **Query params**:
    - `filter`: `protanopia` | `deuteranopia` | `tritanopia` | `identity` (default `protanopia`)
    - `crf` (int 18–32, default 23): quality (lower = better/larger)
    - `preset` (string, default `veryfast`): x264 speed (e.g., ultrafast, superfast, veryfast, faster, fast, medium)

Returns `video/mp4` directly.

## Deploy on Render

1. **Fork or push** this repo to your GitHub.
2. In **Render Dashboard → New → Web Service →** pick this repo.
3. Render detects `render.yaml` and uses the Dockerfile automatically.
4. When deploy finishes you’ll get a URL like:
   `https://video-colorblind-api.onrender.com`
5. Test locally (optional): `docker build -t vcf . && docker run -p 10000:10000 vcf`

## FlutterFlow Setup

Create an **API Call**:
- **Method**: `POST`
- **URL**: `https://<your-service>.onrender.com/process-video?filter=protanopia`
- **Body**: `multipart/form-data`
  - **Field name**: `file`
  - **Value**: your `Uploaded File (Bytes)` variable (e.g., `Uploaded Local File_mediaUpload`)
- **Headers**: none required.

**Response handling**:
- Because the API returns the processed MP4 file directly, in FlutterFlow set the
  API call to expect **Binary** response (File), then bind that to a local file and
  feed it to a **VideoPlayer** or present a download action. If your plan/UI prefers a URL,
  swap the API to return JSON + temporary link (easy to add later).

## Notes

- These matrices are **approximations** appropriate for an MVP. For Daltonization-grade accuracy,
  you can swap the filter to a LUT (`-vf lut3d=...`) or implement frame-by-frame processing.
- Max video length: keep short (e.g., < 20s) for free-tier CPU. Use `preset=superfast` if needed.
