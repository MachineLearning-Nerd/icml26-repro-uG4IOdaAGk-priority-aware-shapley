"""Fail-closed verification for the published PASV repository surface."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CANONICAL = "MachineLearning-Nerd <MachineLearning-Nerd@users.noreply.github.com>"
REQUIRED_FILES = (
    "README.md",
    "STATUS.md",
    "CLAIM_EVIDENCE.md",
    "SOURCE_MANIFEST.md",
    "BRANCH_AUDIT.md",
    "CITATION.cff",
    "docs/paper.txt",
    "outputs/summary.json",
    "outputs/c3_scalability_attempts.json",
)


def command(*args: str) -> str:
    completed = subprocess.run(
        args,
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return completed.stdout


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        fail(f"missing required files: {missing}")

    if command("git", "branch", "--show-current").strip() != "main":
        fail("expected current branch main")

    remote = command("git", "remote", "get-url", "origin").strip()
    expected_remote = "https://github.com/MachineLearning-Nerd/icml26-priority-aware-shapley"
    if remote.rstrip("/").removesuffix(".git") != expected_remote:
        fail(f"unexpected origin: {remote}")

    refs = command("git", "for-each-ref", "--format=%(refname)").splitlines()
    forbidden = [ref for ref in refs if "/orx/" in ref or ref.endswith("/master")]
    if forbidden:
        fail(f"legacy branches remain: {forbidden}")

    identity_lines = command(
        "git", "log", "--all", "--format=%an <%ae>%x09%cn <%ce>"
    ).splitlines()
    noncanonical = [
        line for line in identity_lines if line.split("\t") != [CANONICAL, CANONICAL]
    ]
    if noncanonical:
        fail(f"non-canonical commit identities: {noncanonical[:3]}")

    summary = json.loads((ROOT / "outputs/summary.json").read_text())
    verdict = summary.get("verdict", {})
    if verdict != {"C1_verified": True, "C2_verified": True, "C3_verified": True}:
        fail(f"unexpected claim verdict: {verdict}")

    scalability = json.loads(
        (ROOT / "outputs/c3_scalability_attempts.json").read_text()
    )
    attempts = {item["id"]: item for item in scalability["attempts"]}
    required_passes = [*range(1, 10), 11]
    if scalability.get("verdict") != "verified":
        fail("large-scale C3 verdict is not verified")
    if scalability.get("approaches_passed") != 10 or scalability.get("approaches_total") != 11:
        fail("unexpected C3 route counts")
    if not all(attempts[index]["passed"] for index in required_passes):
        fail("an accepted C3 route failed")
    if attempts[10]["passed"]:
        fail("retained negative-control route unexpectedly passed")
    if attempts[1]["evidence"]["n"] != 8192:
        fail("C3 scale anchor missing")

    pytest_output = command(sys.executable, "-m", "pytest", "-q", "repro/tests/test_pasv.py")
    if "passed" not in pytest_output:
        fail("focused pytest run did not report passing tests")

    print("FINAL_VERIFICATION_PASS")
    print("branch=main")
    print(f"origin={remote}")
    print("commit_identity=canonical")
    print("claim_verdicts=C1 VERIFIED; C2 VERIFIED; C3 VERIFIED")
    print("c3_negative_control=retained_route_10")
    print("focused_tests=PASS")


if __name__ == "__main__":
    main()
