# 第六章：API 文档

本章提供 OpenClaw 插件 API 的完整参考文档。所有类型和方法都附带详细注释。

## 6.1 核心类型

### 6.1.1 OpenClawPluginApi

插件 API 是插件与 OpenClaw 核心交互的主要接口。

```typescript
/**
 * OpenClaw 插件 API
 * 提供所有插件注册功能
 */
interface OpenClawPluginApi {
  // ========== 基本信息 ==========

  /** 插件唯一标识符 */
  id: string;

  /** 插件显示名称 */
  name: string;

  /** 插件版本号 */
  version?: string;

  /** 插件描述 */
  description?: string;

  /** 插件来源路径 */
  source: string;

  // ========== 配置访问 ==========

  /** OpenClaw 全局配置对象 */
  config: OpenClawConfig;

  /** 当前插件的配置（来自 plugins.entries.<id>.config） */
  pluginConfig?: Record<string, unknown>;

  // ========== 运行时 ==========

  /** 运行时 API（TTS、STT、工具等） */
  runtime: PluginRuntime;

  /** 日志记录器 */
  logger: PluginLogger;

  // ========== 路径解析 ==========

  /**
   * 解析相对于插件目录的路径
   * @param input 相对路径
   * @returns 绝对路径
   */
  resolvePath: (input: string) => string;

  // ========== 功能注册方法 ==========

  /**
   * 注册 Agent 工具
   * @param tool 工具定义或工厂函数
   * @param opts 可选配置
   */
  registerTool: (
    tool: AnyAgentTool | OpenClawPluginToolFactory,
    opts?: OpenClawPluginToolOptions,
  ) => void;

  /**
   * 注册事件钩子
   * @param events 事件名称或事件数组
   * @param handler 处理函数
   * @param opts 可选配置
   */
  registerHook: (
    events: string | string[],
    handler: InternalHookHandler,
    opts?: OpenClawPluginHookOptions,
  ) => void;

  /**
   * 注册 HTTP 路由
   * @param params 路由配置
   */
  registerHttpRoute: (params: OpenClawPluginHttpRouteParams) => void;

  /**
   * 注册消息渠道
   * @param registration 渠道注册对象
   */
  registerChannel: (
    registration: OpenClawPluginChannelRegistration | ChannelPlugin,
  ) => void;

  /**
   * 注册 Gateway RPC 方法
   * @param method 方法名称
   * @param handler 处理函数
   */
  registerGatewayMethod: (
    method: string,
    handler: GatewayRequestHandler,
  ) => void;

  /**
   * 注册 CLI 命令
   * @param registrar 注册函数
   * @param opts 可选配置
   */
  registerCli: (
    registrar: OpenClawPluginCliRegistrar,
    opts?: { commands?: string[] },
  ) => void;

  /**
   * 注册后台服务
   * @param service 服务定义
   */
  registerService: (service: OpenClawPluginService) => void;

  /**
   * 注册模型提供商
   * @param provider 提供商定义
   */
  registerProvider: (provider: ProviderPlugin) => void;

  /**
   * 注册自动回复命令
   * @param command 命令定义
   */
  registerCommand: (command: OpenClawPluginCommandDefinition) => void;

  // ========== 生命周期钩子（新 API）==========

  /**
   * 注册生命周期钩子
   * @param hookName 钩子名称
   * @param handler 处理函数
   * @param opts 可选配置（如优先级）
   */
  on: <K extends PluginHookName>(
    hookName: K,
    handler: PluginHookHandlerMap[K],
    opts?: { priority?: number },
  ) => void;
}
```

### 6.1.2 PluginLogger

日志记录器接口。

```typescript
/**
 * 插件日志记录器
 */
interface PluginLogger {
  /**
   * 调试级别日志（仅在调试模式显示）
   */
  debug?: (message: string) => void;

  /**
   * 信息级别日志
   */
  info: (message: string) => void;

  /**
   * 警告级别日志
   */
  warn: (message: string) => void;

  /**
   * 错误级别日志
   */
  error: (message: string) => void;
}

// 使用示例
api.logger.info("[my-plugin] 插件已加载");
api.logger.warn("[my-plugin] 配置缺失，使用默认值");
api.logger.error("[my-plugin] 发生错误");
```

