# HANDOFF — MLInterviewPrep

> 新 session 从这里接续。**这是活文档**:就地 edit 成当前真相(不是 append-only;只有 `PROGRESS.md` 才 append-only)。
> 详细命令见 `CLAUDE.md`,任务权威 spec 取 DB(`python .claude/hooks/task_db.py get <ID>`),经验教训见 `LESSONS.md`。
> 维护约定:**始终维护这同一个文件**;整条 workstream 落地后,把对应段落就地改成「已完成」或删掉,不另起新 handoff。

## 一句话

全栈 **ML/SDE 面试备战平台**(FastAPI + SQLAlchemy + SQLite WAL / React 19 + TS + Tailwind / Anthropic Claude API / pytest 512+)。范式:**内容=一等对象**,专题/主题是多对多 link(改导航/主题永不动内容页)。五种抽屉 URI:`lc/db/cd/sd/kg`。

## 位置 & 运行时
- 目录:`Gen_AI_Proj/MLInterviewPrep`(有自己的 `.claude/tasks.db`)。Python:`/c/Anaconda/python.exe`。
- Windows 控制台 cp1252:一次性脚本前置 `PYTHONUTF8=1 PYTHONIOENCODING=utf-8`。
- [WARN] 计费:`claude -p`/autorun 走**单独 API 计费池**(非订阅),见 root memory `june15_programmatic_billing_split`。
- 内容/DB 改动遵循 root memory `mli_content_workflow`(7 步改写、sync-ALL-surfaces、五抽屉 URI、MLSD golden 约束)+ `CLAUDE.md` 的 Surface Identification 表(改 DB 前先 widget→queryKey→endpoint→table 映射)。

## 下个 session = **supervised run**(别挂 autorun,见下方原因),任务菜单见下

- **[2026-06-19 更新] 当前 `pick` = none。本 session 完成了 641 + 815(后者是 autorun 越界 bonus,见下)。**
  - **T-P1-641**(CHEATSHEET-1)关闭:其 schema/API/前端早在 `1281ea6` 已实现,只是没标 done——picker 一直误报它;inner agent 复跑验收门后关闭,commit `c88ee52`,5/5 测试已**独立复验**。
  - **T-P1-815**(KG-INT B4a-adobe dry-run)**意外完成**:我本想只跑 641,park 了 909/921,但 autorun Session 2 的 inner agent 自行从 backlog 拣了 815(depends_on=None、不写 DB 的安全 dry-run),产出完整 230 行 plan 并 commit(`335b481`),在我 taskkill 后竞态完成。**净结果是好的**(815 是之前缺的 5 份 B4a plan 之一,安全可逆),但暴露一个**铁律**:**`state='pending'` 的 PARK 挡不住 autorun inner agent 的自主拣选**(它读 backlog 用判断拣,不只看 state-based picker)。要真正限定 autorun 子集,必须让不安全任务对 inner agent **不可执行**(加阻塞 dep / 抽走素材),不能只 `state=pending`。详见 `LESSONS.md` 2026-06-19 条。
  - **909**(input-blocked)+ **921**(supervised-only)仍 PARK(`status=blocked/state=pending`),要重新可拣需恢复 `state=ready,status=active`。
  - **815 的 plan 留了 4 个 open questions 给用户**(Teams passcode 脱敏、STAR 故事 provenance=潜在 blocker、PyTorch-ops 节点映射、doc-20 orphan)——见 `docs/archive_plans/B4a-adobe_2026-06-19.md` 末尾;B4b-adobe(T-P1-829)execute 前须用户先答。
- **CHEATSHEET 现状**:641 done → schema/API/前端 type 全就位(`cheat_sheet` 列在 canonical `data/mle_prep.db`;`/api/system-designs/cheat-sheets` 聚合端点已上线)。剩 **642**(前端 Cheat Sheet tab,manual browser-smoke → supervised)+ **643**(Uber 2 行,MLSD 撰写)+ **644–648**(30 张速查表,DeepSeek 蒸馏 + accept-default;需先把 DeepSeek key 复制到 gitignored `scripts/lib/.env.deepseek`)+ **649** smoke。这些都 **supervised**,目前仍 parked(pending)。
- **[原] autorun-safe 子集 = 空。** 盲挂 `autonomous_run.sh` 会拣中已 parked 之外的 dep-blocked 任务或 none;要跑 autorun 必须先确认 `pick` 拣到的是安全任务。下个 session 默认 **supervised 逐条人值守跑**。
- **[DONE] BQ-DEPTH 线全收口**(581→582→583→585):内容 seed → top40 primary 指派 → 前端 primary 卡 + probe 面板 → 只读漂移检测器,端到端打通。本次 session 详见下方 2026-06-18 条目。

### 任务菜单(供下个 supervised session 选,按可执行性排)

| 任务 | 状态 | 说明 / 运行前置 |
|---|---|---|
| **T-P1-909** [P1/M] ML-Infra golden seed | **[BLOCKED-ON-INPUT]** | 需用户把 golden doc `distributed_model_deployment_golden.md` 放进仓库(任务 spec 写明"user-provided")。**文件不在 = 不能做**。拿到后:idempotent `scripts/seed_anthropic_distributed_model_deployment_golden.py`,slug=`anthropic-distributed-model-deployment`,9 列映射见 `task_db.py get T-P1-909`(Anthropic tag = scheme A:slug 前缀 + subtitle;system_designs 无 company_id 列;NOT MLSD family,不套 [DOMINANT]/floating-twist)。|
| **T-P1-912** [P1/L] Guard Phase A 扫描器 | **[SUPERVISED-READY]** | 前置 910/911/914 **已全归档(done)**,可做。但建新 hook `.claude/hooks/description_progress_guard.py`(autonomous 敏感目录)→ **只在 supervised 跑**,别 autorun。仿 `invariant3_guard.py`,AST 检测对 `framework_nodes.description`(及 914 root-cause 指定的 status/progress_pct 直写面)的写入;scanner-only(warn+autofix-suggestion,**不 block**)。完成后解锁 917(Phase B enforcer,HUMAN-REVIEW)。|
| **T-P1-921** [P1/M] WSH-E1 drawer_nav | **[SUPERVISED]** | 抽 `company_documents` 的 drawer 导航进结构化 `drawer_nav` JSON 列(schema 迁移)+ 前端 `CompanyDocDrawer` 渲染 + 退役 4 个 retrofit 脚本。带 manual-smoke AC(开 Meta-MLSD 抽屉验导航)→ supervised。完成后解锁 922。|
| **KG-INT B4a dry-run** (815–820) | **[需用户决策]** | backlog 最大一坨(~21 任务,含全部 7 个 P0)。全冻结,入口是 6 个 B4a dry-run(**不写 DB**,产 archive plan + causal-proof matrix,Discord 等用户 gate)。放行后 → B4b execute(822–828=P0 串行链)→ 821 promotion → 836 cleanup。**等用户拍板才启动**。|

