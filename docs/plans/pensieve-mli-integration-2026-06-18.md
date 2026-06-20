# Plan — 把 MLInterviewPrep 集成进 Pensieve

> 状态：**已落库到 pensieve `.claude/tasks.db`（2026-06-18，全部 `status=blocked`/`pending`，autorun 不可拾取）。**
> 经过三层评审（3 只读研究 agent → 2 路对抗自审 → 用户第三方评判），结论已折入。
> 决策已定：统一启动器 + 双进程 + iframe 嵌入 + 两库分离、不改包名。
>
> **pensieve 任务映射**：T1=`T-P1-433`、T2=`T-P1-434`、T3=`T-P2-435`、T4a=`T-P2-436`(MLI 侧/跨 repo)、T4b=`T-P3-437`(parked)。
> tasks.db 内的 description 是**吸收用户评判后的最终执行规格**（本 md 为决策记录，二者如有出入以 tasks.db 为准）。
>
> **第三方评判吸收的 8 处改动**（覆盖下文对应小节）：
> 1. 端口保持常量、v1 不 env 化（除非先建 dev.py+vite.config+前端 env 三处共享的单一端口源）—— 折入 T1。
> 2. supervisor 崩溃策略钉死：独立 + fail-loud + v1 不自动重启 + 宿主永活（不采纳 review 的"自动重启"）—— 折入 T1，开放决策 #1 取消。
> 3. T3 维持 P2，不升 P1。
> 4. T1 AC2 加打一个真实业务 endpoint（`/api/companies`）证明读写链路，而非只 `/health`。
> 5. T2 不写 iframe 内部 DOM 的 Playwright 断言（同源策略），KG 可见留手动冒烟。
> 6. autorun 爆炸半径前移为一等护栏：全部任务 blocked 落库、需人工 sign-off。
> 7. iframe 集成天花板写死成"已知限制"（无共享 auth/深链/主题、parent↔iframe 不可互访）+ iframe/​/mli-api 双源一致性风险 —— 折入 T2/T3。
> 8. 拆 T4：T4a(加稳定键，MLI 侧、近期做、自身有价值) 独立于 T4b(日历桥，parked)。

---

## 0. 拓扑与端口全景（已核实无冲突）

```
python scripts/dev.py   (在 pensieve 根目录运行 —— 唯一统一入口)
 ├─ pensieve 后端  uvicorn :8200  → data/pensieve.dev.db   (带 schema 漂移门 init_substrate)
 ├─ MLI 后端       uvicorn :8100  → MLI/data/mle_prep.db   (启动自建表 + 自 seed)
 ├─ pensieve 前端  Vite   :5273   /api      → :8200
 └─ MLI 前端       Vite   :5173   /api      → :8100        ← iframe 指向此处
                                  (T3 另加) pensieve :5273  /mli-api → :8100
```

设计中枢的两条不变量（决定了为什么是"双进程+两库"而非"并入"）：

1. **包名冲突**：两个项目都把自己 import 为 `src.backend.*`。同一进程无法加载两个顶层 `src` 包
   → 任何单进程方案都要改包名。**双进程**（各自 cwd / 各自 sys.path）天然绕开。
2. **Pensieve 单 substrate + 漂移门**：`init_substrate` 会拒绝在"被污染"的库上启动；但 pensieve 已并存
   多个独立小库（`sanctum.db`/`jobs.db`/`telemetry.db`，各自 engine+文件）。先例 = **MLI 保留自己的库**，
   绝不并入 substrate。

---

## 1. 自审折入的关键事实（fact-check 全部 CONFIRMED；2 处实质 flag）

| # | 核查项 | 结论 |
|---|--------|------|
| 1 | pensieve `dev.py` 现为单后端(8200)+单前端；eviction/health/stream/watch 辅助按端口参数化 | CONFIRMED，但 `main()` 有 pensieve 专属单后端耦合 → **T1 复杂度上调 L** |
| 2 | MLI 以 `python -m uvicorn src.backend.main:app --port 8100`、仅靠 `cwd=MLI根` 即可 import | CONFIRMED |
| 3 | MLI 的 `sqlite:///data/mle_prep.db` 相对 cwd 解析 | CONFIRMED（cwd 错则建错库 —— T1 要害） |
| 4 | MLI 无 `ANTHROPIC_API_KEY` 也能启动（key 仅惰性 gate LLM 功能） | CONFIRMED（`/api/health` 裸启可用） |
| 5 | pensieve 导航=`AppShell.tsx:44-59` 的 `SHELL_NAV`；路由=`router.tsx:25-68`；页面在 `pages/` | CONFIRMED |
| 6 | pensieve Vite 代理 `vite.config.ts:18-31` 仅 `/api`→8200、IPv4 钉死；MLI 前端=5173≠pensieve 5273 | CONFIRMED |
| 7 | **iframe 风险**：MLI 不发 `X-Frame-Options`/CSP `frame-ancestors` | CONFIRMED（5273 嵌 5173 **开箱可用**，无需改 header） |
| 8 | pensieve `apple_writer_v0` 有 `create_event`/`delete_event`/`pensieve_uid_for_item`；MLI 有 `interview_events` | CONFIRMED；**但 MLI `interview_events` 无稳定业务键**（仅自增 id，re-seed 会换 id）→ **T4 幂等受阻** |

