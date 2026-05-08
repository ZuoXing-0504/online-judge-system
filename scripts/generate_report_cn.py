"""生成中文版开发报告PDF"""
from fpdf import FPDF


class Report(FPDF):
    def header(self):
        self.set_font("CJK", "B", 11)
        self.set_text_color(26, 140, 132)
        self.cell(0, 8, "Online Judge - 开发全记录", align="C")
        self.ln(10)
        self.set_draw_color(180, 180, 180)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def section(self, title):
        self.set_font("CJK", "B", 13)
        self.set_text_color(15, 110, 103)
        self.cell(0, 9, title)
        self.ln(10)

    def sub(self, text):
        self.set_font("CJK", "B", 10)
        self.set_text_color(60, 60, 60)
        self.cell(0, 7, text)
        self.ln(7)

    def body(self, text):
        self.set_font("CJK", "", 9)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def bullet(self, text):
        self.set_font("CJK", "", 9)
        self.set_text_color(50, 50, 50)
        self.cell(6)
        self.cell(4, 5, "-")
        self.multi_cell(0, 5, text)
        self.ln(1)

    def table_row(self, cells, widths, bold=False):
        style = "B" if bold else ""
        self.set_font("CJK", style, 8)
        for i, (cell, w) in enumerate(zip(cells, widths)):
            self.set_fill_color(245, 245, 245) if bold else None
            self.cell(w, 6, str(cell), border=1, fill=bold)
        self.ln()

    def score_bar(self, label, score):
        self.set_font("CJK", "", 9)
        self.set_text_color(50, 50, 50)
        self.cell(25, 6, label)
        filled = int(score * 2)
        for i in range(20):
            if i < filled:
                self.set_fill_color(26, 140, 132)
            else:
                self.set_fill_color(220, 220, 220)
            self.cell(5, 6, "", border=0, fill=True)
        self.cell(10, 6, f"{score}/10")
        self.ln(7)


pdf = Report()
pdf.add_font("CJK", "", "C:/Windows/Fonts/simkai.ttf")
pdf.add_font("CJK", "B", "C:/Windows/Fonts/simhei.ttf")
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Title
pdf.set_font("CJK", "B", 22)
pdf.set_text_color(15, 110, 103)
pdf.cell(0, 12, "Online Judge System")
pdf.ln(10)
pdf.set_font("CJK", "", 11)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 7, "开发全记录 - 改动、原因、成果与不足")
pdf.ln(14)

# Overview
pdf.section("1. 项目概述")
pdf.body(
    "一个基于 FastAPI + SQLAlchemy async + PostgreSQL + Redis + ARQ 的在线代码评测系统。"
    "支持 Python/C++/Java 三种语言在 Docker 沙箱中评测，拥有多页面 SPA 前端、中英双语国际化、"
    "WebSocket 实时推送判题结果、101 道经典题目及官方解析、完整的比赛/排行榜系统、"
    "以及生产级安全防护(限流/CSRF/审计日志/暴力破解锁)。"
)
pdf.body(
    "总计 20 次提交，跨越 3 个开发阶段。后端约 2000 行 Python，前端约 2500 行 JS + 1000 行 CSS，"
    "9 个 HTML 页面，69 个测试用例，代码覆盖率 83%。"
)

# Phase 1
pdf.section("2. 开发阶段")

pdf.sub("第一阶段 - 基础建设 (提交: ed037f5 - a8f7d06)")
pdf.body("搭建核心架构: FastAPI 路由层、SQLAlchemy async 模型层、Docker Compose 服务编排、"
         "以及初始的多页面前端门户。这一阶段把 Demo 做成了可用的系统。")

