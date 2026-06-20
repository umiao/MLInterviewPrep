# Session Handoff — 2026-06-19 (supervised, CHEATSHEET-2)

> 给**新 session** 的接续报告。一次性快照,读完即可丢。权威细节:任务 spec 取 DB(`task_db.py get <ID>`)、经验见 `LESSONS.md`、Surface/路由见 `CLAUDE.md`。
> 本文件覆盖了同日早先的 Adobe-B4a 快照(那批已落地,见下方"历史");当前焦点是 CHEATSHEET 轨道。

## TL;DR

本 session 接续 CHEATSHEET 轨道,完成 **T-P1-642**(前端 Cheat Sheet 标签页)+ 用户要求的视觉提升。

| 任务 | 结果 | commit |
|---|---|---|
| **T-P1-642** CHEATSHEET-2 前端标签页 | ✅ 完成 + 全量验证 | `aa121b9` |
| T-P1-642 视觉提升(右对齐+琥珀+闪电图标) | ✅ 用户反馈后追加 | `21e1a82` |

**净结果:642 完成,已 push 到 origin/main。** 前序 641(schema+API)早已完成。

### 642 交付物
- `src/frontend/src/components/CheatSheetCard.tsx`(新)—— 粘性标题栏 + 分类徽章 + "Full design →" Link + MarkdownPreview(KaTeX/GFM)+ 空状态。`<section id={slug}>` 为深链锚点。
- `src/frontend/src/components/CheatSheetCard.test.tsx`(新,3 测试)。
- `src/frontend/src/pages/SystemDesignList.tsx` —— 第 6 个标签页(右对齐+琥珀+闪电 SVG)、独立 cheat-sheets query、桌面端粘性 TOC 侧栏、`?tab=cheatsheet#<slug>` 深链滚动、`cheatSheetCategory()` 按 display_order 区间推导徽章。

### 验证证据
- vitest 全套 **254/254**;新组件 3/3;`tsc --noEmit` + eslint 干净;`vite build` 通过。
- **真实端点冒烟**:uvicorn 起,`GET /api/system-designs/cheat-sheets` 返回 **53 条**(43 有 cheat_sheet → 内容卡;10 → 空状态卡),字段与 `SystemDesignCheatSheet` 完全一致,按 display_order 排序。**53 ≫ 35+ AC**。
- 用户已在 http://localhost:5173/system-design?tab=cheatsheet 现场查看。

## 当前运行态(重要)

- **两个 dev server 仍在后台跑**(本 session 为给用户现场看而起):
  - 后端 uvicorn → `127.0.0.1:8100`(日志 `logs/backend_dev.log`)
  - 前端 vite → `localhost:5173`(日志 `logs/frontend_dev.log`)
  - **停掉**:`taskkill //F //IM python.exe`(慎,会杀所有 python)或按 PID;或 PowerShell `Get-Process python,node | Stop-Process`。日志在 gitignore 的 `logs/` 下,无需提交。
- `task_db.py pick` = **none**(642 完成,其余 dep-gated / 需输入 / parked)。
- **909**(ML-Infra golden seed,缺用户 `distributed_model_deployment_golden.md`)+ **921**(WSH-E1 drawer_nav,manual browser-smoke)仍 **PARK**。

## 下一步选项(按 ROI)

### Track A — CHEATSHEET 续作(study-ROI 最高,全 supervised)
- **T-P1-643** [CHEATSHEET-3] 从 doc 85 加 2 个 Uber 行(Restaurant Rec + Budget-Constrained Promo)到 system_designs。**DB 内容写入** → 必须 idempotent seed(Invariant 3)+ 对照 Surface Identification 表。**轻、无外部依赖**(源在 doc 85),建议下一个做。
- **T-P1-644–648** 作者化 cheat-sheets(4 eBay 项目 / 4 eBay refs / 7 Pinterest / 10 generic b1 / 9 generic b2)——★ **DeepSeek 蒸馏 + 人审 accept-default**。**前置:把 DeepSeek key 复制到 gitignored `scripts/lib/.env.deepseek`**(pensieve 有现成)。建议先写共享 helper `scripts/lib/ds_distill.py`,再跑 644 一张试点。
- **T-P1-649** [CHEATSHEET-9] smoke(dep 648)。注:spec 写 "37 cards",当前 system_designs 已 53 行,执行时按实际数核对。

### Track B — KG-INT Adobe B4b execute(T-P1-829)
- 用户已裁决 open questions(见 `docs/archive_plans/B4a-adobe_2026-06-19.md` SS6),但 **829 仍被 B4b 串行链 dep-fenced**(depends T-P0-828)。要单独执行需**故意 unblock**。
- **破坏性硬归档**(DELETE ~270K 字 + restore.sql + skeleton seed + 7 步证明),**必须 supervised**;execute 前用户最终拍 Q2 的 (a)/(b)/(c)。
- 另有 **B4b-uber**(同类硬归档)在队列。

### Track C — 其余 4 份缺失 B4a plan(linkedin/tiktok/doordash/parspec)
- 安全 dry-run(不写 DB),每个产出后用户 review open questions。

## 运行规程提醒
- 计费:supervised 走订阅池;`claude -p`/autorun 走单独 API 池。
- 显式路径 commit,**永不** `git add .`;commit msg 英文 `[T-XX-N]` / `[chore]`。
- 改 DB 内容 → idempotent seed(Invariant 3)+ Surface Identification 表;**禁 emoji**;**never EnterPlanMode**。
- 写中文文件用 `python` 前置 `PYTHONUTF8=1 PYTHONIOENCODING=utf-8`(Windows 控制台 cp1252)。
- **教训(仍有效)**:`state='pending'` 的 PARK 挡不住 autorun inner agent 自主拣选;真正 fence 子集要靠阻塞 dep 或抽走素材。kill autorun 后务必重查 `git log` / task 状态(commit count delta 是 tell)。

## 本 session commits(已 push)
- `aa121b9` [T-P1-642] Add Cheat Sheet tab to /system-design with one-pager card per module
- `21e1a82` [T-P1-642] Give Cheat Sheet tab special status: right-align + amber + bolt icon

## 历史(同日早先,已落地)
- `38abecb` [T-P1-815] Resolve Adobe B4a open questions(Q2 DB 实证 + 交接)
- `335b481` / `b1e67ed` / `9af4be2` / `c88ee52` —— 见 git log。