### 6.1.3 OpenClawPluginConfigSchema

配置 Schema 定义。

```typescript
/**
 * 插件配置 Schema
 */
interface OpenClawPluginConfigSchema {
  /**
   * 安全解析配置
   * 用于运行时配置验证
   */
  safeParse?: (value: unknown) => {
    success: boolean;
    data?: unknown;
    error?: {
      issues?: Array<{
        path: Array<string | number>;
        message: string;
      }>;
    };
  };

  /**
   * 解析配置
   * 返回解析后的配置对象
   */
  parse?: (value: unknown) => unknown;

  /**
   * 验证配置
   * 返回验证结果
   */
  validate?: (value: unknown) => PluginConfigValidation;

  /**
   * UI 提示信息
   * 用于配置 UI 渲染
   */
  uiHints?: Record<string, PluginConfigUiHint>;

  /**
   * JSON Schema 定义
   * 用于配置验证
   */
  jsonSchema?: Record<string, unknown>;
}

/**
 * 配置验证结果
 */
type PluginConfigValidation =
  | { ok: true; value?: unknown }
  | { ok: false; errors: string[] };

/**
 * 配置字段 UI 提示
 */
interface PluginConfigUiHint {
  /** 显示标签 */
  label?: string;

  /** 帮助文本 */
  help?: string;

  /** 标签 */
  tags?: string[];

  /** 是否为高级选项 */
  advanced?: boolean;

  /** 是否为敏感信息（如密码） */
  sensitive?: boolean;

  /** 输入框占位符 */
  placeholder?: string;
}
```

## 6.2 工具 API

### 6.2.1 AnyAgentTool

Agent 工具定义。

```typescript
/**
 * Agent 工具定义
 */
interface AnyAgentTool {
  /** 工具名称（使用 snake_case） */
  name: string;

  /** 显示标签 */
  label?: string;

  /** 工具描述（Agent 根据此描述决定是否调用） */
  description: string;

  /** 参数 Schema（使用 Typebox） */
  parameters: TSchema;

  /** 执行函数 */
  execute: (
    toolCallId: string,
    params: Record<string, unknown>,
  ) => Promise<ToolResult>;
}

/**
 * 工具执行结果
 */
interface ToolResult {
  /** 内容数组 */
  content: Array<{
    type: "text" | "image";
    text?: string;
    image_url?: { url: string };
  }>;

  /** 附加详情（可选） */
  details?: unknown;
}

/**
 * 工具工厂函数
 */
type OpenClawPluginToolFactory = (
  ctx: OpenClawPluginToolContext,
) => AnyAgentTool | AnyAgentTool[] | null | undefined;

/**
 * 工具上下文
 */
interface OpenClawPluginToolContext {
  /** OpenClaw 配置 */
  config?: OpenClawConfig;

  /** 工作区目录 */
  workspaceDir?: string;

  /** Agent 目录 */
  agentDir?: string;

  /** Agent ID */
  agentId?: string;

  /** 会话 Key */
  sessionKey?: string;

  /** 会话 ID（临时 UUID） */
  sessionId?: string;

  /** 消息渠道 */
  messageChannel?: string;

  /** Agent 账户 ID */
  agentAccountId?: string;

  /** 请求者发送者 ID */
  requesterSenderId?: string;

  /** 发送者是否为所有者 */
  senderIsOwner?: boolean;

  /** 是否沙箱化 */
  sandboxed?: boolean;
}

/**
 * 工具注册选项
 */
interface OpenClawPluginToolOptions {
  /** 工具名称（用于工厂函数） */
  name?: string;

  /** 多个工具名称 */
  names?: string[];

  /** 是否为可选工具 */
  optional?: boolean;
}
```

### 6.2.2 使用 Typebox 定义参数

