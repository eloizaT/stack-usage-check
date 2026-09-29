import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("name", "usage", "expected_exit", "expected_issue"),
    [
        ("normal", 128, 0, None),
        ("warning", 800, 0, None),
        ("over_limit", 900, 1, "85%"),
        ("default_output", 128, 1, "NoneType"),
        ("default_threshold", 128, 1, "NoneType"),
        ("runnable_after_helper", 128, 0, None),
    ],
)
def test_generate_cli_scenarios(tmp_path, name, usage, expected_exit, expected_issue):
    case_dir = tmp_path / name
    objects = case_dir / "objects"
    objects.mkdir(parents=True)

    prefix = "demo.c:1:1:helper\t16\tstatic\n" if name == "runnable_after_helper" else ""
    (objects / "demo.su").write_text(
        prefix + f"demo.c:2:1:Run_Demo_Step\t{usage}\tstatic\n"
    )
    (case_dir / "application.map").write_text(
        "0x0000 0x0000 1024 object Task_STACK_Array\n"
    )
    (case_dir / "Rte.arxml").write_text(
        "<AUTOSAR>\n"
        "<REFERENCE-VALUES>\n"
        '<VALUE-REF DEST="TIMING-EVENT">/Events/DemoStep</VALUE-REF>\n'
        '<VALUE-REF DEST="ECUC-CONTAINER-VALUE">/Tasks/Task</VALUE-REF>\n'
        "</REFERENCE-VALUES>\n"
        "</AUTOSAR>\n"
    )

    metadata = tmp_path / "metadata/stack_usage_check-0.0.0.dist-info"
    metadata.mkdir(parents=True)
    (metadata / "METADATA").write_text(
        "Metadata-Version: 2.1\nName: stack_usage_check\nVersion: 0.0.0\n"
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(REPO_ROOT / "src"), str(metadata.parent)]
    )

    command = [
        sys.executable,
        "-B",
        "-m",
        "stack_usage_check",
        "generate",
        "--obj-dir",
        str(objects),
        "--map-file",
        str(case_dir / "application.map"),
        "--rte-arxml",
        str(case_dir / "Rte.arxml"),
    ]
    if name != "default_output":
        command += ["--output", str(case_dir / "report.json")]
    if name != "default_threshold":
        command += ["--memory-threshold-limit", "0.85"]

    result = subprocess.run(
        command, cwd=case_dir, env=env, text=True, capture_output=True
    )
    output = case_dir / ("stack_report.json" if name == "default_output" else "report.json")

    assert result.returncode == expected_exit, result.stderr
    if name == "default_output":
        assert not output.exists()
        assert "TypeError:" in result.stderr
        assert expected_issue in result.stderr
    elif name == "runnable_after_helper":
        assert json.loads(output.read_text()) == []
    else:
        assert json.loads(output.read_text()) == [
            {
                "container": "Task",
                "stack_size": 1024,
                "unit": "bytes",
                "functions": [
                    {
                        "function": "Run_Demo_Step",
                        "memory_usage": usage,
                        "container": "Task",
                        "container_allocated_stack_size": 1024,
                    }
                ],
            }
        ]
        if name in {"default_threshold", "over_limit"}:
            assert expected_issue in result.stderr
        else:
            assert ("WARNING:" in result.stderr) == (name == "warning")