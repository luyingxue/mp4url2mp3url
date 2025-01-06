from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import moviepy.editor as mpy
from minio import Minio
import os
import tempfile
import requests
from pydantic import BaseModel
from dotenv import load_dotenv
import uuid
import logging

# 加载环境变量
load_dotenv()

app = FastAPI()

# 配置静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# MinIO客户端
minio_client = Minio(
    os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False
)

# 确保bucket存在
bucket_name = os.getenv("MINIO_BUCKET")
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)

class VideoURL(BaseModel):
    url: str

# 在文件开头添加日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/convert")
async def convert_video(video: VideoURL):
    try:
        logger.info(f"开始处理视频: {video.url}")
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 下载视频
            logger.info("开始下载视频...")
            video_path = os.path.join(temp_dir, "video.mp4")
            response = requests.get(video.url)
            with open(video_path, "wb") as f:
                f.write(response.content)
            logger.info("视频下载完成")
            
            # 转换为MP3
            logger.info("开始转换为MP3...")
            audio_path = os.path.join(temp_dir, "audio.mp3")
            video_clip = mpy.VideoFileClip(video_path)
            video_clip.audio.write_audiofile(audio_path)
            video_clip.close()
            logger.info("MP3转换完成")
            
            # 上传到MinIO
            logger.info("开始上传到MinIO...")
            file_name = f"{uuid.uuid4()}.mp3"
            minio_client.fput_object(bucket_name, file_name, audio_path)
            logger.info("上传完成")
            
            # 生成URL
            url = f"http://{os.getenv('MINIO_ENDPOINT')}/{bucket_name}/{file_name}"
            logger.info(f"生成的URL: {url}")
            
            return JSONResponse({"url": url})
            
    except Exception as e:
        logger.error(f"处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Video to Audio Converter API"} 