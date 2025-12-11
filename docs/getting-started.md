# 快速开始指南

5 分钟上手 Data Insight Agent。

## 前提条件

- **Node.js >= 18**：[下载地址](https://nodejs.org/)
- **Claude Code CLI**：`npm install -g @anthropic-ai/claude-code`.(建议安装最新版本)
- **数据库访问权限**：MySQL 或其它有 mcp-server 可以连接的数据库

> 本仓库提供了基于 Node.js 连接 mysql 数据库的 mcp server，如果需要访问其它数据库，依赖的运行时环境可能会有差异，譬如 lindorm 数据库就需要依赖`uv`环境，需要自行安装

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/shanggqm/data-insight-agent.git
cd data-insight-agent
```

### 2. 运行配置脚本

**macOS / Linux:**

```bash
chmod +x ./scripts/setup.sh
./scripts/setup.sh
```

**Windows PowerShell:**

```powershell
.\scripts\setup.ps1
```

脚本会自动：

- 检查 Node.js 版本
- 安装 MySQL MCP Server 依赖
- 编译 TypeScript
- 创建必要目录

### 3. 配置数据库连接

```bash
# 复制配置模板
cp .mcp.json.example .mcp.json

# 编辑配置文件
code .mcp.json  # 或 nano、vim 等
```

编辑 `.mcp.json`，填入实际的数据库连接信息：

```json
{
  "mcpServers": {
    "mysql": {
      "env": {
        "MYSQL_HOST": "your-mysql-host",
        "MYSQL_PORT": "3306",
        "MYSQL_USER": "your-user",
        "MYSQL_PASSWORD": "your-password",
        "MYSQL_DATABASE": "your-database"
      }
    }
  }
}
```

> **安全提示**：确保数据库用户仅有只读权限

### 4. 启动 Claude Code

在项目的根目录下启动 Claude Code

```bash
claude
```

启动成功后，可以先检查一下 mcp 有没有连接成功：

```bash
/mcp
```

### 5. 开始第一次分析

在 Claude Code 中输入：

```
/analyze
```

然后描述你的分析需求，例如：

> 分析最近 30 天的用户注册情况，关注日注册量趋势和用户来源分布

## 分析输出

分析完成后，结果保存在 `analysis-output/` 目录：

```
analysis-output/
├── index.html                      # 报告中心（索引页）
└── user_registration_20241210_143000/
    ├── processed_data/
    │   └── charts_data.json        # 图表数据
    ├── report.md                   # Markdown 报告
    └── report.html                 # HTML 幻灯片
```

### 查看分析报告

由于浏览器安全限制，HTML 报告需要通过 HTTP 服务访问。项目提供了便捷的 npm 命令：

```bash
# 启动报告服务
npm run serve

# 启动并自动打开浏览器
npm run serve:open
```

然后访问：

- **报告中心**: http://localhost:3000/ - 查看所有报告列表
- **单个报告**: http://localhost:3000/{报告文件夹}/report.html

> **提示**：报告中心会自动列出所有分析报告，按生成时间倒序排列。

## 常见问题

### MCP 连接失败

1. 检查 `.mcp.json` 配置是否正确
2. 确认数据库可访问（网络、防火墙）
3. 验证数据库用户名密码

### 找不到 /analyze 命令

确保项目目录中存在 `.claude/commands/analyze.md` 文件。

### Node.js 版本过低

```bash
# 使用 nvm 安装新版本
nvm install 20
nvm use 20
```