合法 `NavIconName`（9 个，T2 用）：`home / inbox / cogitator / crystal / offload / people / archive / schedule / themes`。新 tab 须复用其一或新增图标（同时改 union 与 `ICON_PATHS`）。

---

## T1 — 统一开发启动器

- **优先级**：P1 ｜ **复杂度**：L ｜ **依赖**：无

### Summary
改造 pensieve `scripts/dev.py`：从"单后端+单前端"重构为按"服务清单"管理，额外拉起 MLI 后端(8100)+前端(5173)。一条 `python scripts/dev.py` 起全部四个；Ctrl+C 全部干净退出。

### Context
用户首要诉求 —— "一起被后端拉起 / 统一入口"。现状 pensieve `dev.py` 只起自己那对，MLI 是独立栈。
研究确认 `dev.py` 的 eviction/health/stream 辅助已按端口参数化、docstring 自述 "mirrors the MLI dev.py" → 属扩展非重写。

### Grounding Assets
- `pensieve/scripts/dev.py:646-718`（binds —— 现有 backend/frontend 的 Popen 站点、`BACKEND_PORT=8200`、watch loop:745-757）
- `pensieve/scripts/dev.py:497-520, 596-621`（binds —— `_preflight_schema` / `_run_db_probes`，**必须门控为 pensieve-only**）
- `MLInterviewPrep/scripts/dev.py:295-311`（REFERENCE —— 复刻的 MLI 启动命令、`cwd=PROJECT_ROOT`、`BACKEND_PORT=8100`）

### Acceptance Criteria
- [ ] **AC1（cwd 正确性 —— 要害）**：新增 `PENSIEVE_MLI_ROOT`（env，默认同级 `../MLInterviewPrep`）；以 `cwd=MLI_ROOT` spawn MLI uvicorn。预言：**先清空两处 db 路径**，跑后断言 `MLI/data/mle_prep.db` mtime 前进 **且** `pensieve/data/mle_prep.db` 不存在。
- [ ] **AC2（旅程 + 有界健康等待）**：跑 `dev.py` → 四端口起；`:8200/api/health` 与 `:8100/api/health` 在**每后端 0.5s×最多 30s** 的有界轮询内均 200。
- [ ] **AC3（探针门控 —— 正确性）**：pensieve 专属探针（`_preflight_schema`/`_run_db_probes`/banner，依赖 `init_substrate` 与 `/api/admin/schema-health`，**MLI 没有这些**）只对 pensieve 后端跑；MLI 服务项仅挂通用 `/api/health` 等待。预言：MLI 启动日志**不含** schema-health 探针调用。
- [ ] **AC4（降级，三分支全覆盖）**：① MLI_ROOT 缺失 ② MLI_ROOT 指向无效目录 ③ MLI 依赖缺失/启动崩溃 —— 三者都 WARN 且**宿主那对仍 200**（MLI 是附加项，永不阻塞宿主）。
- [ ] **AC5（跨平台退出）**：分平台指定信号（POSIX `SIGINT` vs Windows `taskkill /T` / 进程组）。预言 = 信号后 N 秒内四端口**全部拒连**、无孤儿。
- [ ] **AC6（端口清理）**：起前若 8100/5173 被占 → 复用 `evict_stale_backend(port=…)` 杀旧 PID 再绑。预言 = 放占位进程占 8100 → 启动器清掉并成功绑定。

### Technical Approach
把单一 `backend_proc`/`BACKEND_PORT` 抽成服务清单 `[{name, cmd, cwd, port, health, pensieve_probes:bool}]`；循环 spawn + 有界 health-wait + 每服务 stream 线程；watch loop 改为遍历清单。仅改 `pensieve/scripts/dev.py`。MLI 自己的 `dev.py` 不动（仍是其独立入口）。**绝不调用 MLI 的 `dev.py`**（双重 eviction 互杀）—— 直接 spawn uvicorn。

### Edge Cases
Windows taskkill 子 PID 扫除（现有逻辑按端口复用）；cwd 必须绝对路径；MLI deps 未装 → uvicorn import 失败应 fail-fast 为该服务的错误、不拖垮其他；health-wait 超时预算每后端独立。

