# 第九章：常见问题 (FAQ)

本章汇总了插件开发和使用过程中的常见问题及解决方案。

## 9.1 插件发现和加载

### Q1: 为什么我的插件没有被 OpenClaw 发现？

**可能原因和解决方案：**

1. **清单文件缺失或格式错误**
   ```bash
   # 检查清单文件是否存在
   ls ~/.openclaw/extensions/my-plugin/openclaw.plugin.json

   # 验证 JSON 格式
   cat ~/.openclaw/extensions/my-plugin/openclaw.plugin.json | jq .
   ```

2. **插件目录位置不正确**
   ```bash
   # 正确的位置
   ~/.openclaw/extensions/my-plugin/
   # 或
   <workspace>/.openclaw/extensions/my-plugin/
   ```

3. **清单文件缺少必需字段**
   ```json
   // 最小清单文件
   {
     "id": "my-plugin",
     "configSchema": {
       "type": "object",
       "additionalProperties": false,
       "properties": {}
     }
   }
   ```

4. **查看插件列表确认**
   ```bash
   openclaw plugins list --verbose
   ```

### Q2: 插件加载失败，显示安全错误怎么办？

**常见安全错误：**

```
Plugin security error: Path traversal detected
Plugin security error: World-writable directory
Plugin security error: Ownership mismatch
```

**解决方案：**

1. **路径遍历错误**：确保没有使用 `../` 或符号链接逃出插件目录

2. **世界可写目录**：
   ```bash
   # 修复权限
   chmod 755 ~/.openclaw/extensions/my-plugin
   ```

3. **所有权不匹配**：
   ```bash
   # 修复所有权
   chown -R $(whoami) ~/.openclaw/extensions/my-plugin
   ```

### Q3: 如何调试插件加载过程？

**方法：**

1. **查看 Gateway 日志**
   ```bash
   tail -f ~/.openclaw/gateway.log | grep plugin
   ```

2. **使用 verbose 模式**
   ```bash
   openclaw plugins list --verbose
   ```

3. **在插件中添加日志**
   ```typescript
   register(api: OpenClawPluginApi) {
     api.logger.info("[my-plugin] 开始注册...");
     // ...
     api.logger.info("[my-plugin] 注册完成");
   }
   ```

## 9.2 配置问题

### Q4: 插件配置不生效怎么办？

**排查步骤：**

1. **检查配置格式**
   ```json5
   // config.json5
   {
     plugins: {
       entries: {
         "my-plugin": {
           enabled: true,  // 确保启用
           config: {
             // 配置项
           },
         },
       },
     },
   }
   ```

2. **重启 Gateway**
   ```bash
   # 配置更改后必须重启
   openclaw gateway stop
   openclaw gateway start
   ```

3. **检查配置验证**
   ```bash
   openclaw plugins doctor
   ```

4. **查看配置解析日志**
   ```typescript
   register(api: OpenClawPluginApi) {
     const config = this.configSchema.parse(api.pluginConfig);
     api.logger.info(`[my-plugin] 配置: ${JSON.stringify(config)}`);
   }
   ```

### Q5: 如何处理配置验证错误？

**常见验证错误：**

```
Config validation error: Additional properties not allowed
Config validation error: Required property missing
Config validation error: Invalid type
```

**解决方案：**

1. **额外属性错误**：在 Schema 中添加 `additionalProperties: false` 后删除未知属性

2. **缺少必需属性**：提供所有必需属性或设置默认值

3. **类型错误**：确保配置值类型与 Schema 匹配

```typescript
// 提供默认值的解析函数
function parseConfig(value: unknown): MyConfig {
  const raw = value && typeof value === "object" ? value : {};

  return {
    // 使用 ?? 提供默认值
    apiKey: (raw as any).apiKey ?? "",
    timeout: Number((raw as any).timeout) || 30000,
  };
}
```

### Q6: 如何在配置中使用环境变量？

**方法：**

