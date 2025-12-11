#!/bin/bash

# Data Insight Agent - 环境配置脚本 (macOS/Linux)
# 用法: ./scripts/setup.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 打印标题
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Data Insight Agent - 环境配置${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# 检查命令是否存在
check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# 获取 Node.js 主版本号
get_node_major_version() {
    node -v 2>/dev/null | sed 's/v//' | cut -d. -f1
}

# 步骤 1: 检查 Node.js
check_nodejs() {
    print_info "检查 Node.js 环境..."

    if ! check_command node; then
        print_error "未找到 Node.js，请先安装 Node.js >= 18"
        print_info "推荐使用 nvm 安装: https://github.com/nvm-sh/nvm"
        exit 1
    fi

    NODE_VERSION=$(get_node_major_version)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_error "Node.js 版本过低 (当前: v$NODE_VERSION)，需要 >= 18"
        exit 1
    fi

    print_success "Node.js 版本: $(node -v)"
}

# 步骤 2: 检查 npm
check_npm() {
    print_info "检查 npm..."

    if ! check_command npm; then
        print_error "未找到 npm"
        exit 1
    fi

    print_success "npm 版本: $(npm -v)"
}

# 步骤 3: 安装 MySQL MCP Server 依赖
setup_mysql_mcp() {
    print_info "配置 MySQL MCP Server..."

    MCP_DIR="./mcp/mcp-mysql-server"

    if [ ! -d "$MCP_DIR" ]; then
        print_warning "MySQL MCP Server 目录不存在: $MCP_DIR"
        print_info "请确保已克隆完整仓库"
        return 1
    fi

    cd "$MCP_DIR"

    # 安装依赖
    print_info "安装依赖..."
    npm install

    # 编译 TypeScript
    print_info "编译 TypeScript..."
    npm run build 2>/dev/null || npx tsc

    cd - > /dev/null

    print_success "MySQL MCP Server 配置完成"
}

# 步骤 4: 检查 Python/uv (Lindorm 可选)
check_python_uv() {
    print_info "检查 Python/uv 环境 (Lindorm 可选)..."

    if check_command uv; then
        print_success "uv 版本: $(uv --version)"
        return 0
    fi

    if check_command python3; then
        print_success "Python 版本: $(python3 --version)"
        print_warning "未找到 uv，如需使用 Lindorm，建议安装: curl -LsSf https://astral.sh/uv/install.sh | sh"
        return 0
    fi

    print_warning "未找到 Python/uv，Lindorm 功能将不可用"
}

# 步骤 5: 创建必要目录
create_directories() {
    print_info "创建必要目录..."

    mkdir -p analysis-output
    mkdir -p .claude/commands

    print_success "目录创建完成"
}

# 步骤 6: 配置 MCP
setup_mcp_config() {
    print_info "配置 MCP..."

    if [ -f ".mcp.json" ]; then
        print_warning ".mcp.json 已存在，跳过配置"
        return 0
    fi

    if [ ! -f ".mcp.json.example" ]; then
        print_error "未找到 .mcp.json.example 模板文件"
        return 1
    fi

    echo ""
    read -p "是否现在配置 MCP 数据库连接? (y/n): " configure_mcp

    if [ "$configure_mcp" = "y" ] || [ "$configure_mcp" = "Y" ]; then
        cp .mcp.json.example .mcp.json
        print_success "已创建 .mcp.json，请编辑该文件填入实际的数据库连接信息"
        print_info "编辑命令: nano .mcp.json 或 code .mcp.json"
    else
        print_info "跳过 MCP 配置，后续可手动复制 .mcp.json.example 为 .mcp.json"
    fi
}

# 步骤 7: 检查 Claude Code
check_claude_code() {
    print_info "检查 Claude Code..."

    if check_command claude; then
        print_success "Claude Code 已安装: $(claude --version 2>/dev/null || echo '已安装')"
    else
        print_warning "未找到 Claude Code CLI"
        print_info "安装方法: npm install -g @anthropic-ai/claude-code"
    fi
}

# 打印完成信息
print_completion() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  环境配置完成!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "后续步骤:"
    echo "  1. 编辑 .mcp.json 填入数据库连接信息"
    echo "  2. 启动 Claude Code: claude"
    echo "  3. 使用 /analyze 命令开始数据分析"
    echo ""
}

# 主函数
main() {
    print_header

    check_nodejs
    check_npm
    setup_mysql_mcp
    check_python_uv
    create_directories
    setup_mcp_config
    check_claude_code

    print_completion
}

# 运行主函数
main "$@"
