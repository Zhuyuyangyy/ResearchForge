"""
ResearchForge ProjectIngestor
负责读取已有项目，生成统一 ProjectDigest 结构
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


class ProjectDigest:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.project_name = self.project_path.name
        self.readme_files: List[str] = []
        self.docs_files: List[str] = []
        self.evidence_files: List[str] = []
        self.test_files: List[str] = []
        self.detected_modules: List[str] = []
        self.detected_apis: List[str] = []
        self.detected_ports: List[int] = []
        self.git_commit: Optional[str] = None
        self.git_branch: Optional[str] = None
        self.summary: str = ""
        self.limitations: List[str] = []
        self.scan_errors: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "project_path": str(self.project_path),
            "readme_files": self.readme_files,
            "docs_files": self.docs_files,
            "evidence_files": self.evidence_files,
            "test_files": self.test_files,
            "detected_modules": self.detected_modules,
            "detected_apis": self.detected_apis,
            "detected_ports": self.detected_ports,
            "git_commit": self.git_commit,
            "git_branch": self.git_branch,
            "summary": self.summary,
            "limitations": self.limitations,
            "scan_errors": self.scan_errors,
        }


def _safe_read(path: Path, limit: int = 32768) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(limit)
    except Exception:
        return None


def _scan_readmes(root: Path, digest: ProjectDigest):
    patterns = ["README.md", "README*.md", "readme.md", "Readme.md"]
    found = set()
    for p in patterns:
        for f in root.glob(p):
            if f.is_file():
                rel = str(f.relative_to(root))
                if rel not in found:
                    found.add(rel)
                    digest.readme_files.append(rel)
    if digest.readme_files:
        first = root / list(found)[0]
        content = _safe_read(first, 2048) or ""
        lines = [l.strip() for l in content.split("\n") if l.strip()]
        digest.summary = "\n".join(lines[:5]) if lines else ""


def _scan_docs(root: Path, digest: ProjectDigest):
    for dd in [root / "docs", root / "doc"]:
        if not dd.exists():
            continue
        for f in dd.rglob("*.md"):
            rel = str(f.relative_to(root))
            if rel not in digest.readme_files:
                digest.docs_files.append(rel)
        for f in dd.rglob("*.json"):
            rel = str(f.relative_to(root))
            if any(k in rel for k in ["demo_evidence", "benchmark", "evidence", "test_cases"]):
                if rel not in digest.evidence_files:
                    digest.evidence_files.append(rel)
            else:
                if rel not in digest.docs_files:
                    digest.docs_files.append(rel)


def _scan_tests(root: Path, digest: ProjectDigest):
    for td in [root / "tests", root / "test"]:
        if not td.exists():
            continue
        for f in td.rglob("test_*.py"):
            rel = str(f.relative_to(root))
            if rel not in digest.test_files:
                digest.test_files.append(rel)
        for f in td.rglob("*_test.py"):
            rel = str(f.relative_to(root))
            if rel not in digest.test_files:
                digest.test_files.append(rel)


def _scan_evidence(root: Path, digest: ProjectDigest):
    patterns = [
        "**/demo*.json",
        "**/benchmark*.json",
        "**/benchmark_report*.json",
        "**/test_cases*.json",
        "**/confusion_matrix*.json",
    ]
    for p in patterns:
        for f in root.glob(p):
            if f.is_file():
                rel = str(f.relative_to(root))
                if rel not in digest.evidence_files:
                    digest.evidence_files.append(rel)


def _scan_code_structure(root: Path, digest: ProjectDigest):
    """从 backend/app.py 或 backend/app/api/routes.py 提取 API 和模块"""
    # 找 FastAPI 路由定义文件
    routes_candidates = [
        root / "backend" / "app" / "api" / "routes.py",
        root / "backend" / "app" / "routes.py",
        root / "backend" / "routes.py",
        root / "backend" / "app.py",  # single-file FastAPI app
        root / "app" / "api" / "routes.py",
        root / "routes.py",
    ]
    routes_file = None
    for f in routes_candidates:
        if f.exists():
            routes_file = f
            break

    if routes_file:
        # single-file app.py has routes typically after line 300
        content = _safe_read(routes_file, 30000) or ""
        route_pattern = re.compile(
            r'@(?:router|app)\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)',
            re.IGNORECASE
        )
        for m in route_pattern.finditer(content):
            digest.detected_apis.append(f"{m.group(1).upper()} {m.group(2)}")

    # 找 main.py / app.py 获取端口（支持中文注释：端口：8011）
    main_candidates = [
        root / "backend" / "app" / "main.py",
        root / "backend" / "main.py",
        root / "backend" / "app.py",
        root / "main.py",
    ]
    port_pattern = re.compile(r'\b([2-9]\d{3,4})\b')
    for mf in main_candidates:
        if not mf.exists():
            continue
        content = _safe_read(mf, 30000) or ""
        # 找包含 port/PORT/listen/端口 的行，再从中提取数字
        for line in content.split('\n'):
            if any(kw in line for kw in ['port', 'PORT', 'listen', '端口']):
                m = port_pattern.search(line)
                if m:
                    p = int(m.group(1))
                    if 2000 <= p <= 65535 and p not in digest.detected_ports:
                        digest.detected_ports.append(p)
        break  # 只读第一个

    # 扫描 app/ 或 src/ 下的 Python 模块
    for app_dir in [root / "app", root / "backend" / "app", root / "src"]:
        if not app_dir.exists():
            continue
        for sub in app_dir.iterdir():
            if sub.is_dir() and not sub.name.startswith("_"):
                if sub.name not in digest.detected_modules:
                    digest.detected_modules.append(sub.name)
            elif sub.name.endswith(".py") and sub.name not in ["__init__.py", "main.py", "app.py"]:
                name = sub.stem
                if name not in digest.detected_modules:
                    digest.detected_modules.append(name)


def _get_git_info(root: Path, digest: ProjectDigest):
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(root), capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0:
            digest.git_commit = r.stdout.strip()
        r2 = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(root), capture_output=True, text=True, timeout=5,
        )
        if r2.returncode == 0:
            digest.git_branch = r2.stdout.strip()
    except Exception:
        pass


def ingest_project(project_path: str) -> Dict[str, Any]:
    root = Path(project_path)
    if not root.exists() or not root.is_dir():
        return {"error": f"路径不存在或不是目录: {project_path}"}

    digest = ProjectDigest(project_path)

    for scanner in [
        _scan_readmes,
        _scan_docs,
        _scan_tests,
        _scan_evidence,
        _scan_code_structure,
        _get_git_info,
    ]:
        try:
            scanner(root, digest)
        except Exception as e:
            digest.scan_errors.append(f"{scanner.__name__}: {e}")

    digest.limitations = [
        "无法自动判断代码实际运行正确性（需要执行验证）",
        "无法自动判断 SCI / 专利新颖性（需要领域专家）",
        "无法自动判断真实机械臂硬件可用性（需要实际部署）",
        "模块功能描述依赖启发式规则，可能误判",
    ]

    return digest.to_dict()