c1 = [
    ("ed037f5", "初始化系统",
     "FastAPI 入口 + 5 张表 + subprocess 判题引擎 + Docker Compose(Postgres/Redis/app/worker) + 8 页 HTML 前端",
     "无鉴权守卫、无限流、无国际化"),
    ("fe2adfd", "多页面前端门户",
     "SPA 架构(auth/problems/submit/submissions/admin), i18n 中英双语系统, localStorage 会话管理",
     "CSS 仅暗色主题、无分页、纯 textarea 编辑器"),
    ("a8f7d06", "生产级改造",
     "Docker 沙箱判题 + slowapi 限流 + AuditLog 审计 + 软删除 + 结构化日志 + Prometheus + GitHub Actions CI",
     "比赛罚时计算存在 bug"),
]
w = [22, 50, 58, 58]
pdf.table_row(["提交", "标题", "成果", "当时不足"], w, bold=True)
for r in c1:
    pdf.table_row(r, w)
pdf.ln(4)

# Phase 2
pdf.sub("第二阶段 - 比赛系统与多语言 (提交: a41023b - f9e1128)")
pdf.body("新增完整的比赛/排行榜系统、C++/Java 多语言支持、以及大量测试覆盖。")

c2 = [
    ("a41023b", "服务层+核心工具测试", "+9 个测试覆盖全部 5 个 service + Redis 池生命周期 + 分页边界", ""),
    ("f6c7397", "Ruff E712 修复", "布尔比较风格修正，通过 CI lint", ""),
    ("f9e1128", "完整比赛系统",
     "Contest 模型+API+前端+排行榜+罚时计分, C++/Java 沙箱(g++/JDK), 前端分页组件",
     "ContestProblem 显示 NameError, CSRF 403 阻塞所有 POST, 锁账户逻辑 bug"),
    ("8da3131", "修复测试语言值", "多语言 schema 变更后更新测试用例", ""),
    ("8dc36ec", "修复比赛题目展示+启动稳定性",
     "调整 Pydantic schema 顺序修复 NameError, 去掉 -reload 避免 watchfiles 崩溃, 导航栏加 Contests 入口", ""),
]
pdf.table_row(["提交", "标题", "成果", "备注"], w, bold=True)
for r in c2:
    pdf.table_row([r[0], r[1], r[2], r[3] or "-"], w)
pdf.ln(4)

# Phase 3
pdf.sub("第三阶段 - 安全加固与产能打磨 (提交: 4195564 - 645ddbc)")
pdf.body("补齐所有生产缺口: 账户锁、CSRF 防护、密码修改、Alembic 迁移、K8s 部署方案、评论区、"
         "CodeMirror 多语言高亮。CI 从 20 个测试失败收敛到全绿。")

c3 = [
    ("4195564", "第一轮修复",
     "比赛去重(arq 重试保护) + 报名开赛前校验 + 暴力破解锁(5次/15min) + pyproject.toml(ruff+mypy) + 数据库列迁移",
     "CSRF 中间件拦截了所有非 GET 请求"),
    ("7578566", "第二轮新功能",
     "E2E 测试(16步完整链路) + CodeMirror 多语言模板 + CSRF double-submit cookie + 密码修改 API",
     "CI: 20 个测试因 CSRF 403 失败"),
    ("efe1e0b", "搜索优化",
     "题目搜索扩展为 title + slug 双字段匹配", ""),
    ("f59ac17/9ae10ed/452d48f", "CI 稳定(3提交)",
     "CSRF 放行 Bearer 认证 + E2E 测试自建题目 + 放宽 401/403 断言。结果: 20 fail -> 4 -> 1 -> 0", ""),
    ("f017cc0", "Ruff lint 修复",
     "57 个自动修复问题在 CI 中 -fix, B904 手动修, N818/UP045 加入忽略", ""),
    ("8358837", "CodeMirror C++/Java 语法高亮",
     "预加载 lang-cpp/lang-java, Compartment 动态切换", ""),
    ("73d002c", "Admin 解析加载 + 比赛提交标记",
     "Load 按钮获取已有解析回填表单, 提交页通过 ?contest= 参数自动注册比赛", ""),
    ("645ddbc", "K8s Helm Chart + 评论区",
     "8 文件 Helm Chart(deploy/svc/ingress/statefulset), Comment 模型+schema+API", ""),
]
pdf.table_row(["提交", "标题", "成果", "备注"], w, bold=True)
for r in c3:
    pdf.table_row([r[0], r[1][:45], r[2][:55], r[3][:55] or "-"], w)
