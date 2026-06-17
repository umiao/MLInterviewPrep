# HANDOFF — MLInterviewPrep

> 新 session 从这里接续。**这是活文档**:就地 edit 成当前真相(不是 append-only;只有 `PROGRESS.md` 才 append-only)。
> 详细命令见 `CLAUDE.md`,任务权威 spec 取 DB(`python .claude/hooks/task_db.py get <ID>`),经验教训见 `LESSONS.md`。
> 维护约定:**始终维护这同一个文件**;整条 workstream 落地后,把对应段落就地改成「已完成」或删掉,不另起新 handoff。

## 一句话

全栈 **ML/SDE 面试备战平台**(FastAPI + SQLAlchemy + SQLite WAL / React 19 + TS + Tailwind / Anthropic Claude API / pytest 512+)。范式:**内容=一等对象**,专题/主题是多对多 link(改导航/主题永不动内容页)。五种抽屉 URI:`lc/db/cd/sd/kg`。

## 位置 & 运行时
- 目录:`Gen_AI_Proj/MLInterviewPrep`(有自己的 `.claude/tasks.db`)。Python:`/c/Anaconda/python.exe`。
- Windows 控制台 cp1252:一次性脚本前置 `PYTHONUTF8=1 PYTHONIOENCODING=utf-8`。
- ⚠️ 计费:`claude -p`/autorun 走**单独 API 计费池**(非订阅),见 root memory `june15_programmatic_billing_split`。
- 内容/DB 改动遵循 root memory `mli_content_workflow`(7 步改写、sync-ALL-surfaces、五抽屉 URI、MLSD golden 约束)+ `CLAUDE.md` 的 Surface Identification 表(改 DB 前先 widget→queryKey→endpoint→table 映射)。

## Backlog 现状(2026-06-17 核实 + 当日 autorun 后更新)
70 任务:**17 done / 53 未完**(876/878/916 当日 autorun 完成)。53 里绝大多数被 gate/直列链锁住的 `blocked+pending`。

### ✅ state 卫生债已清零(2026-06-17)
曾有 **4 个** `status='active'` 但 `state=None`(picker 不可视:912/918/905/916)。已全部正规化成 `state='ready'`,**现在 `state=None` 计数 = 0**。非完成任务现仅两态:`active+ready`(17,可拣)/ `blocked+pending`(38,dep 门控或 PARK)。
> 有意 PARK 的形态是 `status='blocked' + state='pending'`(picker 用 `state='ready'` 过滤);`state=None` 是异常不是 PARK,已根除。

### 2026-06-17 autorun 结果(scoped DEBT 批跑,两轮)
把 autorun-safe 任务 scope 进 picker(其余临时 park),跑 `autonomous_run.sh`:
- ✅ **T-P1-876**(`9eceb95`)语法修复 · **T-P2-878**(`421e9c9`)发现 pyproject 4 dev deps 其实已同步=audit 误报,改加 dep-sync 回归测试 · **T-P3-916**(`3dd12df`)只读决策 doc。三个均完成 + push。
- Round1(876+878+905+916)Session 2 撞 **Claude session 额度耗尽**只做完 876;额度恢复后 Round2 补做 878+916。
- ⏸ **T-P2-905(归档 PROGRESS.md)仍未做**:它会**重构 PROGRESS.md 结构**,而前任遗留的 **Lyra ad-hoc 待决条目**(见下)还挂在 PROGRESS.md 未提交 → 现在跑 905 会把归档搞乱。**905 阻塞于 Lyra 决定**,等 Lyra 处置后再跑。
- 跑后已恢复全部 park、清零 state=None。
> ⚠️ autorun 不能指定目标,只拣最高优先级 pickable。非 autorun-safe 任务(见下)若不 park 会被先拣中并撞 sensitive-gate / manual-smoke。重跑前须重新 park 非安全任务(含已恢复成 ready 的 912/918),或逐个 supervised。

### 前任遗留待决:Lyra ad-hoc seed(阻塞 905)
`scripts/_add_lyra_jacqueline_2026-05-27.py`(未跟踪)+ PROGRESS.md 一条 2026-05-26 ad-hoc 条目,前任标注「等用户浏览器确认 + 提交决定」。本 session autorun 期间多次 stash/pop 隔离它,未提交、未改动。**待用户拍**:提交 / 丢弃 / 继续保留待决。处置后 905 才好跑。

