import uvicorn
from api.main import app

if __name__ == "__main__":
    # 本地调试配置
    uvicorn.run(
        app,
        host="0.0.0.0",  # 允许外部访问
        port=8001,       # 端口号
        reload=True,     # 开启热重载，代码修改后自动重启
        log_level="info", # 日志级别
        access_log=True   # 显示访问日志
    )
