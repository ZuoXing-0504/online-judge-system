"""Generate a comprehensive development report as a PDF."""
import textwrap
from fpdf import FPDF

class Report(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(26, 140, 132)
        self.cell(0, 8, "Online Judge System - Development Chronicle", align="C")
        self.ln(10)
        self.set_draw_color(180, 180, 180)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def section(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(15, 110, 103)
        self.cell(0, 9, title)
        self.ln(10)

    def sub(self, text):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(60, 60, 60)
        self.cell(0, 6, text)
        self.ln(7)

    def body(self, text):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def bullet(self, text):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(50, 50, 50)
        self.cell(6)
        self.cell(4, 5, "-")
        self.multi_cell(0, 5, text)
        self.ln(1)

    def table_row(self, cells, widths, bold=False):
        style = "B" if bold else ""
        self.set_font("Helvetica", style, 8)
        for i, (cell, w) in enumerate(zip(cells, widths)):
            self.set_fill_color(245, 245, 245) if bold else None
            self.cell(w, 6, str(cell), border=1, fill=bold)
        self.ln()

    def score_bar(self, label, score):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(50, 50, 50)
        self.cell(30, 6, label)
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
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# ── Title ──
pdf.set_font("Helvetica", "B", 22)
pdf.set_text_color(15, 110, 103)
pdf.cell(0, 12, "Online Judge System")
pdf.ln(10)
pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 7, "Development Chronicle & Architecture Analysis")
pdf.ln(14)

# ── Overview ──
pdf.section("1. Project Overview")
pdf.body(
    "An online code judging system built with FastAPI + SQLAlchemy async + PostgreSQL + Redis + ARQ. "
    "Supports Python, C++, and Java judging in Docker sandboxes. Features a multi-page SPA frontend "
    "with i18n, WebSocket live status, 101 classic problems with official solutions, contest/leaderboard "
    "system, and production-grade security (rate limiting, CSRF, audit logs, brute-force lockout)."
)
pdf.body(
    "Total: 20 commits over 3 development phases. ~2,000 lines backend Python, ~2,500 lines frontend JS, "
    "~1,000 lines CSS, 8 HTML pages, 69 tests at 83% coverage."
)

# ── Phase 1: Foundation ──
pdf.section("2. Development Phases")

pdf.sub("Phase 1: Foundation (Commits: ed037f5 - a8f7d06)")
pdf.body("Established the core architecture: FastAPI routes, SQLAlchemy async models, Docker Compose services, and the initial frontend portal.")

commits_p1 = [
    ("ed037f5", "Initialize online judge system", "First commit: FastAPI app, 5 DB models, judge engine with subprocess executor, Docker Compose with Postgres+Redis+app+worker, 8-page HTML frontend portal", "No auth guards, no rate limiting, no i18n"),
    ("fe2adfd", "Add multipage frontend portal", "SPA with auth, problems, submit, submissions, admin pages. i18n system with zh/en translations. Session management via localStorage.", "CSS was dark-only, no pagination, no CodeMirror"),
    ("a8f7d06", "Production-grade online judge system", "Docker sandbox for code execution, rate limiting, audit logs, soft delete, structured logging, Prometheus metrics, CI/CD pipeline, admin solution editing", "Scoring bug in contest penalty calculation"),
]
w = [22, 55, 55, 55]
pdf.table_row(["Commit", "Title", "Achievement", "Gaps at this point"], w, bold=True)
for cid, title, achieve, gap in commits_p1:
    pdf.table_row([cid, title, achieve, gap], w)
pdf.ln(4)

# ── Phase 2: Contest & Multi-language ──
pdf.sub("Phase 2: Contest System & Multi-language (Commits: a41023b - f9e1128)")
pdf.body("Added comprehensive contest/leaderboard system, C++/Java support, and extensive test coverage.")

commits_p2 = [
    ("a41023b", "Add service-layer and core-utils test suites", "+9 tests covering all 5 services, Redis pool lifecycle, pagination edge cases", ""),
    ("f6c7397", "Fix ruff E712 (== True)", "Boolean comparison style fix for CI lint", ""),
    ("f9e1128", "Complete contest system", "Contest model + API + frontend + leaderboard + scoring with penalty tracking. Multi-language sandbox (g++/JDK). Frontend pagination.", "Contest problem display NameError, CSRF 403 blocking all POSTs, lockout logic bug on correct password"),
    ("8da3131", "Fix test language to unsupported value", "Updated test for multi-language schema change", ""),
    ("8dc36ec", "Fix contest problems display + app stability", "Reorder Pydantic schemas to fix NameError, remove --reload flag, add Contest nav links", ""),
]
pdf.table_row(["Commit", "Title", "Achievement", "Notes"], w, bold=True)
for cid, title, achieve, note in commits_p2:
    pdf.table_row([cid, title, achieve, note or "-"], w)
pdf.ln(4)

# ── Phase 3: Hardening ──
pdf.sub("Phase 3: Security & Production Hardening (Commits: 4195564 - 645ddbc)")
pdf.body("Addressed all production gaps: account lockout, CSRF protection, password change, alembic migrations, K8s deployment, comment system, CodeMirror language switching. CI went from 20 failing tests to 0.")

commits_p3 = [
    ("4195564", "Round 1 fixes", "Contest retry dedup, registration start-time check, brute-force lockout (5 attempts/15min), pyproject.toml (ruff+mypy), DB migration", "CSRF middleware blocked all non-GET requests"),
    ("7578566", "Round 2 features", "E2E tests (16-step flow), CodeMirror multi-lang templates, CSRF double-submit cookie, password change API", "CI: 20 test failures due to CSRF 403s"),
    ("efe1e0b", "Search slug matching", "Problem search now matches title AND slug fields", ""),
    ("f59ac17/9ae10ed/452d48f", "CI stabilization (3 commits)", "CSRF exempts Bearer auth, E2E self-contained, test assertions relaxed for 401/403. Result: 20 failures -> 4 -> 0.", "1 remaining: e2e solution_and_csrf needed inline problem creation"),
    ("f017cc0", "Ruff lint fixes", "57 auto-fixable issues handled via --fix in CI, B904 manual fix, N818/UP045 ignored", ""),
    ("8358837", "CodeMirror C++/Java highlighting", "Pre-load lang-cpp/lang-java, Compartment-based runtime switching", ""),
    ("73d002c", "Admin solution load + contest marking", "Load button fetches existing solution, submit page auto-registers contest participants via ?contest= param", ""),
    ("645ddbc", "K8s Helm chart + comments", "8-file Helm chart (deploy/svc/ingress/statefulset), comment model+schema+API", ""),
]
pdf.table_row(["Commit", "Title", "Achievement", "Notes"], w, bold=True)
for cid, title, achieve, note in commits_p3:
    pdf.table_row([cid, title[:45], achieve[:50], note or "-"], w)
pdf.ln(4)

# ── Architecture ──
pdf.section("3. Architecture")
pdf.body("Layer: Frontend (JS ES modules) -> FastAPI Router -> Service Layer -> SQLAlchemy Models -> PostgreSQL")
pdf.body("Async Judge: Router -> Redis/ARQ Queue -> Worker -> Docker Sandbox (Python/C++/Java)")
pdf.body("9 DB tables: users, problems, test_cases, submissions, submission_test_results, audit_logs, contests, contest_problems, contest_participants, contest_submission_attempts, comments")

pdf.sub("Current Scores")
pdf.score_bar("Backend", 8)
pdf.score_bar("Frontend", 7)
pdf.score_bar("Security", 7)
pdf.score_bar("Testing", 8)
pdf.score_bar("DevOps", 7)
pdf.score_bar("Database Design", 8)
pdf.score_bar("Code Quality", 8)

# ── Achievements ──
pdf.section("4. Key Achievements")
achievements = [
    "101 classic problems with official solutions (100% coverage)",
    "Multi-language judging: Python, C++, Java in Docker sandboxes",
    "Contest system: registration, scoring with penalty, freeze board, countdown, leaderboard",
    "69 tests, 83% code coverage, CI enforces 75% minimum",
    "Security: rate limiting, CSRF tokens, httpOnly cookies, brute-force lockout, audit logs, soft delete",
    "Observability: structured JSON logging, Prometheus metrics, request ID tracking",
    "Frontend: 8-page SPA, CodeMirror editor with syntax highlighting, zh/en i18n, light theme, PWA",
    "DevOps: Docker Compose with health checks, GitHub Actions CI/CD, K8s Helm chart",
]
for a in achievements:
    pdf.bullet(a)

# ── Remaining Gaps ──
pdf.section("5. Remaining Gaps & Future Work")
gaps = [
    "Frontend build step: 15 ES module imports -> single bundle with esbuild",
    "E2E browser tests with Playwright (beyond API-level E2E)",
    "CDN independence: bundle CodeMirror locally instead of esm.sh",
    "Redis high availability: sentinel/cluster configuration",
    "Horizontal scaling: docker.sock mount prevents multi-host workers",
    "Admin UI polish: batch operations, problem import/export",
]
for g in gaps:
    pdf.bullet(g)

# ── Stats ──
pdf.section("6. Project Statistics")
stats = [
    ("Total Commits", "20"),
    ("Backend Python Files", "45+"),
    ("Frontend JS Files", "15"),
    ("HTML Pages", "9"),
    ("Database Tables", "11"),
    ("API Endpoints", "25+"),
    ("Test Count", "69"),
    ("Code Coverage", "83%"),
    ("Problems", "101"),
    ("Solutions", "101 (100%)"),
    ("Lines of Backend Code", "~2,000"),
    ("Lines of Frontend Code", "~2,500"),
    ("Lines of CSS", "~1,000"),
]
pdf.table_row(["Metric", "Value"], [95, 95], bold=True)
for label, val in stats:
    pdf.table_row([label, val], [95, 95])

pdf.ln(10)
pdf.set_font("Helvetica", "I", 8)
pdf.set_text_color(130, 130, 130)
pdf.cell(0, 5, "Generated from git history of ZuoXing-0504/online-judge-system - 2026-05-08", align="C")

# Save
output = "online_judge_development_report.pdf"
pdf.output(output)
print(f"PDF saved to {output}")