```typescript
import { Type } from "@sinclair/typebox";

// 简单字符串参数
const nameParam = Type.String({
  description: "用户名称",
});

// 可选参数
const optionalParam = Type.Optional(
  Type.String({
    description: "可选参数",
  }),
);

// 枚举参数
const enumParam = Type.String({
  enum: ["option1", "option2", "option3"],
  description: "选择选项",
});

// 数字参数（带范围）
const numberParam = Type.Number({
  minimum: 0,
  maximum: 100,
  description: "数值（0-100）",
});

// 数组参数
const arrayParam = Type.Array(Type.String(), {
  description: "字符串数组",
});

// 对象参数
const objectParam = Type.Object({
  name: Type.String(),
  age: Type.Number(),
  email: Type.Optional(Type.String()),
});

// 完整工具示例
api.registerTool({
  name: "example_tool",
  description: "示例工具",
  parameters: Type.Object({
    query: Type.String({ description: "搜索查询" }),
    limit: Type.Optional(
      Type.Number({
        minimum: 1,
        maximum: 100,
        default: 10,
      }),
    ),
    sort: Type.Optional(
      Type.String({
        enum: ["asc", "desc"],
        default: "asc",
      }),
    ),
  }),
  async execute(_toolCallId, params) {
    const query = params?.query ?? "";
    const limit = params?.limit ?? 10;
    const sort = params?.sort ?? "asc";

    // 执行工具逻辑...
    return {
      content: [{ type: "text", text: "结果..." }],
    };
  },
});
```

## 6.3 钩子 API

### 6.3.1 PluginHookName

所有可用的钩子事件。

```typescript
/**
 * 插件钩子名称
 */
type PluginHookName =
  // ========== 模型相关 ==========
  | "before_model_resolve" // 模型解析前
  | "before_prompt_build" // 提示词构建前
  | "before_agent_start" // Agent 启动前
  | "llm_input" // LLM 请求时
  | "llm_output" // LLM 响应时
  | "agent_end" // Agent 结束时
  // ========== 会话相关 ==========
  | "before_compaction" // 会话压缩前
  | "after_compaction" // 会话压缩后
  | "before_reset" // 会话重置前
  | "session_start" // 会话开始
  | "session_end" // 会话结束
  // ========== 消息相关 ==========
  | "message_received" // 收到消息
  | "message_sending" // 发送消息前
  | "message_sent" // 消息发送后
  // ========== 工具相关 ==========
  | "before_tool_call" // 工具调用前
  | "after_tool_call" // 工具调用后
  | "tool_result_persist" // 工具结果持久化前
  | "before_message_write" // 消息写入前
  // ========== 子代理相关 ==========
  | "subagent_spawning" // 子代理生成中
  | "subagent_delivery_target" // 子代理投递目标
  | "subagent_spawned" // 子代理已生成
  | "subagent_ended" // 子代理已结束
  // ========== Gateway 相关 ==========
  | "gateway_start" // Gateway 启动
  | "gateway_stop"; // Gateway 停止
```

### 6.3.2 钩子上下文类型

```typescript
/**
 * Agent 上下文（用于大多数 Agent 相关钩子）
 */
interface PluginHookAgentContext {
  agentId?: string;
  sessionKey?: string;
  sessionId?: string;
  workspaceDir?: string;
  messageProvider?: string;
  trigger?: "user" | "heartbeat" | "cron" | "memory";
  channelId?: string;
}

/**
 * 消息上下文
 */
interface PluginHookMessageContext {
  channelId: string;
  accountId?: string;
  conversationId?: string;
}

/**
 * 工具上下文
 */
interface PluginHookToolContext {
  agentId?: string;
  sessionKey?: string;
  sessionId?: string;
  runId?: string;
  toolName: string;
  toolCallId?: string;
}

/**
 * 会话上下文
 */
interface PluginHookSessionContext {
  agentId?: string;
  sessionId: string;
  sessionKey?: string;
}

/**
 * 子代理上下文
 */
interface PluginHookSubagentContext {
  runId?: string;
  childSessionKey?: string;
  requesterSessionKey?: string;
}

/**
 * Gateway 上下文
 */
interface PluginHookGatewayContext {
  port?: number;
}
```

