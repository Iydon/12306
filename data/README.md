# 步骤
## 创建用户及数据库
```sql
create role checker superuser password '123456' login;
create database project_2;
```

## 登录数据库导入数据（PostgreSQL）
```shell
7z x sql.7z
psql project_2 -f main.sql
psql project_2 -f seat_type.sql
psql project_2 -f capacity.sql
psql project_2 -f city.sql
psql project_2 -f station.sql
psql project_2 -f journey.sql
psql project_2 -f district.sql
```