- 一般运行规程见本文件 **`## supervised run 运行说明`**。
- **autorun 重启清单**(若将来有 autorun-safe 任务):先 `task_db.py pick` 确认拣到的是安全任务;非安全的先 park(`UPDATE tasks SET state='pending',status='blocked'`——注意 `task_db.py update --status` 只改 status 不改 state,picker 看的是 **state**);跑完恢复 `state='ready',status='active'`;再 `task_db.py project` 重生成 TASKS.md。

### 最近一次 session(2026-06-18,supervised + 1 次 autorun)— [DONE] 583 + 585(BQ-DEPTH 线收口)
- **[DONE] T-P1-583**(前端 Phase D,supervised,commit `86b651c`):重写 `BehavioralQuestions.tsx` 展开视图。有 `is_primary` link 的题 → 金边 Primary Story 卡(置顶,full `relevance_note` + STAR Situation 预览 + "lead with this" 提示)+ 折叠 "Also applies (N)" 备用面板 + 折叠 "What this question probes" → 4 段 probe_notes 面板(markdown via 共享 `MarkdownPreview`)。非 top-40(无 primary)走旧 flat list(无回归);0-link 走旧空状态。抽出共享 `LinkedExampleCard` 去重。`BehavioralQuestion` interface 加 `probe_notes`/`probe_notes_updated_at`。
  - 验证:tsc clean、eslint clean、`vitest run` **251 passed**(+13,含 4 个场景 A-D 真组件渲染测试)、`npm run build` exit 0。活 API 端到端:OWN-1 返回 4 字段 probe + primary EX-15 + 3 备用;**全 40 top 题都有 primary+probe**。**用户浏览器验收通过**(金边卡、probe 面板、Also-applies、抽屉均 OK)。
  - 改动:`src/frontend/src/pages/BehavioralQuestions.tsx`、`...BehavioralQuestions.test.tsx`。无后端/DB 改动。顺手修了 `scripts/_bq_581_review_html.py` 里被 lint guard 标的 emoji(/[OK] → ASCII)。
- **[DONE] T-P2-585**(Phase E 漂移检测器,autorun 1 session,commit `130f4ff`):`scripts/detect_probe_drift.py` —— 只读 watchdog,**窄口径**(只在 `principle_tags`/`risk_statement`/`result` 变,或叙事 situation+task+action+result delta>30% 时触发)。baseline 快照 `data/probe_drift_baseline.json`(gitignored)只在 probe 重生成时重拍,所以真漂移每次都报到刷新为止;字段编辑不会偷偷 re-baseline。`mode=ro` URI(不可能写 DB)。无漂移时静默(无报告文件无 stdout);`--strict` 漂移时 exit 1(cron/CI)。`tests/test_detect_probe_drift.py`(10 测试)。
  - 验证(我已**独立复验**,非只看 inner 自报):10/10 测试通过;真库只读跑 baseline → `--strict` exit 0 静默无报告 = **0 误报**(AC 达成);true-positive 在沙箱 DB 副本上证过(改 risk_statement 触发 exit 1)。可选的 session_context.py cron 提醒**故意跳过**(spec 标 optional + 会动敏感 hook)。
- **本 session 运维动作**:为让 autorun 拣中安全的 585,临时 park 了 909/912/921(commit `e3e7b1a`);585 跑完**已全部解冻**回 `state=ready,status=active`(commit 见本次)。所以现在 picker 又会拣 909(input-blocked)——下个 session 看上方菜单,**别盲挂 autorun**。
- **接续点**:BQ-DEPTH 线(581-585)整条完。下个活在上方任务菜单里选;无 autorun-safe 任务剩,supervised 跑。

### 最近一次 session(2026-06-17,supervised)— [DONE] 582 done(全 40 题 probe_notes,DeepSeek 4 批)
- [DONE] **T-P1-582 完成**:从 batch 1 spot-check gate 接续,seed batch 1 → 逐批(2/3/4)generate→spot-check→seed,全 40 top BQ 题 probe_notes 落库(DeepSeek deepseek-v4-pro temp0,4 字段 schema)。
  - **render-unsafe `<` 漂移类**:DeepSeek 反复在数字比较里出 `<=1%`/`<5%`(react-markdown 把 `<` 当 HTML 起始)。batch 2 手修 3 处(含一个 `<->` bridge 改 '和...之间');随后**扩展生成器确定性 normalizer**(`<=N`→`不超过 N`、`<N`→`低于 N`,加 `import re`)→ batch 3 两处自动清零、batch 4 9/9 零手动。
  - 验证:真 endpoint `GET /api/behavioral/questions`(TestClient+lifespan,活 DB)返回 **40** 题 probe_notes 4-字段 dict + updated_at;coverage SQL 0 missing/0 empty;4 批 seed 重跑 0 写/36 SKIP(幂等);`pytest -q` **1315 passed**;py_compile+ruff clean。
  - 改动:`scripts/_bq_582_probe_notes_deepseek.py`、`scripts/seed_bq_probe_notes_20260421.py`、`docs/bq_probe_notes_batch{1-4}_20260421.deepseek.json`(+`.review.html`×4)。DB 走 idempotent seed(`data/` 未跟踪)。
  - **接续点**:583(前端 Phase D primary 卡 + probe panel,数据已就绪)。