### 6.3.3 钩子事件类型

```typescript
// ========== before_model_resolve ==========
interface PluginHookBeforeModelResolveEvent {
  /** 用户提示词 */
  prompt: string;
}

interface PluginHookBeforeModelResolveResult {
  /** 覆盖模型 */
  modelOverride?: string;
  /** 覆盖提供商 */
  providerOverride?: string;
}

// ========== before_prompt_build ==========
interface PluginHookBeforePromptBuildEvent {
  prompt: string;
  /** 会话消息 */
  messages: unknown[];
}

interface PluginHookBeforePromptBuildResult {
  /** 系统提示词 */
  systemPrompt?: string;
  /** 前置上下文 */
  prependContext?: string;
}

// ========== llm_input ==========
interface PluginHookLlmInputEvent {
  runId: string;
  sessionId: string;
  provider: string;
  model: string;
  systemPrompt?: string;
  prompt: string;
  historyMessages: unknown[];
  imagesCount: number;
}

// ========== llm_output ==========
interface PluginHookLlmOutputEvent {
  runId: string;
  sessionId: string;
  provider: string;
  model: string;
  assistantTexts: string[];
  lastAssistant?: unknown;
  usage?: {
    input?: number;
    output?: number;
    cacheRead?: number;
    cacheWrite?: number;
    total?: number;
  };
}

// ========== agent_end ==========
interface PluginHookAgentEndEvent {
  messages: unknown[];
  success: boolean;
  error?: string;
  durationMs?: number;
}

// ========== message_received ==========
interface PluginHookMessageReceivedEvent {
  from: string;
  content: string;
  timestamp?: number;
  metadata?: Record<string, unknown>;
}

// ========== message_sending ==========
interface PluginHookMessageSendingEvent {
  to: string;
  content: string;
  metadata?: Record<string, unknown>;
}

interface PluginHookMessageSendingResult {
  content?: string;
  cancel?: boolean;
}

// ========== message_sent ==========
interface PluginHookMessageSentEvent {
  to: string;
  content: string;
  success: boolean;
  error?: string;
}

// ========== before_tool_call ==========
interface PluginHookBeforeToolCallEvent {
  toolName: string;
  params: Record<string, unknown>;
  runId?: string;
  toolCallId?: string;
}

interface PluginHookBeforeToolCallResult {
  params?: Record<string, unknown>;
  block?: boolean;
  blockReason?: string;
}

// ========== after_tool_call ==========
interface PluginHookAfterToolCallEvent {
  toolName: string;
  params: Record<string, unknown>;
  runId?: string;
  toolCallId?: string;
  result?: unknown;
  error?: string;
  durationMs?: number;
}

// ========== session_start ==========
interface PluginHookSessionStartEvent {
  sessionId: string;
  sessionKey?: string;
  resumedFrom?: string;
}

// ========== session_end ==========
interface PluginHookSessionEndEvent {
  sessionId: string;
  sessionKey?: string;
  messageCount: number;
  durationMs?: number;
}

// ========== gateway_start ==========
interface PluginHookGatewayStartEvent {
  port: number;
}

// ========== gateway_stop ==========
interface PluginHookGatewayStopEvent {
  reason?: string;
}
```

## 6.4 HTTP 路由 API

### 6.4.1 OpenClawPluginHttpRouteParams

```typescript
/**
 * HTTP 路由配置
 */
interface OpenClawPluginHttpRouteParams {
  /** 路由路径（如 /my-plugin/webhook） */
  path: string;

  /** 处理函数 */
  handler: OpenClawPluginHttpRouteHandler;

  /** 认证类型 */
  auth: "gateway" | "plugin";

  /** 匹配模式 */
  match?: "exact" | "prefix";

  /** 是否替换已存在的路由 */
  replaceExisting?: boolean;
}

/**
 * HTTP 路由处理函数
 */
type OpenClawPluginHttpRouteHandler = (
  req: IncomingMessage,
  res: ServerResponse,
) => Promise<boolean | void> | boolean | void;

/**
 * 返回 true 表示请求已处理
 * 返回 false 或 void 表示继续下一个处理器
 */
```