### 评审分歧裁决（保留为单任务而非拆分）
refuter 建议拆 "spawn+health" 与 "teardown+eviction"。**保留为一个 L 任务**：eviction 在 spawn 前、teardown 在 spawn 后，二者夹着 spawn；拆开会留下"能起但起前不清/起后不收"的破中间态。改用分组 AC（A=AC1-3 / B=AC4 / C=AC5-6）保证可分组测试。

### Open Decisions（见文末汇总 #1）
进程崩溃策略：带崩整体 vs 仅挂那一格（建议：独立）。

---

## T2 — pensieve "面试" 导航 tab（iframe 嵌入）

- **优先级**：P1 ｜ **复杂度**：M ｜ **依赖**：T1（软）

### Summary
pensieve `AppShell` 加顶层 "面试" 项 → `/ml-interview` 路由 → `MlInterviewPage`，内嵌 MLI SPA 的 iframe，复用 MLI 现有 KG/看板/笔记 UI（零重写）。

### Context
用户选 iframe 方案。研究确认导航=`SHELL_NAV` 数组、路由表、页面目录均如上；iframe 嵌入开箱可用。

### Grounding Assets
- `pensieve/src/frontend/src/components/AppShell.tsx:44-59`（binds —— `SHELL_NAV` 形状、`icon: NavIconName`）
- `pensieve/src/frontend/src/router.tsx:25-68`（binds —— 路由表）
- `pensieve/src/frontend/src/components/NavIcon.tsx:23-32`（binds —— 9 个合法图标名）

### Acceptance Criteria
- [ ] **AC1**：新增 `SHELL_NAV` 项（`to:"/ml-interview"`）；点击导航过去。
- [ ] **AC2**：`/ml-interview` 路由 + `MlInterviewPage` 挂载。
- [ ] **AC3（旅程）**：点"面试" → iframe 渲染 MLI 应用（KG/看板/笔记可见可交互）。手动冒烟：MLI 仪表盘在 pensieve 内可见。
- [ ] **AC4（双分支 + 可靠探测）**：src 取自 `import.meta.env.VITE_MLI_URL`（默认 `http://localhost:5173`，不硬编码）。**跨域 iframe 的 `onerror` 不可靠** → 改用对 `VITE_MLI_URL` 的 `fetch` 预检+超时。MLI 可达 → iframe 在、占位符不在 DOM；MLI 不可达 → N 秒内 DOM 出现"MLI 未运行"占位符、不显示坏 iframe。
- [ ] **AC5（无漂移）**：图标用合法 `NavIconName`（不新增资源则复用 9 个之一）；`npm run build`（`tsc -b`）通过。

### Technical Approach
改 `AppShell.tsx`（导航项）、`router.tsx`（路由+import）、新增 `pages/MlInterviewPage.tsx`（iframe + fetch 预检 → 占位符）。配置走 Vite env。共 3 文件。

### Edge Cases
X-Frame-Options 已确认非问题（MLI dev 不发）；iframe 在可缩放 AppShell 内的全高布局；跨域（5273↔5173）意味着 parent↔iframe 无 JS 互访 —— v1 可接受（设计上本就无共享状态）。

### Open Decisions（见文末汇总 #2、#3）
图标/标签选择；prod 形态（dev 指 5173 Vite，prod MLI 前端需先 build+托管）。

---

## T3 — `/mli-api` Vite 代理接缝

- **优先级**：P2 ｜ **复杂度**：S ｜ **依赖**：T1（硬）

### Summary
pensieve `vite.config.ts` 代理加 `"/mli-api" → 127.0.0.1:8100`（rewrite 去 `/mli-api` 前缀 → `/api`）。

### Context
纯 iframe 的 T2 **不需要**它（iframe 加载 MLI 自己的前端，走其自有 /api→8100）。T3 是给 pensieve **原生代码**调 MLI 接口的接缝 —— phase 2（首页露出"下一场面试"）与 T4 日历桥的前置。低成本，先建好。

### Grounding Assets
- `pensieve/src/frontend/vite.config.ts:18-31`（binds —— 代理块，现仅 `/api`→8200、IPv4 钉死）

### Acceptance Criteria
- [ ] **AC1**：`curl :5273/mli-api/health`（pensieve Vite 宿主）返回 **MLI** 的 health JSON —— 断言 body 形状（`service` 字段为 MLI 而非 pensieve），不止 200。
- [ ] **AC2（无回归 + 无遮蔽）**：现有 `/api`→8200 不变；新增的唯一路由就是 `/mli-api`，不遮蔽任何 pensieve `/api` 路由。
- [ ] **AC3（rewrite 正确）**：嵌套路径与末尾斜杠均对（`/mli-api/foo/bar`、`/mli-api/`）。
- [ ] **AC4（MLI 宕机分支）**：代理到死的 8100 → 有界连接错误（502/ECONNREFUSED），**不挂起**。
- [ ] **AC5**：IPv4 钉死 127.0.0.1（与文件内 Windows-IPv6 教训一致）。