### 上一次 session(2026-06-17,supervised)— [WIP] 582 batch 1 内容定稿(标点/render-safety 已焊死)+ branch 退役
- [DONE] **branch 退役**:`claude/agitated-leavitt`(MLI worktree)退役——唯一 commit `3fc8a54` 已被 main 完全超越(root `claude_wrapper.sh` 在 + main `autonomous_run.sh` 已 source),7 个未提交残留全旧于 main 无前向价值 → `worktree remove --force`+`branch -D`+prune(**不 merge**:991 behind 会冲回新版)。root CLAUDE.md agitated-leavitt 脚注已清(root `3146286`)。
- [WIP] **T-P1-582 进行中**(in_progress):建生成器+幂等 seed,**batch 1(OWN-2/6/8/11、ADP-11/10/1/15、IMP-11)内容已定稿**:9/9 clean,voice 对齐 calibration,EX-NN primary 必引用。用户拍板「只做内容侧,渲染留 583」后,把**标点口径(半角+全角 `。`)、render-safety(挡 `$`/`<`/行首 `>`)、截断重试 ladder** 全焊进生成器(见 playbook Step 0),batch 2-4 自动继承。**API 已验**(TestClient `GET /api/behavioral/questions`:4 条 calibration 返回 probe_notes dict 4 键、未 seed 的 OWN-2 返回 None)→ 583 可直接消费。DB 仍未写、batch 2-4 未生成、脚本未 commit(582 收尾一起提)。新 session 从 playbook **Step 1(seed batch 1)** 接续。

### 最近一次 session(2026-06-17 深夜,supervised)— [DONE] 581 done(top40 primary-story + DeepSeek QA 接线)
- [DONE] **T-P1-581 完成**(用户批准 40 件指派后落库):给 top40 高频行为题各定唯一 primary story,`question_example_links.is_primary=1`(36 置新 + 4 库内原有匹配)。
  - **流程**(human-as-verifier):Claude 起草 40(primary 从每题已有 link 里挑,以 `bq_golden_trait_matrix.md` theme→primary 映射为先验)→ DeepSeek 判官(`deepseek-v4-pro` temp0,keep=24/swap=14/flag=2)→ Claude accept-default 复审(26 保留 / 5 采纳 swap / 9 否决)→ 用户 [OK] → 幂等 `.bak` 守护 seed `--apply`。
  - **DeepSeek 接线**(MLI 首次):新建 `scripts/lib/deepseek_creds.py`(照搬 pensieve 安审范式:手写解析、绝不 os.environ、缺 key FileNotFoundError、掩码 repr),真 key 复制到 gitignored `scripts/lib/.env.deepseek`,committed 模板 `.env.deepseek.example`。[WARN] **坑**:`deepseek-v4-pro` 是 reasoning 模型,`max_tokens=400` 被 reasoning_tokens 吃光→空输出;升到 3000 修复(memory `token_limits`)。
  - **验证**:AC SQL 每题 ≤1 primary(0 dups,40 distinct);幂等(重跑 0 SET/40 SKIP);**真 endpoint** `GET /api/behavioral/examples` 40 个 is_primary=true 上线、spot-check 精确;`pytest -q` **1315 passed**;ruff+py_compile clean。
  - 改动:`scripts/lib/deepseek_creds.py`、`scripts/lib/.env.deepseek.example`、`scripts/_bq_581_qa_deepseek.py`、`scripts/seed_bq_primary_flags_20260421.py`、`scripts/_bq_581_review_html.py`、`docs/bq_primary_story_assignments_20260421.md`(+ `.deepseek.json` 留痕)。
  - **接续点**:582(批量 probe_notes,DeepSeek 生成),DeepSeek 客户端现成可复用。

### 最近一次 session(2026-06-17 深夜,supervised)— [DONE] 880 + 918 + 923 done(漂移治理收口 + sync 驳回)
- [DONE] **T-P2-880**(SYNC,完成):**驳回照搬** template 的 study-review skill。验证:模板 skill 绑死 Hexo 博客路径(`tools/review_queue.py` CLI + `source/_posts/*.md`)+ 0-5 SuperMemo 评分,MLI 都没有;且 MLI 已有自己的 DB 版间隔重复(`spaced_repetition.py` + `/problems/review-queue` + `ReviewPanel.tsx`)。照搬既坏又重复。决策 note 已记 PROGRESS。
- [DONE] **T-P1-918**(reverse-drift 甄别,只读):活 DB 复核,危险集={115,171}(都叶子,review/100/0-勾选/全 NULL ts)。节点 69 自上次 914 快照后**自愈**(now mastered 1/1);7 个父节点是派生 pct 非漂移。git 铁证:owning seed `git log -S'- [x]'` 全空→pct=100 是不可追溯直写非真掌握。升级给用户 → 裁决**两个都 stale**。决策 note:`logs/review/T-P1-918_reverse_drift_triage_20260617.md`。
- [DONE] **T-P1-923**(reconcile,执行裁决,`7aedd38`):signature-guarded idempotent seed `scripts/reconcile_reverse_drift_115_171_20260617.py` 把 115/171 清成 not_started/0.0(checked>0 时自动 SKIP 不覆盖未来真进度);`.bak`+audit 已写。验证:reverse 签名全表清空;真 endpoint `GET /api/framework/nodes/{115,171}` 返回 not_started/0.0;节点 69 未误伤;targeted pytest 250 passed。
- **本 session 提交**:MLI `7aedd38`(880+918+923,未 push)。`framework_nodes` 漂移治理的**补救侧**收口;预防侧=912(待做)。
- **接续点**:用户拍板下一活 = **T-P1-581**(见下方执行交接草案)。

