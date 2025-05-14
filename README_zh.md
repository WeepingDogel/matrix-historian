# Matrix Historian

一个Matrix消息存档和搜索服务。

## 功能特性

- 自动记录Matrix房间的消息历史
- 支持按房间、用户和内容搜索消息
- 提供Web界面进行消息浏览和搜索
- 支持Docker部署
- 使用SQLite数据库存储消息

## 快速开始

### 使用Docker部署

1. 克隆仓库
```bash
git clone https://github.com/yourusername/matrix-historian.git
cd matrix-historian/src
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置Matrix bot账号信息
```

3. 启动服务
```bash
docker-compose up -d
```

服务将在以下端口启动：
- API服务: http://localhost:8001
- Web界面: http://localhost:8502

### 手动配置

参考 `docs/get-started.md` 获取详细的手动配置说明。

## 配置说明

主要配置项：
- `MATRIX_HOMESERVER`: Matrix服务器地址
- `MATRIX_USER`: Bot用户名
- `MATRIX_PASSWORD`: Bot密码

## 使用方法

1. 访问 http://localhost:8502 打开Web界面
2. 使用搜索框搜索消息
3. 使用过滤器按房间或用户筛选消息

## 开发说明

项目结构：
```
src/
├── app/             # 主应用代码
│   ├── api/        # API接口
│   ├── bot/        # Matrix机器人
│   ├── db/         # 数据库模型
│   └── webui/      # Web界面
├── tests/          # 测试代码
└── docker-compose.yml
```

## 许可证

本项目采用 MIT 许可证

[English](README.md)
