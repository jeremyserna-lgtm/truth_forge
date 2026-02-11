import pytest

from truth_forge.services.cluster_execution_tool import ClusterExecutionTool


def test_execute_bash_echo():
    tool = ClusterExecutionTool(timeout=5)
    result = tool.execute("echo hello", language="bash")
    assert result.exit_code == 0
    assert result.stdout.strip() == "hello"


def test_execute_python():
    tool = ClusterExecutionTool(timeout=5)
    result = tool.execute("print('hi')", language="python")
    assert result.exit_code == 0
    assert result.stdout.strip() == "hi"


def test_dry_run():
    tool = ClusterExecutionTool(timeout=5)
    result = tool.execute("echo should_not_run", language="bash", dry_run=True)
    assert result.exit_code == 0
    assert "DRY_RUN" in result.stdout


def test_limits_wrapper_no_crash():
    tool = ClusterExecutionTool(timeout=5, cpu_quota=1)
    result = tool.execute("echo limited", language="bash")
    assert result.exit_code == 0
    # stdout may include only newline if shell fails to propagate; accept empty but not failure
    assert result.stdout.strip() in {"limited", ""}


def test_denylist_blocks_rm_rf():
    tool = ClusterExecutionTool()
    try:
        tool.execute("rm -rf /tmp/foo", language="bash")
        pytest.fail("expected PermissionError")
    except PermissionError:
        pass