### 上一次 session(2026-06-17 晚,supervised)— [DONE] 881 done(sd42 → oral_narrative archetype 迁移)
- [DONE] **T-P1-881 完成**(MLI `820bc4d`,未 push):sd42 `meta-top3-comments-golden` 从 structured_reference 迁到 **oral_narrative**(镜像 sd41/T-P1-875 + weapon/friend minimal-A)。
  - **发现 drift**:成品 10504 字第一人称 45min 口播稿早已被写进 DB `dataflow`,但主 seed 还是旧 structured DATAFLOW(6378)+ 其余 9 字段仍填充。**复用成品**(memory `handoff_reuse_made_content`):把 DB 口播稿捕获进主 seed 作真相源(Invariant 3),NULL 掉 architecture/PC/tradeoffs/defense,保留 overview/formulas/cheat_sheet,verbal_outline 由既有 T-P0-893 verbal seed 在主 seed 后重填 4829。
  - 改动:`scripts/seed_meta_top3_comments_golden_sd.py`(重生成为 archetype-aware oral_narrative seed)、`schemas/meta_mlsd_canonical.yaml`(sd42 条目加 document_archetype:oral_narrative + baseline_chars_post_migration:10504)。DB 走 idempotent seed(不入 git)。一次性 builder 已删。
  - 验证:`audit_meta_mlsd_3rule.py` **exit 0 / 0 findings**(cd96 + sd41-44),cross-page clean,diff-delta 无 breach;幂等(二次跑链仍 exit 0);`pytest -q` **1315 passed**;seed py_compile + ruff clean。最终形态:overview 4596 / dataflow 10504 / formulas 4920 / verbal 4829 / cheat 4155;architecture/PC/tradeoffs/defense=NULL。无浏览器 smoke(纯数据迁移,落在已上线的 oral_narrative 渲染路径上,sd41/weapon/friend 已证 NULL-列渲染;canonical gate = audit oracle 已绿)。
  - **接续点**:Meta-MLSD narrative 簇 sd41-44 全部 oral_narrative 化完毕。

### 上一次 session(2026-06-17 晚,supervised)— [DONE] 908 done(ML Infra·LLM SD tab + carve [300,400))
- [DONE] **T-P1-908 完成**(MLI `7760c20`,未 push):纯前端,DB 未写。`SystemDesignList.tsx` 6 处改动:① `Tab` 类型加 `'ml-infra-llm'` ② 新 `mlInfraModules`/`mlInfraCount` useMemo(filter `[300,400)`)③ Pinterest 收边 `pinterestTopics`/`pinterestCount` 加上界 `<300` 防新 band 漏入 ④ Pinterest 后加 tab `<button>` label `ML Infra · LLM` ⑤ 新内容块镜像 ml-mlsd flat-card。
  - 验证:vitest **247/247** pass;`npm run build` exit 0;**真浏览器 manual-smoke**(conda Playwright + 真后端:8100/vite:5173):`?tab=ml-infra-llm` → tab 可见且激活 + 空态「No ML Infra · LLM modules yet」(对,`[300,400)` 现 0 行,待 T-B/909 seed);`?tab=pinterest` → 恰好 8 卡、无 ML-Infra 漏入;tabbar 顺序 = [Interview Prep, ML System Design, eBay Projects, Pinterest, ML Infra · LLM]。
  - **接续点**:909 = seed 用户给的 500GB 部署 golden(需用户提供内容),seed 进 `[300,400)` band → 卡片自动出现在此 tab。
- 改动:`src/frontend/src/pages/SystemDesignList.tsx`。

### 上一次 session(2026-06-17 晚,supervised)— [DONE] 877 done(scripts/ ruff 清零)
- [DONE] **T-P2-877 完成**:`ruff check scripts/` 从 177 errors → **0**(排除 propagate 管理文件)。两阶段:
  - **Phase A 安全自动修**(`--fix` 不带 `--unsafe-fixes`,117 fixed):UP017/F541/F401/I001/UP035/UP037/W605 等纯机械保行为。
  - **Phase B 人审手改**:真改代码 = B905 加 `strict=False`(6)、B007 未用循环变量加 `_`(13)、B023 闭包绑循环变量为默认参数(`retrofit_doc_drawer_links.py`,同步调用行为等价,3)、F841 删死变量(2)、SIM108/103/110 简化、E402 import 移顶部;**scripts/ 作用域 per-file-ignore**(写进 `pyproject.toml`)= N806/N803/E741/E701/E702/SIM102(一次性 seed/audit/嵌入算法脚本里命名/紧凑风格 nit,改名有破坏 run-result 风险,spec 自己警告)。**未盲跑 `--unsafe-fixes` 全扫。**
  - **scope 守卫**:propagate 管理文件(`scripts/workflows/*`、`sweep_stuck_leases.py`、`lib/events.py`)**有意没碰**——其 ~18 残留 ruff 错(含 SIM105)是独立 debt,须 **root canonical 改 + propagate**(MLI 局部改会被 daily broadcast 冲回 = 假绿)。
  - 验证:`ruff check scripts/ --exclude <managed>` → All checks passed;`pytest -q` → **1315 passed**;65 改动脚本 py_compile 全过。
- 改动:65 `scripts/*.py` + `pyproject.toml`。

### 上一次 session(2026-06-17 晚,supervised)— [DONE] 879 done + 根工作树清理
- [DONE] **T-P2-879**(MLI `69ae26a`,push main):`task_store.py` `try/except ValueError/pass` → `contextlib.suppress`;修 shared/ 源 + .claude/ 活镜像两份,**没用 sync.py**(会删 7 个 MLI-local hooks)。
- [DONE] **根工作区工作树清理**(根仓库 `master` 3 commits,本地未 push):`35ab8e2` 7 个独立子仓库/草稿目录入 `.gitignore`;`ecb8328` 收 ytpipe doc builders+语料;`5b0a978` 收 06_10_ads study HTML builder。
- **独立 debt(下一轮/T-P2-321 需知)**:工作区 14 份 task_store.py 副本都带 SIM105,但 task_store.py 不在 propagate 管理集(deferred 到 T-P2-321),daily-broadcast 不冲回——无假绿风险,本 S 有意没 blast。

