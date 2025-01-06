# MP4转MP3转换服务

## 项目说明
一个简单的微服务，提供MP4视频转换为MP3音频的功能。通过RESTful API接收视频URL，返回转换后的音频URL。

## 功能特点
- 支持MP4视频转换为MP3音频
- RESTful API接口
- 异步任务处理
- MinIO对象存储
- 任务状态查询

## 文件结构



## 运行项目

uvicorn main:app --reload
访问 http://localhost:8000/static/index.html 查看web界面