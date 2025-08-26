
首次docker构建前，需要生成证书
```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 3650 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```
Linux：
```bash
docker-compose down && docker-compose build --no-cache && docker-compose up -d
```

MacOS:
可能新版需要去掉-。
```bash
docker compose down && docker compose build --no-cache && docker compose up -d
```