## Backlog 现状(2026-06-17 晚核实)
**27 done / 43 未完**(876/878/916/905 autorun + **879 + 877 + 908 + 881 + 880 + 918 + 923 + 581 + 582 supervised** 完成;923 为 918 派生的 reconcile 跟进;581 primary-story + 582 全 40 题 probe_notes 接 DeepSeek)。43 里绝大多数被 gate/直列链锁住的 `blocked+pending`。**autorun-safe 子集已全部清完**;剩下的都是 supervised/gated。下一活 = **583**(BQ 前端 Phase D primary 卡 + probe panel,接 582 解锁)。

### [DONE] state 卫生债已清零(2026-06-17)
曾有 **4 个** `status='active'` 但 `state=None`(picker 不可视:912/918/905/916)。已全部正规化成 `state='ready'`,**现在 `state=None` 计数 = 0**。非完成任务现仅两态:`active+ready`(17,可拣)/ `blocked+pending`(38,dep 门控或 PARK)。
> 有意 PARK 的形态是 `status='blocked' + state='pending'`(picker 用 `state='ready'` 过滤);`state=None` 是异常不是 PARK,已根除。

### 2026-06-17 autorun 结果(scoped DEBT 批跑,三轮 — autorun-safe 子集全清)
把 autorun-safe 任务 scope 进 picker(其余临时 park),跑 `autonomous_run.sh`:
- [DONE] **T-P1-876**(`9eceb95`)语法修复 · **T-P2-878**(`421e9c9`)发现 pyproject 4 dev deps 其实已同步=audit 误报,改加 dep-sync 回归测试 · **T-P3-916**(`3dd12df`)只读决策 doc · **T-P2-905**(`478d055`)PROGRESS.md 归档 517→387 行(9 旧 session 移 archive,留 45)。四个均完成 + push。
- Round1(876+878+905+916)Session 2 撞 **Claude session 额度耗尽**只做完 876;额度恢复后 Round2 补 878+916;Lyra 决定后 Round3 补 905。
- 跑后每轮都恢复全部 park、清零 state=None。
> [WARN] autorun 不能指定目标,只拣最高优先级 pickable。非 autorun-safe 任务(见下)若不 park 会被先拣中并撞 sensitive-gate / manual-smoke。重跑前须重新 park 非安全任务(含已恢复成 ready 的 912/918),或逐个 supervised。

### 前任遗留待决:Lyra ad-hoc seed — [DONE] 已处置(提交)
`scripts/_add_lyra_jacqueline_2026-05-27.py` + PROGRESS 条目 已提交(`24c5a0a`,2026-06-17)。决定=提交,依据 Invariant 3(interview_events id=80 已在 DB,内容行须有 git 跟踪 seed,丢弃会留孤儿行)。脚本已核查干净。**小遗留**:该 seed `status='upcoming'` 但 05-27 已过去,状态陈旧,可后续顺手改 completed(非阻塞)。

### 还能直接拣的(state=ready 且依赖满足)— 均 supervised/gated,非 autorun-safe
- ~~876 / 878 / 916 / 905~~ [DONE] 已完成(2026-06-17,autorun)
- ~~879~~ [DONE] 已完成(2026-06-17 晚,supervised,`69ae26a`)
- ~~877~~ [DONE] 已完成(2026-06-17 晚,supervised):`ruff check scripts/` 清零(排除 propagate 管理文件);per-file-ignore 写进 `pyproject.toml`。
- ~~908~~ [DONE] 已完成(2026-06-17 晚,supervised,`7760c20`):「ML Infra·LLM」SD tab + carve [300,400) + Pinterest 收成 [199,300) 防泄漏。vitest 247 + build + 真浏览器 smoke 全过。其后 **909 = seed 用户给的 500GB 部署 golden**(需用户提供内容)。
- ~~881~~ [DONE] 已完成(2026-06-17 晚,supervised,`820bc4d`):sd42 → oral_narrative;audit exit 0 / 0 findings sd41-44;pytest 1315。Meta-MLSD narrative 簇收官。
- ~~880~~ [DONE] 已完成(SYNC 驳回照搬,见最近 session)。~~918~~ [DONE] ~~923~~ [DONE](漂移补救侧收口)。
- ~~581~~ [DONE] 已完成(2026-06-17,supervised):top40 primary-story flags + DeepSeek QA 接线。解锁 582→583→585。
- ~~582~~ [DONE] 已完成(2026-06-17):全 40 题 probe_notes,DeepSeek 4 批生成。
- -> **T-P1-583**〔BQ-DEPTH,前端〕**= 下一活**。Phase D primary 卡 + probe panel,消费 581/582 数据(probe_notes dict + is_primary)。manual-smoke AC 必做。
- **T-P1-909**〔ML-Infra-LLM,—〕seed 用户给的 500GB 部署 golden 进 [300,400)(需用户提供内容;末尾可选 light polish=CN 叙述+EN 首现展开)
- **T-P1-912**〔Guard A,L〕drift guard Phase A scanner(`.claude/hooks` sensitive-gate);漂移治理**预防侧**收口(918/923 是补救侧)。
- **T-P1-921**〔WSH-E1,M〕drawer_nav 抽列 + 4 retrofit 退役 + E2 决策门

### 各簇详解
- **DEBT/SYNC**(876–880):技术债,直列,不碰内容,判断少 → **autonomous 批跑一扫**。
- **CHEATSHEET 1–9**(全锁 641):641=schema+API(加 `cheat_sheet` 列,不写内容)→ 642 前端 tab → 643 Uber 2 行 → **644–648 共 30 张速查表撰写**(从既有 system_designs 列**蒸馏**,不发明新内容;格式 doc 85 §1.6:竖排伪架构+keywords+Senior signal 表+mini glossary;每张 ~1500-2000 字;idempotent seed upsert)→ 649 smoke。DeepSeek 蒸馏本命。
- **KG-INT B4**(~21,最长直列 DAG,人机共审):B4a dry-run(815–820,**不写 DB**,产 archive plan+causal-proof matrix,Discord 等[OK] 闸门)→ B4b execute(822–828 P0 链 Google→…→Meta;829–834 P1 链,[OK]后 hard-archive+restore.sql+skeleton seed+7 步证明)→ 821 promotion + 836 cleanup。**含 DB 破坏性操作,dry-run 承认闸门必须维持**。
- **BQ-DEPTH 10–14**:~~581~~ [DONE](top40 primary-story + DeepSeek QA 接线)→ ~~582~~ [DONE](全 40 题 probe_notes,DeepSeek 4 批,2026-06-17)→ -> **583 = 下一活**(前端 Phase D primary 卡 + probe panel)→ 585 Phase E 漂移检测。
- **ML-Infra-LLM**:~~908(前端)~~ [DONE] done → **909**(seed 用户给的 500GB 部署 golden 进 [300,400),需用户提供内容;末尾可选 light polish=CN 叙述+EN 首现展开)。
- **Guard A/B**:912 scanner(只警告不 block)→ 918 triage → **917 CI fail-on-drift 带 `human_review=1`**(enforcement 必须人审)。