### Technical Approach
仅改 `pensieve/src/frontend/vite.config.ts` 一处。

### Edge Cases
rewrite 必须 strip（MLI 内部无 `/mli-api` 前缀）；CORS 不涉及（服务端代理）。

---

## T4 — 面试日程 → 日历桥（你的问题 1）

- **优先级**：P3（**低**）｜ **复杂度**：M ｜ **依赖**：T1、T3，+「MLI 稳定键」前置（若选幂等路线）

### Summary
复用 pensieve 已有的 `apple_writer_v0.create_event` 写回原语，把 MLI `interview_events` 推到日历。
（你自述优先级很低、目前无面试。）

### Context
pensieve 已有完整日历机制：CalDAV/iCal 读（Google Cal / Apple）+ 写回 Apple Calendar。MLI 持有 `interview_events`。
→ 本质是接到既有原语，而非新建。

### 🚨 拦路问题（fact-check claim 8）
MLI `interview_events` **无稳定业务键** —— 唯一键是自增 `id`，导入路径"always insert, no dedup"，re-seed 换新 id。
而 pensieve 幂等写回靠确定性 UID（`<item_id>@pensieve`）。→ "同步两次只产生一个日历事件"在 MLI 现状下**做不到**。
**首要开放决策**（文末 #4）：先给 `interview_events` 加稳定键/去重（换幂等+可删改），还是接受非幂等"只新增"。

### Grounding Assets
- `pensieve/src/backend/services/apple_writer_v0.py:131,158,218`（binds —— `pensieve_uid_for_item` / `create_event` / `delete_event`）
- `pensieve/src/backend/routers/calendar.py:417-509`（REFERENCE —— accept→push 流程范式）
- `MLInterviewPrep/src/backend/models/timeline.py:30-45`（REFERENCE —— `interview_events`，仅自增 id）

### Acceptance Criteria（待 #4 决策后定稿）
- [ ] **AC1**：pensieve 侧服务**经 /mli-api HTTP** 读 `interview_events`（不跨库直连），用稳定键派生确定性 UID 调 `create_event`；同步两次 → 一个事件。
- [ ] **AC2（双分支）**：Apple writer 未配置 → 记日志的 no-op、不报错；配置但中途写失败 → 幂等可重试（重同步收敛）、不产生重复。
- [ ] **AC3（对 MLI 只读）**：预言 = 全程仅 HTTP、不打开 MLI sqlite 句柄、MLI 库行数/mtime 不变。
- [ ] **AC4（时区）**：显式钉死（`scheduled_at` 源时区 → 日历时区），断言生成事件 start = 源时刻。

### Technical Approach
新增 `pensieve/src/backend/services/mli_calendar_bridge.py`（经 HTTP 读 8100，保持双进程/两库边界）；复用 `apple_writer_v0`；可选手动"同步面试"按钮或 routine。

### Edge Cases
时区（复用 pensieve datetime 契约）；无 Apple 凭据 → skip；MLI 离线 → skip。

### Open Decisions（文末 #4、#5）
幂等前置；方向（单向 vs 双向）与触发（手动 vs 定时）。

---

## 推荐顺序
**T1 → T2** 即达成"统一入口"地板（一条命令、外壳内的面试 tab）。**T3** 低成本接缝，建议顺手。
**T4** 留到真有面试且定了开放项再做。

---

## 🔲 开放决策汇总（只有你能拍板）

1. **T1 进程崩溃策略**：带崩整体 vs 仅挂那一格。（建议：**独立** —— MLI 挂 ≠ pensieve 挂）
2. **T2 图标 & 标签**：复用 9 个之一（`schedule`？`archive`？）vs 新画 MLI 图标；标签"面试" vs "ML 面试准备"。
3. **T2 prod 形态**：dev 下 iframe 指 MLI Vite :5173；prod 下 MLI 前端无 Vite，需 build+托管。
   （建议：**v1 仅 dev**，prod 托管另立任务）
4. **T4 幂等前置**：给 `interview_events` 加稳定业务键/去重 vs 接受非幂等"只新增"。
   （建议：**现在无面试 → 先不做 T4**；真做时优先补稳定键）
5. **T4 方向 & 触发**：单向 vs 双向；手动 vs 定时。
   （建议：**v1 单向 + 手动**，与 pensieve "对外日历只读、仅 Apple writer 写"不变量一致）
6. **任务落库去向**：写进 **pensieve 的 tasks.db**（代码主要落那、执行也在那）还是 MLI 的？
   ⚠️ 两个 repo 都有 autonomous runner，**写入即可能被自动拾取执行** —— 故本稿先存为 md，待你确认去向+点头后再投射。
