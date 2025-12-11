# 数据库工具清单

## MySQL（默认）

| 工具 | 用途 |
|------|------|
| `mcp__mysql__query` | SELECT 查询 |
| `mcp__mysql__describe_table` | 查看表结构 |
| `mcp__mysql__list_tables` | 列出所有表 |

**禁止使用 `mcp__mysql__execute`**，避免数据修改。

## Lindorm

| 工具 | 用途 |
|------|------|
| `mcp__alibaba_cloud_lindorm__lindorm_execute_sql` | SQL 查询（仅 SELECT） |
| `mcp__alibaba_cloud_lindorm__lindorm_show_tables` | 列出所有表 |
| `mcp__alibaba_cloud_lindorm__lindorm_describe_table` | 查看表结构 |

## 使用原则

1. **只读查询**：仅使用 SELECT，禁止 INSERT/UPDATE/DELETE
2. **SQL 聚合优先**：通过 GROUP BY、COUNT、SUM 等直接得出统计结果
3. **控制返回量**：添加 LIMIT 避免大数据量进入上下文
4. **并行查询**：多个独立统计需求可并行发起