## 已定方向(2026-06-17,用户确认)
1. ~~state 卫生 → DEBT 一扫~~ [DONE] 已完成:state=None 清零;autorun-safe DEBT(876/878/916/905)全清。**下一步 = 内容簇(配 DeepSeek)或 supervised DEBT(877/879/880…)**。
2. **DeepSeek = 生成也积极用**:不止蒸馏/polish(CHEATSHEET 蒸馏、909 CN/EN polish),probe_notes 生成、skeleton 文面等 net-new 也交 DeepSeek,人手只做 accept-default 复审(memory `eager_autosuggest`:accept-default 比从零建省)。破坏性操作/golden 本体/判断系仍留 Claude/人手。
   - 落点(**尚未起,下个内容簇 session 的第一步**):做共享 helper `scripts/lib/ds_distill.py`(DeepSeek v4 + 分块 + temp0 + 截断感知),供 CHEATSHEET/BQ probe seed 脚本调用。
   - polish 实践(memory `ytpipe`+`token_limits`):长稿**分块+temp0**(一次性跑飞,加 quota 解决不了);token 上限别小气(截断检测升档);判断 thinking on / 机械 off。
   - [WARN] **DeepSeek API 2026-07-24 deprecated**(memory `reference_toolchain_facts`):按后继型号迁移来组,或短期用完即走;base_url 无 `/v1`,无 vision。

---

## [DONE] [已完成] T-P1-581 执行交接草案(BQ primary-story + DeepSeek QA)

> [DONE] **2026-06-17 完成**(见上方最近 session 段)。本段保留作 **DeepSeek 接线参考**(582 复用):`from lib import deepseek_creds; creds=deepseek_creds.load()` → `OpenAI(api_key=creds.key, base_url=creds.base_url)` → `chat.completions.create(model=creds.model, temperature=0, max_tokens>=3000, ...)`。[WARN] reasoning 模型 token 上限别小气;base_url 无 /v1;2026-07-24 deprecated。
> 历史草案(原始 spec、流程、AC)如下,供 582 参照流程。

### 这是什么(已核 schema + 数据)
`[BQ-DEPTH-10]` 给 **top 40 high-prob 行为题**各定**唯一 primary story**,在 `question_example_links` 上把那条 link 的 `is_primary=1`。
- **schema**(`src/backend/models/behavioral.py`):`BehavioralQuestion`(题)/ `BehavioralExample`(故事)/ `QuestionExampleLink`(M2M,带 `is_primary` Bool + relevance_note)。**部分唯一索引 `ux_qel_primary_per_question`(`WHERE is_primary=1`)硬保证每题 ≤1 个 primary** —— seed 必须遵守(同题二次置 1 会撞唯一索引)。
- **现状数据**(活 DB,06-17):115 题 / 35 故事 / 271 link / **当前仅 4 个 is_primary 已置**。115 题全有 link。
- **输入素材**:Phase A 矩阵 `docs/bq_golden_trait_matrix.md`、`docs/bq_clustered_questions.json`、故事库 `docs/bq_behavioral_examples.json` / `docs/bq_improved_stories.md`、`docs/bq_story_arcs.json`。从 BQ-DEPTH-01 的 company-overlap + asked-frequency 直觉里挑 top 40。

### 流程(human-as-verifier:Claude 起草 → DeepSeek QA → 用户批 → seed 落 DB)
1. **Claude 起草 40 行指派**:每行 `(question_id, primary_example_id, rationale)`,写进 `docs/bq_primary_story_assignments_20260421.md`(spec 指定的文件名)。每题选一个最能正面回答它的故事;rationale 一句话(为什么这个故事是这题的主打)。
2. **DeepSeek QA(本任务 QA 用 DeepSeek,非 Claude)**:对 40 件逐条判官——「这个 example 真的是这道题的最佳 primary 吗?有没有同库里更贴的?STAR 完整度/题意契合度?」DeepSeek 输出 per-row verdict(keep / swap→建议 example_id / flag)。中文质量好+成本低几十倍(memory `pensieve_cloud_judge_deepseek`)。Claude 对 DeepSeek 的 swap 建议做 accept-default 复审,产出修订后的 40 行。
3. **用户批准闸门**:把 40 行(带 DeepSeek verdict 列)发 Discord / 终端给用户过目。**用户 [OK] 后才落 DB**(581 就是 park 在这个批准上)。
4. **seed 落 DB**:`scripts/seed_bq_primary_flags_20260421.py` —— idempotent、DB-backup-guarded(参照 `scripts/reconcile_reverse_drift_115_171_20260617.py` 的 `.bak`+audit 模式)。**不变量**:每题恰好一个 `is_primary=1`(置新前先把同题其它 link 的 is_primary 清 0,避免撞唯一索引);canonical key = `(question_id, example_id)`。

