# 贡献指南

感谢你对 Data Insight Agent 的关注！欢迎提交 Issue 和 Pull Request。

## 行为准则

- 尊重他人，友善交流
- 聚焦技术讨论
- 接受建设性反馈

## 如何贡献

### 报告问题

1. 检查 [已有 Issue](https://github.com/shanggqm/data-insight-agent/issues) 避免重复
2. 使用清晰的标题描述问题
3. 提供复现步骤和环境信息

### 提交 Pull Request

1. Fork 仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 创建 Pull Request

### PR 规范

- 标题清晰描述改动
- 描述中说明改动原因和影响
- 确保代码风格一致
- 如有必要，更新文档

## 开发环境

### 设置

```bash
# 克隆仓库
git clone https://github.com/shanggqm/data-insight-agent.git
cd data-insight-agent

# 安装依赖
./scripts/setup.sh
```

### 项目结构

```
.claude/skills/data-analysis/   # Skill 定义
mcp/mcp-mysql-server/           # MySQL MCP Server
docs/                           # 文档
scripts/                        # 脚本
```

## 贡献方向

### 文档改进

- 修正错误
- 补充示例
- 翻译

### 功能增强

- 新的分析方法模板
- 报告模板优化
- MCP Server 改进

### Bug 修复

- 修复已知问题
- 改进错误处理

## 提交信息规范

```
<type>: <description>

[optional body]

[optional footer]
```

Type:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

示例：

```
feat: add weekly report template

Add a new report template for weekly business analysis.
Includes trend charts and comparison tables.
```

## 许可证

贡献的代码将采用 [MIT 许可证](LICENSE)。
