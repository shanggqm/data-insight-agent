# Data Insight Agent

[中文文档](README_CN.md)
<img width="5414" height="668" alt="image" src="https://github.com/user-attachments/assets/1a9ed343-c0f3-437a-ab5b-f5492039795d" />

**Stop wrestling with data, start getting insights.**

Data analysts and product managers spend hours on repetitive workflows: writing SQL, exporting to Excel, manual aggregation, building charts, writing reports. Even with LLMs, you hit walls - hallucinated calculations, context length limits, unreliable outputs.

Generic MCP servers? They solve "can it work" but not "can I actually use it". Query timeouts, credential exposure, context explosions - one pitfall after another.

**Data Insight Agent** is battle-tested solution combining Claude Code + MCP + Context Engineering best practices:

- **CodeAct Pattern** - LLM writes & executes code for calculations, eliminating hallucinations
- **Smart Caching** - Query results go to filesystem, not context. No more token explosions
- **Standardized Output** - Professional Markdown reports + interactive HTML slides, every time
- **Production-Ready MCP** - Rebuilt MySQL server with security and reliability fixes

One command. Natural language in, professional analysis out.

## Quick Start

```bash
git clone https://github.com/shanggqm/data-insight-agent.git
cd data-insight-agent
./scripts/setup.sh
cp .mcp.json.example .mcp.json  # Configure your database
claude
/analyze
```

## Output

```
analysis-output/{topic}_{timestamp}/
├── processed_data/charts_data.json   # Chart data
├── report.md                         # Markdown report
└── report.html                       # Interactive slides
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [Contributing](CONTRIBUTING.md)

## License

[MIT](LICENSE)

## Author

**Meiqing Guo** · GitHub [@shanggqm](https://github.com/shanggqm) · WeChat: **郭美青聊AI**
