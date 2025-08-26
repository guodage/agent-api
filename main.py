import uvicorn
import ssl
from api.main import app

if __name__ == "__main__":
    # 创建SSL上下文
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    
    # 生成自签名证书（仅用于开发）
    # 你需要先生成证书文件
    ssl_context.load_cert_chain(
        certfile="cert.pem",  # 证书文件
        keyfile="key.pem"     # 私钥文件
    )
    
    # 本地调试配置（HTTPS）
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True,
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem"
    )
