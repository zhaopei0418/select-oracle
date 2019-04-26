# 安装依懒
```
pip install -r requirements.txt
```

## 自定义proto文件，修改protos/select.proto

## 重新生成执行
```
python -m grpc_tools.protoc -Iprotos --python_out. --grpc_python_out=. protos/select.proto
```

## 可配置的环境变量,没有配置用默认的
```
SELECT_MAX_WORKERS 最大工作者,默认20 
SELECT_PORT 监听端口号, 默认 50051
SELECT_USER_NAME 数据库用户名, 默认orcl
SELECT_PASSWORD 数据库密码, 默认orcl
SELECT_DATABASE_URL 数据库地址, 默认:127.0.0.1:1521/orcl
```

## 修改select_oracle.py 启动服务python select_oracle.py
