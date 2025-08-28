

Linux：
```bash
docker-compose down && docker-compose build --no-cache && docker-compose up -d
```

MacOS:
可能新版需要去掉-。
```bash
docker compose down && docker compose build --no-cache && docker compose up -d
```

git ssh代理
~/.ssh/config
```text
Host github.com
    Hostname github.com
    Port 22
    User git
    ProxyCommand nc -x 192.168.1.233:1080 %h %p
```