```typescript
function parseConfig(value: unknown): MyConfig {
  const raw = value && typeof value === "object" ? value : {};

  return {
    // 优先使用配置值，其次环境变量
    apiKey:
      (raw as any).apiKey ??
      process.env.MY_PLUGIN_API_KEY ??
      "",
  };
}
```

在清单中声明环境变量（用于文档）：

```json
{
  "id": "my-plugin",
  "envVars": ["MY_PLUGIN_API_KEY"]
}
```

## 9.3 工具开发问题

### Q7: 工具没有被 Agent 调用怎么办？

**可能原因：**

1. **工具描述不够清晰**
   ```typescript
   // ❌ 不推荐：描述太模糊
   description: "处理数据",

   // ✅ 推荐：描述清晰具体
   description:
     "将文本翻译成指定语言。当用户需要翻译内容、转换语言时使用此工具。",
   ```

2. **参数描述不清晰**
   ```typescript
   parameters: Type.Object({
     // ✅ 添加参数描述
     text: Type.String({
       description: "要翻译的文本内容",
     }),
     target_lang: Type.String({
       description: "目标语言代码，如 zh(中文)、en(英语)、ja(日语)",
     }),
   }),
   ```

3. **工具是可选的且被策略禁用**
   ```typescript
   // 检查是否注册为可选工具
   api.registerTool(tool, { optional: true });
   ```

### Q8: 工具执行超时怎么办？

**解决方案：**

1. **实现超时控制**
   ```typescript
   async execute(_toolCallId, params) {
     const timeout = 30000; // 30 秒超时

     const result = await Promise.race([
       performOperation(params),
       new Promise((_, reject) =>
         setTimeout(() => reject(new Error("操作超时")), timeout),
       ),
     ]);

     return result;
   }
   ```

2. **提供进度反馈**
   ```typescript
   async execute(_toolCallId, params) {
     // 分批处理大数据
     const batchSize = 100;
     const results = [];

     for (let i = 0; i < data.length; i += batchSize) {
       const batch = data.slice(i, i + batchSize);
       results.push(...await processBatch(batch));
     }

     return { content: [{ type: "text", text: JSON.stringify(results) }] };
   }
   ```

### Q9: 如何处理工具参数验证错误？

**最佳实践：**

```typescript
async execute(_toolCallId, params) {
  try {
    // 1. 检查参数存在
    if (!params) {
      return {
        content: [{ type: "text", text: "错误：缺少参数" }],
      };
    }

    // 2. 验证必需参数
    const requiredParam = params.required_param;
    if (!requiredParam || typeof requiredParam !== "string") {
      return {
        content: [{ type: "text", text: "错误：请提供有效的 required_param 参数" }],
      };
    }

    // 3. 验证参数范围
    const count = Number(params.count) || 10;
    if (count < 1 || count > 100) {
      return {
        content: [{ type: "text", text: "错误：count 必须在 1-100 之间" }],
      };
    }

    // 4. 执行操作
    const result = await performOperation(requiredParam, count);

    return {
      content: [{ type: "text", text: result }],
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `操作失败: ${error instanceof Error ? error.message : String(error)}`,
      }],
    };
  }
}
```

## 9.4 钩子问题

### Q10: 钩子没有触发怎么办？

**排查步骤：**

1. **确认事件名称正确**
   ```typescript
   // ✅ 正确的事件名称
   api.on("message_received", handler);

   // ❌ 错误的事件名称
   api.on("messageReceived", handler);  // 驼峰命名是错的
   ```

2. **确认钩子已注册**
   ```bash
   openclaw hooks list
   ```

3. **检查钩子函数返回值**
   ```typescript
   // 某些钩子需要返回特定值才能生效
   api.on("message_sending", async (event, ctx) => {
     // 返回 { cancel: true } 会取消消息
     if (shouldBlock(event.content)) {
       return { cancel: true };
     }
     // 返回 { content: "..." } 会修改消息
     return { content: modifiedContent };
   });
   ```

### Q11: 如何在钩子中访问配置？