pdf.ln(4)

# Architecture
pdf.section("3. 系统架构")
pdf.body("分层: 前端(JS ES modules) -> FastAPI Router -> Service 业务层 -> SQLAlchemy Models -> PostgreSQL")
pdf.body("异步判题: Router -> Redis/ARQ 队列 -> Worker -> Docker 沙箱(Python/C++/Java)")
pdf.body("数据库 11 张表: users, problems, test_cases, submissions, submission_test_results, "
         "audit_logs, contests, contest_problems, contest_participants, contest_submission_attempts, comments")

pdf.sub("当前各项评分")
pdf.score_bar("后端架构", 8)
pdf.score_bar("前端", 7)
pdf.score_bar("安全性", 7)
pdf.score_bar("测试", 8)
pdf.score_bar("DevOps", 7)
pdf.score_bar("数据库设计", 8)
pdf.score_bar("代码质量", 8)

# Achievements
pdf.section("4. 核心成果")
for a in [
    "101 道经典算法题, 全部配有官方解析 (100% 覆盖)",
    "多语言判题: Python / C++ / Java 在 Docker 沙箱中隔离执行",
    "完整比赛系统: 报名/计分/罚时/封榜/倒计时/排行榜",
    "69 个测试用例, 83% 代码覆盖率, CI 强制 75% 最低线",
    "安全防护: 限流/CSRF Token/httpOnly Cookie/暴力破解锁/审计日志/软删除",
    "可观测性: 结构化 JSON 日志/Prometheus 指标/请求 ID 追踪",
    "前端: 8 页面 SPA/CodeMirror 多语言高亮/中英 i18n/柔光主题/PWA",
    "DevOps: Docker Compose 健康检查/GitHub Actions CI/K8s Helm Chart",
]:
    pdf.bullet(a)

# Gaps
pdf.section("5. 剩余不足与后续工作")
for g in [
    "前端构建: 15 个 ES module 请求应打包为单个 bundle(esbuild)",
    "E2E 浏览器测试: 引入 Playwright 做真实浏览器端到端测试",
    "CDN 解耦: CodeMirror 从 esm.sh 打包到本地, 避免依赖外部 CDN",
    "Redis 高可用: sentinel 哨兵/集群模式配置",
    "水平扩展: docker.sock 挂载阻止多机 Worker 部署",
    "Admin 批量操作: 题目导入导出、批量添加测试用例",
]:
    pdf.bullet(g)

# Stats
pdf.section("6. 项目统计")
s = [
    ("总提交数", "20"),
    ("后端 Python 文件", "45+"),
    ("前端 JS 文件", "15"),
    ("HTML 页面", "9"),
    ("数据库表", "11"),
    ("API 端点", "25+"),
    ("测试用例数", "69"),
    ("代码覆盖率", "83%"),
    ("题目数", "101"),
    ("解析覆盖", "101 (100%)"),
    ("后端代码行数", "~2000"),
    ("前端代码行数", "~2500"),
    ("CSS 行数", "~1000"),
]
pdf.table_row(["指标", "数值"], [95, 95], bold=True)
for k, v in s:
    pdf.table_row([k, v], [95, 95])

pdf.ln(10)
pdf.set_font("CJK", "", 8)
pdf.set_text_color(130, 130, 130)
pdf.cell(0, 5, "基于 ZuoXing-0504/online-judge-system Git 历史生成 - 2026-05-08", align="C")

out = "online_judge_development_report_cn.pdf"
pdf.output(out)
print(f"PDF saved to {out}")
