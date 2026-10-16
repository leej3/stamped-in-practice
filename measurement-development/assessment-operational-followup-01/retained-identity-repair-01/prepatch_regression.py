"""Run the new admission acceptance cases against the exact prepatch guard."""
import ast
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path.cwd() / "scripts"))
import assessment_procedure
import pytest

source = subprocess.check_output([
    "git", "show", "22bd357edca8095ef501cdc15f3b6d8884c2b40b:scripts/assessment_procedure.py"], text=True)
tree = ast.parse(source)
guard = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
             and node.name == "check_retained_target")
exec(compile(ast.Module(body=[guard], type_ignores=[]), "prepatch-assessment-procedure", "exec"),
     assessment_procedure.__dict__)
raise SystemExit(pytest.main([
    "-q", "tests/test_operational_assessment.py",
    "-k", "test_v4_shared_git_identities_bind_each_original_capture"]))
