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
70 任务:**18 done / 52 未完**(876/878/916/905 当日 autorun 完成)。52 里绝大多数被 gate/直列链锁住的 `blocked+pending`。**autorun-safe 子集已全部清完**;剩下的都是 supervised/gated。

### ✅ state 卫生债已清零(2026-06-17)
曾有 **4 个** `status='active'` 但 `state=None`(picker 不可视:912/918/905/916)。已全部正规化成 `state='ready'`,**现在 `state=None` 计数 = 0**。非完成任务现仅两态:`active+ready`(17,可拣)/ `blocked+pending`(38,dep 门控或 PARK)。
> 有意 PARK 的形态是 `status='blocked' + state='pending'`(picker 用 `state='ready'` 过滤);`state=None` 是异常不是 PARK,已根除。

### 2026-06-17 autorun 结果(scoped DEBT 批跑,三轮 — autorun-safe 子集全清)
把 autorun-safe 任务 scope 进 picker(其余临时 park),跑 `autonomous_run.sh`:
- ✅ **T-P1-876**(`9eceb95`)语法修复 · **T-P2-878**(`421e9c9`)发现 pyproject 4 dev deps 其实已同步=audit 误报,改加 dep-sync 回归测试 · **T-P3-916**(`3dd12df`)只读决策 doc · **T-P2-905**(`478d055`)PROGRESS.md 归档 517→387 行(9 旧 session 移 archive,留 45)。四个均完成 + push。
- Round1(876+878+905+916)Session 2 撞 **Claude session 额度耗尽**只做完 876;额度恢复后 Round2 补 878+916;Lyra 决定后 Round3 补 905。
- 跑后每轮都恢复全部 park、清零 state=None。
> ⚠️ autorun 不能指定目标,只拣最高优先级 pickable。非 autorun-safe 任务(见下)若不 park 会被先拣中并撞 sensitive-gate / manual-smoke。重跑前须重新 park 非安全任务(含已恢复成 ready 的 912/918),或逐个 supervised。

### 前任遗留待决:Lyra ad-hoc seed — ✅ 已处置(提交)
`scripts/_add_lyra_jacqueline_2026-05-27.py` + PROGRESS 条目 已提交(`24c5a0a`,2026-06-17)。决定=提交,依据 Invariant 3(interview_events id=80 已在 DB,内容行须有 git 跟踪 seed,丢弃会留孤儿行)。脚本已核查干净。**小遗留**:该 seed `status='upcoming'` 但 05-27 已过去,状态陈旧,可后续顺手改 completed(非阻塞)。

### 还能直接拣的(state=ready 且依赖满足)— 均 supervised/gated,非 autorun-safe
- ~~876 / 878 / 916 / 905~~ ✅ 已完成(2026-06-17,autorun)
- **T-P2-877**〔DEBT,M〕876 修后 `ruff check scripts/` 残 ~193(60 可自动修;剩 N806/B905/E741 旧 util 改名有语义风险需人审)— **非纯 autorun**(尾部需人审)
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
1. ~~state 卫生 → DEBT 一扫~~ ✅ 已完成:state=None 清零;autorun-safe DEBT(876/878/916/905)全清。**下一步 = 内容簇(配 DeepSeek)或 supervised DEBT(877/879/880…)**。
2. **DeepSeek = 生成也积极用**:不止蒸馏/polish(CHEATSHEET 蒸馏、909 CN/EN polish),probe_notes 生成、skeleton 文面等 net-new 也交 DeepSeek,人手只做 accept-default 复审(memory `eager_autosuggest`:accept-default 比从零建省)。破坏性操作/golden 本体/判断系仍留 Claude/人手。
   - 落点(**尚未起,下个内容簇 session 的第一步**):做共享 helper `scripts/lib/ds_distill.py`(DeepSeek v4 + 分块 + temp0 + 截断感知),供 CHEATSHEET/BQ probe seed 脚本调用。
   - polish 实践(memory `ytpipe`+`token_limits`):长稿**分块+temp0**(一次性跑飞,加 quota 解决不了);token 上限别小气(截断检测升档);判断 thinking on / 机械 off。
   - ⚠️ **DeepSeek API 2026-07-24 deprecated**(memory `reference_toolchain_facts`):按后继型号迁移来组,或短期用完即走;base_url 无 `/v1`,无 vision。

---

## 开新 session 运行说明(golden-path,照做即可)

### 0. 开工前(preflight)
```bash
cd "<...>/Gen_AI_Proj/MLInterviewPrep"
git status --short                      # 工作树该干净(上个 session 已收尾);有遗留先决定去留
ls .claude/autonomous.lock .claude/run-pgid   # 应都不存在(无在跑的 autorun)
python .claude/hooks/task_db.py pick    # 看默认拣选;get <ID> 读权威 spec(AC 在 description)
```
- ⚠️ **计费**:`claude -p`/autorun 走单独 API 池(非订阅)。额度耗尽会报 `You've hit your session limit · resets <t>`,session 空跑、不提交——等重置再跑。
- **单写者**:跑 autorun 期间不开第二个写 session、不手动改 tasks.db。

