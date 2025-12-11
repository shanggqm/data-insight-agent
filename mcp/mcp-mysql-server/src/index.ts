#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import * as mysql from 'mysql2/promise';
// import { config } from 'dotenv';
import { URL } from 'url';
import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';

// Cache configuration
const CACHE_DIR = path.join(process.cwd(), 'cache');
const SAMPLE_SIZE = 3; // 返回的样本数据条数

// 确保缓存目录存在
function ensureCacheDir(): void {
  if (!fs.existsSync(CACHE_DIR)) {
    fs.mkdirSync(CACHE_DIR, { recursive: true });
  }
}

// 生成缓存文件名
function generateCacheFileName(toolName: string, identifier: string): string {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const hash = crypto.createHash('md5').update(identifier).digest('hex').substring(0, 8);
  return `${toolName}_${timestamp}_${hash}.json`;
}

// 保存缓存并返回格式化结果
function saveAndFormatResult(toolName: string, identifier: string, rows: any[]): { content: { type: string; text: string }[] } {
  ensureCacheDir();

  const fileName = generateCacheFileName(toolName, identifier);
  const filePath = path.join(CACHE_DIR, fileName);

  // 保存完整结果到缓存文件
  const cacheData = {
    toolName,
    identifier,
    timestamp: new Date().toISOString(),
    totalCount: rows.length,
    data: rows
  };
  fs.writeFileSync(filePath, JSON.stringify(cacheData, null, 2), 'utf-8');

  // 构建返回结果：样本数据 + summary + 缓存文件路径
  const sampleData = rows.slice(0, SAMPLE_SIZE);
  const summary = {
    totalCount: rows.length,
    sampleCount: sampleData.length,
    hasMore: rows.length > SAMPLE_SIZE,
    cacheFile: filePath
  };

  const response = {
    summary,
    sampleData
  };

  return {
    content: [
      {
        type: 'text',
        text: JSON.stringify(response, null, 2),
      },
    ],
  };
}

// // Load environment variables
// config();



interface DatabaseConfig {
  host: string;
  user: string;
  password: string;
  database: string;
  port?: number; // Add optional port parameter
}

// Type guard for error objects
function isErrorWithMessage(error: unknown): error is { message: string } {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    typeof (error as Record<string, unknown>).message === 'string'
  );
}

// Helper to get error message
function getErrorMessage(error: unknown): string {
  if (isErrorWithMessage(error)) {
    return error.message;
  }
  return String(error);
}

// Add parseMySQLUrl function after DatabaseConfig interface
function parseMySQLUrl(url: string): DatabaseConfig {
  try {
    const parsedUrl = new URL(url);
    if (parsedUrl.protocol !== 'mysql:') {
      throw new Error('Invalid MySQL URL protocol');
    }

    return {
      host: parsedUrl.hostname,
      user: parsedUrl.username || '',
      password: parsedUrl.password || '',
      database: parsedUrl.pathname.slice(1), // remove leading '/'
      port: parsedUrl.port ? parseInt(parsedUrl.port, 10) : 3306,
    };
  } catch (error: unknown) {
    if (error instanceof Error) {
      throw new Error(`Invalid MySQL URL: ${error.message}`);
    }
    throw new Error('Invalid MySQL URL: Unknown error');
  }
}

class MySQLServer {
  private server: Server;
  private connection: mysql.Connection | null = null;
  private config: DatabaseConfig | null = null;

