# Data Insight Agent - 环境配置脚本 (Windows PowerShell)
# 用法: .\scripts\setup.ps1

$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-Info { Write-Host "[INFO] $args" -ForegroundColor Blue }
function Write-Success { Write-Host "[SUCCESS] $args" -ForegroundColor Green }
function Write-Warning { Write-Host "[WARNING] $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "[ERROR] $args" -ForegroundColor Red }

# 打印标题
function Write-Header {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host "  Data Insight Agent - 环境配置" -ForegroundColor Blue
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host ""
}

# 检查命令是否存在
function Test-Command {
    param([string]$Command)
    return [bool](Get-Command $Command -ErrorAction SilentlyContinue)
}

# 获取 Node.js 主版本号
function Get-NodeMajorVersion {
    $version = node -v 2>$null
    if ($version) {
        return [int]($version -replace 'v' -split '\.')[0]
    }
    return 0
}

# 步骤 1: 检查 Node.js
function Test-NodeJS {
    Write-Info "检查 Node.js 环境..."

    if (-not (Test-Command "node")) {
        Write-Error "未找到 Node.js，请先安装 Node.js >= 18"
        Write-Info "下载地址: https://nodejs.org/"
        exit 1
    }

    $nodeVersion = Get-NodeMajorVersion
    if ($nodeVersion -lt 18) {
        Write-Error "Node.js 版本过低 (当前: v$nodeVersion)，需要 >= 18"
        exit 1
    }

    Write-Success "Node.js 版本: $(node -v)"
}

# 步骤 2: 检查 npm
function Test-Npm {
    Write-Info "检查 npm..."

    if (-not (Test-Command "npm")) {
        Write-Error "未找到 npm"
        exit 1
    }

    Write-Success "npm 版本: $(npm -v)"
}

# 步骤 3: 安装 MySQL MCP Server 依赖
function Install-MySQLMCP {
    Write-Info "配置 MySQL MCP Server..."

    $mcpDir = ".\mcp\mcp-mysql-server"

    if (-not (Test-Path $mcpDir)) {
        Write-Warning "MySQL MCP Server 目录不存在: $mcpDir"
        Write-Info "请确保已克隆完整仓库"
        return $false
    }

    Push-Location $mcpDir

    try {
        # 安装依赖
        Write-Info "安装依赖..."
        npm install

        # 编译 TypeScript
        Write-Info "编译 TypeScript..."
        npm run build 2>$null
        if ($LASTEXITCODE -ne 0) {
            npx tsc
        }

        Write-Success "MySQL MCP Server 配置完成"
    }
    finally {
        Pop-Location
    }
}

# 步骤 4: 检查 Python/uv (Lindorm 可选)
function Test-PythonUV {
    Write-Info "检查 Python/uv 环境 (Lindorm 可选)..."

    if (Test-Command "uv") {
        Write-Success "uv 已安装"
        return $true
    }

    if (Test-Command "python") {
        Write-Success "Python 版本: $(python --version)"
        Write-Warning "未找到 uv，如需使用 Lindorm，建议安装: pip install uv"
        return $true
    }

    Write-Warning "未找到 Python/uv，Lindorm 功能将不可用"
    return $false
}

# 步骤 5: 创建必要目录
function New-Directories {
    Write-Info "创建必要目录..."

    $directories = @(
        "analysis-output",
        ".claude\commands"
    )

    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }

    Write-Success "目录创建完成"
}

# 步骤 6: 配置 MCP
function Initialize-MCPConfig {
    Write-Info "配置 MCP..."

    if (Test-Path ".mcp.json") {
        Write-Warning ".mcp.json 已存在，跳过配置"
        return
    }

    if (-not (Test-Path ".mcp.json.example")) {
        Write-Error "未找到 .mcp.json.example 模板文件"
        return
    }

    Write-Host ""
    $configure = Read-Host "是否现在配置 MCP 数据库连接? (y/n)"

    if ($configure -eq "y" -or $configure -eq "Y") {
        Copy-Item ".mcp.json.example" ".mcp.json"
        Write-Success "已创建 .mcp.json，请编辑该文件填入实际的数据库连接信息"
        Write-Info "编辑命令: notepad .mcp.json 或 code .mcp.json"
    }
    else {
        Write-Info "跳过 MCP 配置，后续可手动复制 .mcp.json.example 为 .mcp.json"
    }
}

# 步骤 7: 检查 Claude Code
function Test-ClaudeCode {
    Write-Info "检查 Claude Code..."

    if (Test-Command "claude") {
        Write-Success "Claude Code 已安装"
    }
    else {
        Write-Warning "未找到 Claude Code CLI"
        Write-Info "安装方法: npm install -g @anthropic-ai/claude-code"
    }
}

# 打印完成信息
function Write-Completion {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  环境配置完成!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "后续步骤:"
    Write-Host "  1. 编辑 .mcp.json 填入数据库连接信息"
    Write-Host "  2. 启动 Claude Code: claude"
    Write-Host "  3. 使用 /analyze 命令开始数据分析"
    Write-Host ""
}

# 主函数
function Main {
    Write-Header

    Test-NodeJS
    Test-Npm
    Install-MySQLMCP
    Test-PythonUV
    New-Directories
    Initialize-MCPConfig
    Test-ClaudeCode

    Write-Completion
}

# 运行主函数
Main