### 1. 选活
- **autorun-safe(无人值守可完整完成)**:纯机械、不碰 `.claude/` sensitive-gate、不改活循环用的 task 基建(`task_store.py`/`task_db.py`)、无 manual-smoke AC、不写 MLSD golden 内容。当前这类**已清完**。
- **supervised(逐条人值守)**:877(ruff 尾部需人审)/ 879(改 task 基建)/ 880(`.claude/skills`)/ 881(MLSD 内容)/ 908(manual-smoke)/ 921(大改)+ 所有内容簇(CHEATSHEET/KG-INT/BQ-DEPTH)。**逐个 supervised,别挂 autorun**。

### 2. 跑 autorun(仅 autorun-safe 任务;本 session 验证过的配方)
`autonomous_run.sh` **不能指定目标**,只拣最高优先级 pickable。要 scope 到指定子集:
```bash
# (a) 把"非目标但 pickable"的任务临时 park 出 picker(direct SQL;picker 用 state='ready' 过滤)
python -c "import sqlite3;d=sqlite3.connect('.claude/tasks.db');[d.execute(\"UPDATE tasks SET status='blocked',state='pending' WHERE id=?\",(t,)) for t in ['T-P1-881','T-P1-908','T-P1-912','T-P1-918','T-P1-921','T-P2-877','T-P2-879','T-P2-880']];d.commit()"
python .claude/hooks/task_db.py project          # 刷 TASKS.md 反映 park
python .claude/hooks/task_db.py pick             # 确认只剩目标
# (b) 若 PROGRESS.md 有"未提交且不该进 task commit"的遗留 → 先 stash 隔离(inner agent 会 git add PROGRESS.md)
git stash push -m "isolate-pending" -- PROGRESS.md     # 仅在有此类遗留时
# (c) 跑(后台);TASKS.md 因 (a) 的 regen 而 dirty → 用 --allow-dirty(剩余 dirty 仅 TASKS.md/未跟踪,安全)
bash scripts/autonomous_run.sh <N> --allow-dirty       # N = 目标任务数 + 1~2 余量
```
- 启动后核一眼:`tail logs ... EXPECTED_TASK_PREFIX=<目标>` 确认首拣正确、preflight 放行。
- inner agent 每完成一个任务:自跑 Verification + `complete --reviewer xushenghui` + append 自己的 PROGRESS 条目 + 显式路径 commit。

### 3. autorun 收尾(每轮跑完都做)
```bash
# 恢复 park 的任务 → active+ready(本 session 它们都源自 active+ready)
python -c "import sqlite3;d=sqlite3.connect('.claude/tasks.db');[d.execute(\"UPDATE tasks SET status='active',state='ready' WHERE id=?\",(t,)) for t in [<上面 park 的同一批>]];d.commit()"
python .claude/hooks/task_db.py project
git stash pop          # 若 (b) stash 过;PROGRESS.md 尾部冲突=保留双方(已提交条目+遗留),git add 后 git reset 取消暂存留遗留为待决,git stash drop
# 更新本 HANDOFF(就地改成当前真相)→ git add <显式路径> TASKS.md HANDOFF.md → commit [chore] → push
git push origin main
```

### 4. 铁律(贯穿)
- **显式路径 commit**,**永不** `git add .`/`-A`/`-u`(`no_wildcard_add` 钩强制)。commit msg 英文(`commit_msg_guard` 拦 CJK),格式 `[T-XX-N] ...` 或 `[chore]/[ad-hoc] ...`。
- 改 DB 内容 → 走 idempotent seed(Invariant 3)+ Surface Identification 表;**never EnterPlanMode**。
- 写中文文件用 `python` 写 UTF-8;PROGRESS append 用 Bash heredoc(干净)。

### 接续点(下个 session 最可能先做)
1. 读本文件 + `task_db.py pick`。
2. **内容簇起步**:先做 `scripts/lib/ds_distill.py`(DeepSeek helper),再开 CHEATSHEET 641 闸 → 644 跑 1 张蒸馏试点(supervised,人审 accept-default)。
3. 或挑 supervised DEBT(877 ruff `--fix` 自动部分 + 人审尾部 / 879 SIM105)。

## Pitfalls(本项目特有)
1. **TASKS.md 只读**(PreToolUse hook 拦截 Write/Edit)— 一切走 `task_db.py`;ID 自动生成,别手编。
2. **每个 DB 内容行须有 idempotent Python seed 脚本作真相源**(Invariant 3),禁 ad-hoc SQL;`invariant3_guard.py` 会拦截 schedule-shaped prose 写入 `company_documents.content`。
3. **改 DB 前先过 Surface Identification 表**(CLAUDE.md):widget→queryKey→endpoint→table,别按上一轮编辑目标 pattern-match(失败案例 `logs/2026-04-30_pinterest_root_cause.md`)。
4. **never 用 EnterPlanMode**;多任务执行委托 `scripts/autonomous_run.sh`,别在主 context 串跑多任务。
5. 中文写文件用 `python` 写 UTF-8,**别用 bash/PS heredoc 塞中文**(易乱码);PROGRESS append 用 Bash heredoc(UTF-8 干净)。