### 还能直接拣的(state=ready 且依赖满足)
- ~~876 / 878 / 916~~ ✅ 已完成(2026-06-17)
- **T-P2-877**〔DEBT,M〕876 修后 `ruff check scripts/` 残 ~193(60 可自动修;剩 N806/B905/E741 旧 util 改名有语义风险需人审)— **非纯 autorun**(尾部需人审)
- **T-P2-905**〔DEBT,S〕归档 PROGRESS.md — **阻塞于上面的 Lyra 决定**
- **T-P2-879**〔DEBT,S〕`shared/hooks/task_store.py:145` SIM105 → `contextlib.suppress` — **改活循环用的 task 基建,supervised**
- **T-P2-880**〔SYNC,S〕从 template 引入 study-review skill(拷前人审 scope)
- **T-P1-881**〔Meta-MLSD,S〕sd42 archetype 迁移 oral_narrative(sd43/44 已折进 894/895)
- **T-P1-908**〔ML-Infra-LLM,M〕加「ML Infra · LLM」SD tab + carve [300,400) + Pinterest 收成 [199,300) 防泄漏(其后 909 seed golden)
- **T-P1-921**〔WSH-E1,M〕drawer_nav 抽列 + 4 retrofit 退役 + E2 决策门

### 各簇详解
- **DEBT/SYNC**(876–880):技术债,直列,不碰内容,判断少 → **autonomous 批跑一扫**。
- **CHEATSHEET 1–9**(全锁 641):641=schema+API(加 `cheat_sheet` 列,不写内容)→ 642 前端 tab → 643 Uber 2 行 → **644–648 共 30 张速查表撰写**(从既有 system_designs 列**蒸馏**,不发明新内容;格式 doc 85 §1.6:竖排伪架构+keywords+Senior signal 表+mini glossary;每张 ~1500-2000 字;idempotent seed upsert)→ 649 smoke。★DeepSeek 蒸馏本命。
- **KG-INT B4**(~21,最长直列 DAG,人机共审):B4a dry-run(815–820,**不写 DB**,产 archive plan+causal-proof matrix,Discord 等👍 闸门)→ B4b execute(822–828 P0 链 Google→…→Meta;829–834 P1 链,👍后 hard-archive+restore.sql+skeleton seed+7 步证明)→ 821 promotion + 836 cleanup。**含 DB 破坏性操作,dry-run 承认闸门必须维持**。
- **BQ-DEPTH 10–14**(锁 581):581 top40 定 primary story(Discord 批 40 件)→ 582 剩 ~36 题批量 probe_notes(★DeepSeek 候选)→ 583 前端 Phase D → 585 Phase E 漂移检测。
- **ML-Infra-LLM**:908(前端)→ 909(seed 用户给的 500GB 部署 golden,末尾可选 light polish=CN 叙述+EN 首现展开)。
- **Guard A/B**:912 scanner(只警告不 block)→ 918 triage → **917 CI fail-on-drift 带 `human_review=1`**(enforcement 必须人审)。

## 已定方向(2026-06-17,用户确认)
1. **下手点 = state 卫生 → DEBT 一扫**:先把 state=None 4 个正规化成 `ready`,再 876→877→878→879 autonomous 批跑一扫(技术债、不碰内容)。
2. **DeepSeek = 生成也积极用**:不止蒸馏/polish(CHEATSHEET 蒸馏、909 CN/EN polish),probe_notes 生成、skeleton 文面等 net-new 也交 DeepSeek,人手只做 accept-default 复审(memory `eager_autosuggest`:accept-default 比从零建省)。破坏性操作/golden 本体/判断系仍留 Claude/人手。
   - 落点:做共享 helper `scripts/lib/ds_distill.py`(DeepSeek v4 + 分块 + temp0 + 截断感知),供 CHEATSHEET/BQ probe seed 脚本调用。
   - polish 实践(memory `ytpipe`+`token_limits`):长稿**分块+temp0**(一次性跑飞,加 quota 解决不了);token 上限别小气(截断检测升档);判断 thinking on / 机械 off。
   - ⚠️ **DeepSeek API 2026-07-24 deprecated**(memory `reference_toolchain_facts`):按后继型号迁移来组,或短期用完即走;base_url 无 `/v1`,无 vision。

## 接续点(新 session 先做)
1. 读本文件 + `python .claude/hooks/task_db.py pick`。
2. 正规化 state=None 4 个(912/918/905/916)→ `state='ready'`。
3. 起 DeepSeek helper(`scripts/lib/ds_distill.py`)+ DEBT 簇 autonomous 批跑(876→877→878→879)。

## Pitfalls(本项目特有)
1. **TASKS.md 只读**(PreToolUse hook 拦截 Write/Edit)— 一切走 `task_db.py`;ID 自动生成,别手编。
2. **每个 DB 内容行须有 idempotent Python seed 脚本作真相源**(Invariant 3),禁 ad-hoc SQL;`invariant3_guard.py` 会拦截 schedule-shaped prose 写入 `company_documents.content`。
3. **改 DB 前先过 Surface Identification 表**(CLAUDE.md):widget→queryKey→endpoint→table,别按上一轮编辑目标 pattern-match(失败案例 `logs/2026-04-30_pinterest_root_cause.md`)。
4. **never 用 EnterPlanMode**;多任务执行委托 `scripts/autonomous_run.sh`,别在主 context 串跑多任务。
5. 中文写文件用 `python` 写 UTF-8,**别用 bash/PS heredoc 塞中文**(易乱码);PROGRESS append 用 Bash heredoc(UTF-8 干净)。