```typescript
register(api: OpenClawPluginApi) {
  // 保存配置引用
  const config = this.configSchema.parse(api.pluginConfig);

  api.on("message_received", async (event, ctx) => {
    // 使用闭包访问配置
    if (config.logMessages) {
      api.logger.info(`收到消息: ${event.content}`);
    }
  });
}
```

### Q12: 钩子执行顺序如何控制？

```typescript
// 使用 priority 选项控制执行顺序
// 数字越小，优先级越高
api.on("message_received", handler1, { priority: 10 });
api.on("message_received", handler2, { priority: 5 });  // 先执行
api.on("message_received", handler3, { priority: 20 }); // 后执行
```

## 9.5 HTTP 路由问题

### Q13: HTTP 路由返回 404 怎么办？

**检查项：**

1. **路由路径正确**
   ```typescript
   api.registerHttpRoute({
     path: "/my-plugin/api",  // 不需要 /plugins 前缀
     // 完整 URL: /plugins/my-plugin/api
   });
   ```

2. **确认插件已启用**
   ```bash
   openclaw plugins list
   ```

3. **重启 Gateway**
   ```bash
   openclaw gateway restart
   ```

### Q14: 如何处理 CORS 问题？

```typescript
api.registerHttpRoute({
  path: "/my-plugin/api",
  handler: async (req, res) => {
    // 设置 CORS 头
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type");

    // 处理预检请求
    if (req.method === "OPTIONS") {
      res.statusCode = 204;
      res.end();
      return true;
    }

    // 处理实际请求
    // ...
  },
});
```

### Q15: 如何验证 Webhook 签名？

```typescript
import crypto from "node:crypto";

api.registerHttpRoute({
  path: "/my-plugin/webhook",
  handler: async (req, res) => {
    // 读取请求体
    const body = await readBody(req);

    // 获取签名头
    const signature = req.headers["x-signature"] as string;

    // 计算预期签名
    const expectedSignature = crypto
      .createHmac("sha256", config.secret)
      .update(body)
      .digest("hex");

    // 使用时间安全的比较
    if (
      !signature ||
      !crypto.timingSafeEqual(
        Buffer.from(signature),
        Buffer.from(expectedSignature),
      )
    ) {
      res.statusCode = 401;
      res.end(JSON.stringify({ error: "Invalid signature" }));
      return true;
    }

    // 处理请求
    // ...
  },
});
```

## 9.6 服务问题

### Q16: 服务启动失败怎么办？

**常见错误：**

1. **端口被占用**
   ```typescript
   async start(ctx) {
     try {
       await startServer(ctx.config.port);
     } catch (error) {
       if (error.code === "EADDRINUSE") {
         ctx.logger.error("[my-service] 端口被占用");
         // 尝试使用其他端口
       }
       throw error;
     }
   }
   ```

2. **依赖服务不可用**
   ```typescript
   async start(ctx) {
     // 检查依赖服务
     const healthy = await checkDependency();
     if (!healthy) {
       ctx.logger.warn("[my-service] 依赖服务不可用，等待重试...");
       // 实现重试逻辑
     }
   }
   ```

### Q17: 如何正确停止服务？

```typescript
api.registerService({
  id: "my-service",

  async start(ctx) {
    // 保存资源引用
    this.server = await createServer();
    this.timer = setInterval(task, 60000);
  },

  async stop(ctx) {
    ctx.logger.info("[my-service] 正在停止...");

    // 1. 停止接受新请求
    if (this.server) {
      await new Promise((resolve) => this.server.close(resolve));
    }

    // 2. 清理定时器
    if (this.timer) {
      clearInterval(this.timer);
    }

    // 3. 等待进行中的请求完成
    await waitForPendingRequests();

    ctx.logger.info("[my-service] 已停止");
  },
});
```

## 9.7 性能问题

### Q18: 插件导致系统变慢怎么办？

**诊断步骤：**