  constructor() {
    this.server = new Server(
      {
        name: 'mysql-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // Get database URL from command line arguments
    const args = process.argv.slice(2);
    if (args.length > 0) {
      try {
        const databaseUrl = args[0];
        this.config = parseMySQLUrl(databaseUrl);

      } catch (error: unknown) {
        console.error('Error parsing database URL:', error instanceof Error ? error.message : 'Unknown error');
        process.exit(1);
      }
    }

    if (process.env.MYSQL_HOST && process.env.MYSQL_USER && process.env.MYSQL_PASSWORD && process.env.MYSQL_DATABASE) {
      // Fallback to environment variables if no command line argument is provided
      this.config = {
        host: process.env.MYSQL_HOST,
        user: process.env.MYSQL_USER,
        password: process.env.MYSQL_PASSWORD,
        database: process.env.MYSQL_DATABASE,
        port: Number(process.env.MYSQL_PORT ?? 3306),
      };
    }

    if (!this.config) {
      console.error('No database configuration provided. Please provide a MySQL URL as a command line argument');
      console.error('Example: node xxx.js mysql://user:password@localhost:3306/mydb');
      process.exit(1);
    }

    this.setupToolHandlers();

    // Error handling
    this.server.onerror = (error) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {
      await this.cleanup();
      process.exit(0);
    });
  }

  private async cleanup() {
    if (this.connection) {
      await this.connection.end();
    }
    await this.server.close();
  }

  private async ensureConnection() {
    if (!this.config) {
      throw new McpError(
        ErrorCode.InvalidRequest,
        'Database configuration not set. Please provide MySQL URL as command line argument or set environment variables (MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE).'
      );
    }

    if (!this.connection) {
      try {
        this.connection = await mysql.createConnection(this.config);
      } catch (error) {
        throw new McpError(
          ErrorCode.InternalError,
          `Failed to connect to database: ${getErrorMessage(error)}`
        );
      }
    }
  }

  private setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'query',
          description: 'Execute a SELECT query',
          inputSchema: {
            type: 'object',
            properties: {
              sql: {
                type: 'string',
                description: 'SQL SELECT query',
              },
              params: {
                type: 'array',
                items: {
                  type: ['string', 'number', 'boolean', 'null'],
                },
                description: 'Query parameters (optional)',
              },
            },
            required: ['sql'],
          },
        },
        {
          name: 'execute',
          description: 'Execute an INSERT, UPDATE, or DELETE query',
          inputSchema: {
            type: 'object',
            properties: {
              sql: {
                type: 'string',
                description: 'SQL query (INSERT, UPDATE, DELETE)',
              },
              params: {
                type: 'array',
                items: {
                  type: ['string', 'number', 'boolean', 'null'],
                },
                description: 'Query parameters (optional)',
              },
            },
            required: ['sql'],
          },
        },
        {
          name: 'list_tables',
          description: 'List all tables in the database',
          inputSchema: {
            type: 'object',
            properties: {},
            required: [],
          },
        },
        {
          name: 'describe_table',
          description: 'Get table structure',
          inputSchema: {
            type: 'object',
            properties: {
              table: {
                type: 'string',
                description: 'Table name',
              },
            },
            required: ['table'],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      switch (request.params.name) {
        case 'query':
          return await this.handleQuery(request.params.arguments);
        case 'execute':
          return await this.handleExecute(request.params.arguments);
        case 'list_tables':
          return await this.handleListTables();
        case 'describe_table':
          return await this.handleDescribeTable(request.params.arguments);
        default:
          throw new McpError(
            ErrorCode.MethodNotFound,
            `Unknown tool: ${request.params.name}`
          );
      }
    });
  }

  private async handleQuery(args: any) {
    await this.ensureConnection();

    if (!args.sql) {
      throw new McpError(ErrorCode.InvalidParams, 'SQL query is required');
    }

    if (!args.sql.trim().toUpperCase().startsWith('SELECT')) {
      throw new McpError(
        ErrorCode.InvalidParams,
        'Only SELECT queries are allowed with query tool'
      );
    }

    try {
      const [rows] = await this.connection!.query(args.sql, args.params || []);
      return saveAndFormatResult('query', args.sql, rows as any[]);
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Query execution failed: ${getErrorMessage(error)}`
      );
    }
  }

  private async handleExecute(args: any) {
    await this.ensureConnection();

    if (!args.sql) {
      throw new McpError(ErrorCode.InvalidParams, 'SQL query is required');
    }

    const sql = args.sql.trim().toUpperCase();
    if (sql.startsWith('SELECT')) {
      throw new McpError(
        ErrorCode.InvalidParams,
        'Use query tool for SELECT statements'
      );
    }

    try {
      const [result] = await this.connection!.query(args.sql, args.params || []);
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Query execution failed: ${getErrorMessage(error)}`
      );
    }
  }

  private async handleListTables() {
    await this.ensureConnection();

    try {
      const [rows] = await this.connection!.query('SHOW TABLES');
      return saveAndFormatResult('list_tables', 'SHOW_TABLES', rows as any[]);
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to list tables: ${getErrorMessage(error)}`
      );
    }
  }

  private async handleDescribeTable(args: any) {
    await this.ensureConnection();

    if (!args.table) {
      throw new McpError(ErrorCode.InvalidParams, 'Table name is required');
    }

    try {
      const [rows] = await this.connection!.query('DESCRIBE ??', [args.table]);
      return saveAndFormatResult('describe_table', args.table, rows as any[]);
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to describe table: ${getErrorMessage(error)}`
      );
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('MySQL MCP server running on stdio');
  }
}

const server = new MySQLServer();
server.run().catch(console.error);
