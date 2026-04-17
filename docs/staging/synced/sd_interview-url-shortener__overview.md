---
target_table: system_designs
target_slug: interview-url-shortener
target_column: overview
---
## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个类似 **TinyURL** / **bit.ly** 的短链接服务：用户提交一个长 URL，系统
返回一个唯一的短 URL；当访问短 URL 时，系统将请求重定向到原始长 URL。

### 功能性需求 (Functional Requirements)

1. **URL 缩短 (Shorten)**：给定一个长 URL，生成一个唯一的短链接
2. **URL 重定向 (Redirect)**：访问短链接时，重定向到原始长 URL
3. **自定义别名 (Custom Alias)**：用户可选择自定义短链接后缀（如 `short.url/my-brand`）
4. **过期 / TTL**：短链接可设置过期时间，过期后返回 404
5. **分析统计 (Analytics)**：记录每次点击的基本信息（时间、来源、地理位置）

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**：99.99%（重定向是核心路径，必须极高可用）
- **延迟 (Latency)**：重定向 P99 < 10ms（读路径）；缩短 P99 < 100ms（写路径）
- **一致性 (Consistency)**：短链接创建后必须立即可用（强一致）；分析数据可接受最终一致
- **可扩展性 (Scalability)**：支撑 1 亿 DAU，读写比 100:1
- **持久性 (Durability)**：短链接一旦创建，在 TTL 内不可丢失

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 短链接长度有限制吗？** -- WHY: 决定编码空间大小和哈希策略。7 字符 Base62 = $62^7 \approx 3.5 \times 10^{12}$ 个唯一值，足够使用数十年。

2. **Q: 是否需要支持同一长 URL 的去重（相同长 URL 返回相同短链接）？** -- WHY: 如果需要去重，需要额外的长 URL -> 短 URL 反向索引，增加写路径复杂度。

3. **Q: 重定向应使用 301 还是 302？** -- WHY: **301 (Moved Permanently)** 浏览器会缓存，减少服务端流量但丢失分析数据；**302 (Found)** 每次都回到服务端，保留完整分析。如果分析重要，选 302。

4. **Q: 短链接是否需要支持删除/更新？** -- WHY: 如果支持更新，缓存失效策略会更复杂（需要主动清除 CDN 缓存）。

5. **Q: 分析需要实时还是近实时？** -- WHY: 实时分析需要流处理（如 Kafka + Flink）；近实时可用批处理（更简单）。

6. **Q: 预期的 URL 创建速率是多少？** -- WHY: 影响 ID 生成器的吞吐量需求和数据库写入压力。

7. **Q: 是否需要防滥用（恶意 URL 检测）？** -- WHY: 如果需要，写路径需要集成 URL 安全检查服务（如 Google Safe Browsing API），增加写延迟。

### 范围外 (Out of Scope)

- 用户认证 / 账户系统（假设已有）
- 付费计划 / 配额管理
- URL 内容预览（Open Graph 元数据获取）
- 多语言 / 国际化界面

<!-- T-P1-213 dogfood sync marker -->
