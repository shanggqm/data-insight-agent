# Data Insight Agent

[English](README.md)
<img width="5414" height="668" alt="image" src="https://github.com/user-attachments/assets/1a9ed343-c0f3-437a-ab5b-f5492039795d" />
**别再和数据较劲，直接获取洞察。**

数据分析师和产品经理每天都在重复同样的流程：写 SQL、导出 Excel、手工聚合、画图表、写报告。即便有了大模型，依然困难重重——计算幻觉、上下文超限、输出不稳定。

社区里的 MCP Server？解决了"能不能用"，但离"好不好用"差了十万八千里。查询超时、凭证暴露、上下文爆炸，一个坑接着一个坑。

**Data Insight Agent** 是经过实战打磨的解决方案，融合 Claude Code + MCP + 上下文工程最佳实践：

- **CodeAct 模式** - 让模型写代码执行计算，彻底消除计算幻觉
- **智能缓存** - 查询结果写入文件系统，不再撑爆上下文
- **标准化输出** - 专业 Markdown 报告 + 交互式 HTML 幻灯片，每次都稳定输出
- **生产级 MCP** - 重构 MySQL Server，修复安全和可靠性问题

一条命令，自然语言输入，专业分析输出。

## 快速开始

```bash
git clone https://github.com/shanggqm/data-insight-agent.git
cd data-insight-agent
./scripts/setup.sh
cp .mcp.json.example .mcp.json  # 配置数据库连接
claude
/analyze
```

## 输出结构

```
analysis-output/{主题}_{时间戳}/
├── processed_data/charts_data.json   # 图表数据
├── report.md                         # Markdown 报告
└── report.html                       # 交互式幻灯片
```

## 文档

- [快速开始指南](docs/getting-started.md)
- [贡献指南](CONTRIBUTING.md)

## 许可证

[MIT](LICENSE)

## 作者

**郭美青** · GitHub [@shanggqm](https://github.com/shanggqm) · 微信公众号: **郭美青聊 AI**

![](.claude/skills/data-analysis/references/andy_talk_ai_qrcode.jpg)