### 6.4.2 HTTP 路由示例

```typescript
// 注册 HTTP 路由
api.registerHttpRoute({
  path: "/my-plugin/api",
  auth: "plugin", // 或 "gateway"
  match: "prefix", // 或 "exact"
  handler: async (req, res) => {
    // 设置响应头
    res.setHeader("Content-Type", "application/json");

    // 处理不同方法
    if (req.method === "GET") {
      res.statusCode = 200;
      res.end(JSON.stringify({ status: "ok" }));
      return true;
    }

    if (req.method === "POST") {
      // 解析请求体
      const body = await parseBody(req);

      // 处理请求
      const result = await processRequest(body);

      res.statusCode = 200;
      res.end(JSON.stringify(result));
      return true;
    }

    // 不支持的方法
    res.statusCode = 405;
    res.end(JSON.stringify({ error: "Method not allowed" }));
    return true;
  },
});
```

## 6.5 服务 API

### 6.5.1 OpenClawPluginService

```typescript
/**
 * 后台服务定义
 */
interface OpenClawPluginService {
  /** 服务 ID */
  id: string;

  /**
   * 启动函数
   * 在 Gateway 启动时调用
   */
  start: (ctx: OpenClawPluginServiceContext) => void | Promise<void>;

  /**
   * 停止函数
   * 在 Gateway 停止时调用
   */
  stop?: (ctx: OpenClawPluginServiceContext) => void | Promise<void>;
}

/**
 * 服务上下文
 */
interface OpenClawPluginServiceContext {
  /** OpenClaw 配置 */
  config: OpenClawConfig;

  /** 工作区目录 */
  workspaceDir?: string;

  /** 状态存储目录 */
  stateDir: string;

  /** 日志记录器 */
  logger: PluginLogger;
}
```

## 6.6 命令 API

### 6.6.1 OpenClawPluginCommandDefinition

```typescript
/**
 * 自动回复命令定义
 */
interface OpenClawPluginCommandDefinition {
  /** 命令名称（不带斜杠） */
  name: string;

  /** 命令描述（显示在帮助中） */
  description: string;

  /** 是否接受参数 */
  acceptsArgs?: boolean;

  /** 是否需要授权用户（默认 true） */
  requireAuth?: boolean;

  /** 命令处理函数 */
  handler: PluginCommandHandler;
}

/**
 * 命令上下文
 */
interface PluginCommandContext {
  /** 发送者 ID */
  senderId?: string;

  /** 渠道名称 */
  channel: string;

  /** 渠道 ID */
  channelId?: ChannelId;

  /** 发送者是否已授权 */
  isAuthorizedSender: boolean;

  /** 命令参数 */
  args?: string;

  /** 完整命令内容 */
  commandBody: string;

  /** OpenClaw 配置 */
  config: OpenClawConfig;

  /** 来源（From） */
  from?: string;

  /** 目标（To） */
  to?: string;

  /** 账户 ID */
  accountId?: string;

  /** 线程 ID */
  messageThreadId?: number;
}

/**
 * 命令处理函数
 */
type PluginCommandHandler = (
  ctx: PluginCommandContext,
) => PluginCommandResult | Promise<PluginCommandResult>;

/**
 * 命令结果
 */
type PluginCommandResult = ReplyPayload;
```

## 6.7 提供商 API

### 6.7.1 ProviderPlugin