1. **检查日志输出频率**
   ```typescript
   // ❌ 避免：每次调用都输出日志
   for (const item of items) {
     api.logger.info(`处理: ${item}`);
   }

   // ✅ 推荐：批量或关键节点输出
   api.logger.info(`开始处理 ${items.length} 项`);
   // 处理...
   api.logger.info(`处理完成`);
   ```

2. **检查钩子处理时间**
   ```typescript
   api.on("message_received", async (event, ctx) => {
     const start = Date.now();

     // 处理...

     const duration = Date.now() - start;
     if (duration > 100) {
       api.logger.warn(`[my-plugin] 钩子处理耗时 ${duration}ms`);
     }
   });
   ```

3. **避免同步阻塞**
   ```typescript
   // ❌ 避免：同步文件操作
   const data = fs.readFileSync(path);

   // ✅ 推荐：异步操作
   const data = await fs.promises.readFile(path);
   ```

### Q19: 如何处理大量数据？

```typescript
// 使用流式处理
import { createReadStream } from "node:fs";

async function processLargeFile(filePath: string) {
  const stream = createReadStream(filePath);

  for await (const chunk of stream) {
    // 逐块处理
    await processChunk(chunk);
  }
}

// 使用分页查询
async function fetchAllData(api, pageSize = 100) {
  let page = 1;
  const allData = [];

  while (true) {
    const data = await api.fetchPage(page, pageSize);
    if (data.length === 0) break;

    allData.push(...data);
    page++;
  }

  return allData;
}
```

## 9.8 其他问题

### Q20: 如何调试插件？

**方法：**

1. **使用环境变量启用调试**
   ```bash
   DEBUG=my-plugin:* openclaw gateway
   ```

2. **在代码中添加断点式日志**
   ```typescript
   function debug(api: OpenClawPluginApi, label: string, data: unknown) {
     if (process.env.MY_PLUGIN_DEBUG) {
       api.logger.debug?.(`[DEBUG] ${label}: ${JSON.stringify(data, null, 2)}`);
     }
   }
   ```

3. **使用 Node.js 调试器**
   ```bash
   node --inspect-brk $(which openclaw) gateway
   ```

### Q21: 如何发布插件到 npm？

**步骤：**

1. **准备 package.json**
   ```json
   {
     "name": "@my-scope/openclaw-my-plugin",
     "version": "1.0.0",
     "main": "dist/index.js",
     "types": "dist/index.d.ts",
     "openclaw": {
       "extensions": ["./dist/index.js"]
     }
   }
   ```

2. **构建和发布**
   ```bash
   npm run build
   npm publish --access public
   ```

3. **用户安装**
   ```bash
   openclaw plugins install @my-scope/openclaw-my-plugin
   ```

### Q22: 如何处理插件版本兼容性？

```typescript
// 在 register 函数中检查 API 版本
register(api: OpenClawPluginApi) {
  // 检查所需的 API 方法是否存在
  if (!api.on) {
    api.logger.warn(
      "[my-plugin] 当前版本不支持 on() API，部分功能不可用"
    );
    // 使用回退方案
    return;
  }

  // 正常注册
  // ...
}
```

## 9.9 总结

本章涵盖了插件开发的常见问题和解决方案：

| 类别 | 主要问题 |
|------|----------|
| 插件发现 | 清单文件、目录位置、安全检查 |
| 配置 | 验证错误、环境变量、默认值 |
| 工具开发 | Agent 调用、超时、参数验证 |
| 钩子 | 事件名称、执行顺序、配置访问 |
| HTTP 路由 | 404 错误、CORS、签名验证 |
| 服务 | 启动失败、停止清理 |
| 性能 | 日志频率、阻塞操作、大数据处理 |
| 其他 | 调试、发布、兼容性 |

如果遇到本 FAQ 未涵盖的问题，请：
1. 查阅官方文档
2. 查看 `extensions/` 目录下的现有插件
3. 在 GitHub Issues 提问

---

**上一章**：[最佳实践](./08-最佳实践.md) | **下一章**：[生态系统](./10-生态系统.md)
