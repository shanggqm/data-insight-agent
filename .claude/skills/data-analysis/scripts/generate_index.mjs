#!/usr/bin/env node
/**
 * 报告索引生成脚本
 *
 * 扫描 analysis-output/ 目录下的所有报告文件夹，
 * 生成 index.html 索引页面。
 *
 * 使用方式：
 *   node .claude/skills/data-analysis/scripts/generate_index.mjs
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 项目根目录
const projectRoot = path.resolve(__dirname, '../../../../');
const outputDir = path.join(projectRoot, 'analysis-output');
const templatePath = path.join(__dirname, '../templates/index_template.html');

/**
 * 从文件夹名解析报告信息
 * 格式: {topic}_{YYYYMMDD_HHmmss}
 */
function parseReportFolder(folderName) {
    const match = folderName.match(/^(.+)_(\d{8}_\d{6})$/);
    if (!match) return null;

    return {
        folder: folderName,
        topic: match[1],
        timestamp: match[2]
    };
}

/**
 * 扫描报告目录
 */
function scanReports() {
    if (!fs.existsSync(outputDir)) {
        console.log('analysis-output 目录不存在，创建空索引');
        fs.mkdirSync(outputDir, { recursive: true });
        return [];
    }

    const entries = fs.readdirSync(outputDir, { withFileTypes: true });
    const reports = [];

    for (const entry of entries) {
        if (!entry.isDirectory()) continue;
        if (entry.name.startsWith('.')) continue;

        // 检查是否包含 report.html
        const reportPath = path.join(outputDir, entry.name, 'report.html');
        if (!fs.existsSync(reportPath)) continue;

        const info = parseReportFolder(entry.name);
        if (info) {
            reports.push(info);
        }
    }

    // 按时间倒序排列
    reports.sort((a, b) => b.timestamp.localeCompare(a.timestamp));

    return reports;
}

/**
 * 生成索引页
 */
function generateIndex(reports) {
    let template = fs.readFileSync(templatePath, 'utf8');

    // 替换报告数据
    const reportsJson = JSON.stringify(reports, null, 2);
    template = template.replace(
        /\/\*__REPORTS_DATA__\*\/\[\]\/\*__END_DATA__\*\//,
        `/*__REPORTS_DATA__*/${reportsJson}/*__END_DATA__*/`
    );

    const indexPath = path.join(outputDir, 'index.html');
    fs.writeFileSync(indexPath, template);

    return indexPath;
}

// 主程序
function main() {
    console.log('扫描报告目录...');
    const reports = scanReports();
    console.log(`发现 ${reports.length} 个报告`);

    console.log('生成索引页...');
    const indexPath = generateIndex(reports);
    console.log(`索引页已生成: ${indexPath}`);

    if (reports.length > 0) {
        console.log('\n报告列表:');
        reports.forEach((r, i) => {
            console.log(`  ${i + 1}. ${r.topic} (${r.timestamp})`);
        });
    }

    console.log('\n使用 `npm run serve` 启动服务后访问 http://localhost:3000/');
}

main();
