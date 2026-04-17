---
target_table: system_designs
target_slug: interview-rate-limiter
target_column: overview
---
## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个**限流器 (Rate Limiter)**：在给定时间窗口内，限制客户端（用户/IP/API Key）
对服务的请求次数。当请求超过阈值时，多余的请求被拒绝并返回 **HTTP 429 (Too Many
Requests)**。限流器通常部署在 **API Gateway** 层，保护后端服务免受流量洪峰和滥用。

### 功能性需求 (Functional Requirements)

1. **请求计数 (Request Counting)**：按客户端标识（user ID / IP / API Key）准确统计请求数
2. **限流决策 (Rate Decision)**：根据预定义规则判断是否允许当前请求通过
3. **限流规则引擎 (Rule Engine)**：支持灵活配置限流规则（每分钟 N 次、每秒 M 次等）
4. **HTTP 响应头 (Response Headers)**：返回 `X-RateLimit-Limit`、`X-RateLimit-Remaining`、`X-RateLimit-Retry-After` 等标准头
5. **多维度限流 (Multi-dimension)**：支持按用户、API 端点、IP 等不同维度独立限流

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**：99.99%（限流器故障不应导致后端服务不可用）
- **延迟 (Latency)**：P99 < 1ms（限流检查在请求关键路径上，必须极快）
- **一致性 (Consistency)**：在分布式环境下允许轻微不精确（偶尔多放几个请求可接受），但不能严重超限
- **可扩展性 (Scalability)**：支撑百万级 QPS（作为所有 API 请求的入口层）
- **容错性 (Fault Tolerance)**：限流器不可用时，应该 **放行 (fail-open)** 而非 **拒绝 (fail-closed)**

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 限流器部署在客户端还是服务端？** -- WHY: 客户端限流容易被绕过（恶意用户可直接调 API），服务端 / API Gateway 限流是标准做法。确认部署位置决定整体架构。

2. **Q: 需要支持哪些限流维度？按用户、按 IP、按 API 端点、还是组合？** -- WHY: 不同维度对应不同的 key 设计（`user:123:endpoint:/api/orders` vs `ip:1.2.3.4`），影响存储结构和规则引擎复杂度。

3. **Q: 限流规则是硬编码还是动态可配置？** -- WHY: 如果需要运行时热更新规则（如促销期间临时提高某 API 限额），需要独立的规则存储 + 推送机制，增加架构复杂度。

4. **Q: 分布式环境下对精确度的要求是什么？允许偶尔超限 1-2% 吗？** -- WHY: 严格精确需要全局锁或强一致存储（性能差）；允许轻微不精确可以用本地计数器 + 定期同步（性能好得多）。

5. **Q: 限流器故障时应该放行还是拒绝？** -- WHY: **Fail-open** 意味着限流器故障时所有请求放行（可能导致后端过载）；**Fail-closed** 意味着拒绝所有请求（用户体验极差）。大多数生产系统选择 fail-open。

6. **Q: 是否需要支持不同用户层级的差异化限流（如免费用户 vs 付费用户）？** -- WHY: 差异化限流需要规则引擎支持用户属性查询，增加每次限流检查的延迟。

7. **Q: 被限流的请求需要排队等待还是直接拒绝？** -- WHY: 排队（如 **Leaky Bucket**）适合平滑流量；直接拒绝（如 **Token Bucket**）适合保护后端。场景不同选择不同。

### 范围外 (Out of Scope)

- DDoS 防护（由 CDN/WAF 层处理）
- 用户认证 / 鉴权系统（假设已有，限流器只读取身份信息）
- 计费 / 配额管理（限流器不负责计费，只做流量控制）
- 客户端限流 SDK（只设计服务端限流器）