```typescript
/**
 * 模型提供商插件
 */
interface ProviderPlugin {
  /** 提供商 ID */
  id: string;

  /** 显示标签 */
  label: string;

  /** 文档路径 */
  docsPath?: string;

  /** 别名 */
  aliases?: string[];

  /** 环境变量 */
  envVars?: string[];

  /** 模型配置 */
  models?: ModelProviderConfig;

  /** 认证方法 */
  auth: ProviderAuthMethod[];

  /** 格式化 API Key 显示 */
  formatApiKey?: (cred: AuthProfileCredential) => string;

  /** 刷新 OAuth 令牌 */
  refreshOAuth?: (cred: OAuthCredential) => Promise<OAuthCredential>;
}

/**
 * 认证方法
 */
interface ProviderAuthMethod {
  /** 方法 ID */
  id: string;

  /** 显示标签 */
  label: string;

  /** 提示文本 */
  hint?: string;

  /** 认证类型 */
  kind: "oauth" | "api_key" | "token" | "device_code" | "custom";

  /** 执行函数 */
  run: (ctx: ProviderAuthContext) => Promise<ProviderAuthResult>;
}

/**
 * 认证上下文
 */
interface ProviderAuthContext {
  /** OpenClaw 配置 */
  config: OpenClawConfig;

  /** Agent 目录 */
  agentDir?: string;

  /** 工作区目录 */
  workspaceDir?: string;

  /** 提示器 */
  prompter: WizardPrompter;

  /** 运行时环境 */
  runtime: RuntimeEnv;

  /** 是否远程环境 */
  isRemote: boolean;

  /** 打开 URL 函数 */
  openUrl: (url: string) => Promise<void>;

  /** OAuth 工具 */
  oauth: {
    createVpsAwareHandlers: typeof createVpsAwareOAuthHandlers;
  };
}

/**
 * 认证结果
 */
interface ProviderAuthResult {
  /** 认证配置文件 */
  profiles: Array<{
    profileId: string;
    credential: AuthProfileCredential;
  }>;

  /** 配置补丁 */
  configPatch?: Partial<OpenClawConfig>;

  /** 默认模型 */
  defaultModel?: string;

  /** 备注信息 */
  notes?: string[];
}
```

## 6.8 渠道 API

### 6.8.1 ChannelPlugin

```typescript
/**
 * 渠道插件定义
 */
interface ChannelPlugin {
  /** 渠道 ID */
  id: string;

  /** 元数据 */
  meta: {
    id: string;
    label: string;
    selectionLabel?: string;
    docsPath?: string;
    docsLabel?: string;
    blurb?: string;
    order?: number;
    aliases?: string[];
    preferOver?: string[];
    detailLabel?: string;
    systemImage?: string;
  };

  /** 能力定义 */
  capabilities: {
    chatTypes: ("direct" | "group" | "channel" | "thread")[];
    polls?: boolean;
    reactions?: boolean;
    edit?: boolean;
    unsend?: boolean;
    reply?: boolean;
    effects?: boolean;
    groupManagement?: boolean;
    threads?: boolean;
    media?: boolean;
    nativeCommands?: boolean;
    blockStreaming?: boolean;
  };

  /** 配置处理 */
  config: {
    listAccountIds: (cfg: OpenClawConfig) => string[];
    resolveAccount: (cfg: OpenClawConfig, accountId?: string) => AccountConfig;
  };

  /** 出站消息处理 */
  outbound: {
    deliveryMode: "direct" | "gateway" | "hybrid";
    chunker?: ((text: string, limit: number) => string[]) | null;
    chunkerMode?: "text" | "markdown";
    textChunkLimit?: number;
    pollMaxOptions?: number;
    resolveTarget?: (params: {
      cfg?: OpenClawConfig;
      to?: string;
      allowFrom?: string[];
      accountId?: string | null;
      mode?: ChannelOutboundTargetMode;
    }) => { ok: true; to: string } | { ok: false; error: Error };
    sendPayload?: (ctx: ChannelOutboundPayloadContext) => Promise<OutboundDeliveryResult>;
    sendText?: (ctx: ChannelOutboundContext) => Promise<OutboundDeliveryResult>;
    sendMedia?: (ctx: ChannelOutboundContext) => Promise<OutboundDeliveryResult>;
    sendPoll?: (ctx: ChannelPollContext) => Promise<ChannelPollResult>;
  };

  /** 入站消息处理（可选） */
  inbound?: {
    handleWebhook?: (
      req: IncomingMessage,
      res: ServerResponse,
      cfg: OpenClawConfig,
    ) => Promise<InboundMessage | void>;
  };

  /** Gateway 集成（可选） */
  gateway?: {
    startAccount?: (ctx: ChannelGatewayContext) => Promise<unknown>;
    stopAccount?: (ctx: ChannelGatewayContext) => Promise<void>;
  };

  /** 设置向导（可选） */
  setup?: {
    configure?: (ctx: SetupContext) => Promise<{ cfg: OpenClawConfig }>;
    configureInteractive?: (ctx: SetupContext) => Promise<SetupResult>;
    configureWhenConfigured?: (ctx: SetupContext) => Promise<SetupResult>;
  };

  /** 安全策略（可选） */
  security?: {
    getDmPolicy?: (account: AccountConfig) => DmPolicy;
  };

  /** 状态检查（可选） */
  status?: {
    checkHealth?: (account: AccountConfig) => Promise<HealthStatus>;
  };
}
```