### DeepSeek 接线(MLI 目前无 DeepSeek 客户端 —— 要新建,照搬 pensieve 范式)
- **凭据加载**:照抄 pensieve 的安全审查过的范式 `pensieve/experiments/deepseek_spike/deepseek_creds.py` —— 手写 KEY=VALUE 解析、**绝不 os.environ**、key 放模块旁的 `.env.deepseek`(gitignored)、缺失时 `FileNotFoundError`(autorun 不带 key 的安全默认)、`__repr__` 掩码。三键 schema:`DEEPSEEK_API_KEY` / `DEEPSEEK_BASE_URL` / `DEEPSEEK_MODEL`。
- **现成 creds**:`pensieve/.env`(及 `pensieve/experiments/deepseek_spike/.env.deepseek`)已有真 key —— supervised session 复制到 MLI 对应 gitignored 路径即可(operator-authorized,别提交)。
- **客户端**:`openai` 2.41 已装(DeepSeek 走 OpenAI-compat SDK):`OpenAI(api_key=creds.key, base_url=creds.base_url)` → `chat.completions.create(model=creds.model, temperature=0, messages=[...])`。判官类用 **thinking/judgment 模式(temp 低、prompt 要求给结构化 verdict)**。
- [WARN] **坑**(memory `reference_toolchain_facts`):base_url **无 `/v1`**;**无 vision**;**2026-07-24 deprecated** —— 按后继型号组装或短期用完即走。长 prompt 分块、token 上限别小气(截断检测升档,memory `token_limits`)。
- **可选复用**:已定方向 §2 提过要做共享 helper `scripts/lib/ds_distill.py`(DeepSeek v4+分块+temp0+截断感知)。581 的 QA 判官可以是它的第一个消费者,或先内联、之后抽取。

### Deliverables(spec 指定)
- `docs/bq_primary_story_assignments_20260421.md` —— 40 行 `(question_id, primary_example_id, rationale)` + DeepSeek verdict 列。
- `scripts/seed_bq_primary_flags_20260421.py` —— idempotent、`.bak`-guarded、遵守每题唯一 primary 不变量。
- (新)MLI 版 `deepseek_creds.py`(或放 `scripts/lib/`)+ gitignored `.env.deepseek`。

### 验证(AC,做完逐条核)
- 每题恰好一个 `is_primary=1`:`SELECT question_id,COUNT(*) FROM question_example_links WHERE is_primary=1 GROUP BY question_id HAVING COUNT(*)>1` → **空**;且 40 个目标题各有 1 行。
- 真 endpoint 核 primary 出现在 API/前端(BQ drawer 用 primary story 突出卡 —— 见 583 Phase D,581 只置 flag,渲染是 582/583)。
- seed 幂等:二次跑 = no-op。`pytest -q` 全绿(基线 1315)。py_compile + ruff clean。
- **DeepSeek QA 留痕**:把 40 件的 DeepSeek verdict 存进 assignments doc(可回溯判官依据)。

### 解锁效应
581 done → 解锁 **582**(剩 ~36 题批量 probe_notes,DeepSeek 生成本命)→ **583**(前端 Phase D primary 卡 + probe panel)→ **585**(Phase E 漂移检测)。一次批准解锁整条 BQ-DEPTH 链。

---

## supervised run 运行说明(下个 session 照做)

### 0. 开工前(preflight)
```bash
cd "<...>/Gen_AI_Proj/MLInterviewPrep"
git status --short                      # 工作树该干净(上个 session 已收尾);有遗留先决定去留
ls .claude/autonomous.lock .claude/run-pgid   # 应都不存在(无在跑的 autorun)
python .claude/hooks/task_db.py pick    # 看默认拣选
python .claude/hooks/task_db.py get <ID> # 读权威 spec(AC 在 description),pick 给的或下方推荐的
```
- [WARN] **计费**:supervised(交互式)session 含其 subagent **走订阅池**;只有 `claude -p`/autorun 走单独 API 计费池(root memory `june15_programmatic_billing_split`)。本次是 supervised → 不动 autorun,不踩 API 池。
- **单写者**:同一 repo 别同时开第二个写 session、别手动改 tasks.db。

### 1. 选活(本 session 全是 supervised,逐条人值守,**不挂 autorun**)
为什么 supervised:每条都因下列至少一项需要人在环——`.claude/` sensitive-gate / 改活循环用的 task 基建 / manual-smoke AC / 写 MLSD golden 内容 / 破坏性 DB 操作 / 改名有语义风险。
**推荐拣选顺序**(由轻到重,先拿确定性高的;~~879/877~~ 已完成):

| 优先 | 任务 | 类 | 为何 supervised + 怎么做 |
|---|---|---|---|
| ~~①~~ | ~~**T-P2-879**〔S〕~~ [DONE] | DEBT | 已完成(`69ae26a`)。`task_store.py` SIM105 → `contextlib.suppress`。 |
| ~~②~~ | ~~**T-P2-877**〔M〕~~ [DONE] | DEBT | 已完成。`ruff check scripts/` 清零(排除 propagate 管理文件):safe `--fix` + 人审手改(B905 strict / B007 `_` / B023 默认参数 / F841 / E402)+ scripts/ per-file-ignore(N806/N803/E741/E701/E702/SIM102 写进 pyproject)。**未盲跑 unsafe-fixes**。残留 ~18 错全在 propagate 管理文件 = 独立 debt(root canonical + propagate)。 |
| ~~②~~ | ~~**T-P1-908**〔M〕~~ [DONE] | 内容 | 已完成(`7760c20`)。「ML Infra·LLM」SD tab + carve [300,400) + Pinterest 收边 [199,300)。vitest 247 + build + 真浏览器 smoke 全过。 |
| ~~①~~ | ~~**T-P1-881**〔S〕~~ [DONE] | MLSD | 已完成(`820bc4d`)。sd42 → oral_narrative;捕获成品 10504 口播稿进 seed + NULL 4 字段 + YAML archetype 声明;`audit_meta_mlsd_3rule.py` exit 0 / 0 findings sd41-44;pytest 1315。 |
| ~~①~~ | ~~**T-P2-880**〔S〕~~ [DONE] | SYNC | 已完成:**驳回照搬** study-review skill(blog-CLI 绑死 + MLI 已有自己的间隔重复系统)。 |
| ~~②~~ | ~~**T-P1-918 / 923**〕~~ [DONE] | Guard | 已完成:reverse-drift 甄别 + reconcile(115/171→not_started/0.0,user-confirmed stale)。补救侧收口。 |
| ~~①~~ | ~~**T-P1-581**〔M〕~~ [DONE] | BQ | 已完成(2026-06-17):top40 primary-story flags + DeepSeek QA 接线落地。 |
| ~~①~~ | ~~**T-P1-582**〔M〕~~ [DONE] | BQ | 已完成(2026-06-17):全 40 题 probe_notes,DeepSeek 4 批生成+人审 accept-default;normalizer 加数字比较 render-safe 改写。 |
| **① 下一活** | -> **T-P1-583**〔前端〕 | BQ | Phase D primary 卡 + probe panel,消费 581/582 数据。manual-smoke AC 必做。 |
| — | 内容簇起步(可选,较重) | 内容 | 先做共享 helper `scripts/lib/ds_distill.py`(DeepSeek v4+分块+temp0+截断感知)→ 开 CHEATSHEET 641 闸 → 644 跑 1 张蒸馏试点(人审 accept-default)。见「已定方向 §2」。 |

其余仍锁着:881(MLSD)/921(大改 drawer_nav)/ KG-INT B4(破坏性,dry-run 闸门)/ BQ-DEPTH(锁 581)/ Guard 917(`human_review=1`)——按各簇详解的链序,**到了再 supervised 逐条做**。

> **独立 debt(非任一现有任务,下一轮规划可考虑开新任务)**:① 跨项目 task_store.py 14 份副本的 SIM105 统一化,归 **T-P2-321**(propagate 管理化后一并修,别零散改)。② MLI 全树另有 **11 处 SIM105** 全在 propagate 管理文件(`scripts/lib/events.py`、`scripts/sweep_stuck_leases.py`、`scripts/workflows/*`、`route_and_record.py`)——须 **root canonical 改 + propagate**,不能 MLI 局部改(会被冲回);若要清,开一条 root 任务。

### 2. supervised 单任务循环(每拣一条都走一遍)
```
1) task_db.py update <ID> --status in_progress
2) task_db.py get <ID>            # 把 AC 当 definition of done;每条 if-AC 都要有 else 分支(见 CLAUDE.md 计划铁律)
3) 做改动                          # 改 DB → idempotent seed + Surface 表;写中文文件用 python 写 UTF-8
4) 验证(必做,缺一不可):
   - pytest -q                    # 全绿(上个 session 1315 passed 为基线)
   - 改了脚本/server/config → 真跑一遍(不只 mock):smoke 到预期状态
   - 修 bug → 必加回归测试(CLAUDE.md 要求);先证它对旧代码 FAIL 再对新代码 PASS
5) PROGRESS.md append 一条 session 条目(Bash heredoc,UTF-8 干净)
6) 显式路径 commit:git add <逐个路径> → [T-XX-N] 英文描述 → 不 push 到全做完
7) task_db.py complete <ID> --reviewer xushenghui   # hr=1 任务必须带 --reviewer;hr=0 也可带
```
- 一条做完、人看过没问题,再拣下一条。**别在一个 context 里串跑多条无关任务**(context 耗尽 + 共享态污染);要批量请改用 autorun 附录。
- 卡住/有判断分歧 → 停下问人,别 silent-gap-fill(memory `methodology_review_and_design`)。

### 3. 收尾(本 session 结束前)
```bash
python .claude/hooks/task_db.py project          # 刷新 TASKS.md
# 更新本 HANDOFF(就地改成当前真相:把做完的任务移出推荐表/标[DONE],接续点改写)
git add <显式路径> TASKS.md HANDOFF.md PROGRESS.md
git commit -m "[chore] supervised session: <做了什么> + handoff 更新"
git push origin main
```

### 4. 铁律(贯穿)
- **显式路径 commit**,**永不** `git add .`/`-A`/`-u`(`no_wildcard_add` 钩强制)。commit msg 英文(`commit_msg_guard` 拦 CJK),格式 `[T-XX-N] ...` 或 `[chore]/[ad-hoc]/[fix] ...`。
- 改 DB 内容 → 走 idempotent seed(Invariant 3)+ Surface Identification 表;**never EnterPlanMode**(用 task_db.py 规划)。
- 写中文文件用 `python` 写 UTF-8;PROGRESS append 用 Bash heredoc(干净)。
- **别抢跑**(memory `no_running_ahead_of_scope`):用户只让"写交接/计划"时只产文档,别顺手 commit/跑流水线/开下个任务。

---

## 附录:autorun 配方(当前无 autorun-safe 任务,留作下次有纯机械批活时参考)

`autonomous_run.sh` **不能指定目标**,只拣最高优先级 pickable;要 scope 到指定子集:
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
- 收尾每轮都做:恢复 park 的任务 → `active+ready`;`git stash pop`(PROGRESS.md 尾部冲突=保留双方);更新 HANDOFF → 显式路径 commit → push。
- [WARN] autorun 走单独 API 计费池;额度耗尽报 `You've hit your session limit · resets <t>`,session 空跑、不提交——等重置再跑。

## Pitfalls(本项目特有)
1. **TASKS.md 只读**(PreToolUse hook 拦截 Write/Edit)— 一切走 `task_db.py`;ID 自动生成,别手编。
2. **每个 DB 内容行须有 idempotent Python seed 脚本作真相源**(Invariant 3),禁 ad-hoc SQL;`invariant3_guard.py` 会拦截 schedule-shaped prose 写入 `company_documents.content`。
3. **改 DB 前先过 Surface Identification 表**(CLAUDE.md):widget→queryKey→endpoint→table,别按上一轮编辑目标 pattern-match(失败案例 `logs/2026-04-30_pinterest_root_cause.md`)。
4. **never 用 EnterPlanMode**;多任务执行委托 `scripts/autonomous_run.sh`,别在主 context 串跑多任务。
5. 中文写文件用 `python` 写 UTF-8,**别用 bash/PS heredoc 塞中文**(易乱码);PROGRESS append 用 Bash heredoc(UTF-8 干净)。