## 6.9 运行时 API

### 6.9.1 PluginRuntime

```typescript
/**
 * 运行时 API
 */
interface PluginRuntime {
  /** 文本转语音 */
  tts: {
    /**
     * 将文本转换为语音（电话质量）
     * @param params 参数
     * @returns PCM 音频数据和采样率
     */
    textToSpeechTelephony: (params: {
      text: string;
      cfg: OpenClawConfig;
    }) => Promise<{
      audio: Buffer;
      sampleRate: number;
    }>;
  };

  /** 语音转文本 */
  stt: {
    /**
     * 转录音频文件
     * @param params 参数
     * @returns 转录文本
     */
    transcribeAudioFile: (params: {
      filePath: string;
      cfg: OpenClawConfig;
      mime?: string;
    }) => Promise<{
      text?: string;
    }>;
  };

  /** 工具工厂 */
  tools: {
    /**
     * 创建内存搜索工具
     */
    createMemorySearchTool: (params: {
      config: OpenClawConfig;
      agentSessionKey?: string;
    }) => AnyAgentTool | null;

    /**
     * 创建内存获取工具
     */
    createMemoryGetTool: (params: {
      config: OpenClawConfig;
      agentSessionKey?: string;
    }) => AnyAgentTool | null;

    /**
     * 注册内存 CLI 命令
     */
    registerMemoryCli: (program: Command) => void;
  };

  /** 日志函数 */
  log: (message: string) => void;
}
```

## 6.10 SDK 导入路径

```typescript
// 核心 API
import type { OpenClawPluginApi } from "openclaw/plugin-sdk/core";
import { emptyPluginConfigSchema } from "openclaw/plugin-sdk/core";

// Telegram 渠道 SDK
import type { OpenClawPluginApi } from "openclaw/plugin-sdk/telegram";
import { emptyPluginConfigSchema } from "openclaw/plugin-sdk/telegram";

// Discord 渠道 SDK
import type { OpenClawPluginApi } from "openclaw/plugin-sdk/discord";

// Slack 渠道 SDK
import type { OpenClawPluginApi } from "openclaw/plugin-sdk/slack";

// Signal 渠道 SDK
import type { OpenClawPluginApi } from "openclaw/plugin-sdk/signal";

// iMessage 渠道 SDK
import type { OpenClawPluginApi } from "openclaw/plugin-sdk/imessage";

// WhatsApp 渠道 SDK
import type { OpenClawPluginApi } from "openclaw/plugin-sdk/whatsapp";

// LINE 渠道 SDK
import type { OpenClawPluginApi } from "openclaw/plugin-sdk/line";
```

---

**上一章**：[进阶指南](./05-进阶指南.md) | **下一章**：[实践示例](./07-实践示例.md)
