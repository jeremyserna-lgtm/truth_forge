import pytest

from truth_forge.services.cluster_execution_tool import ClusterExecutionTool


@pytest.mark.skip(reason="ssh endpoint not available in CI environment")
def test_remote_exec_placeholder():
    tool = ClusterExecutionTool(timeout=2)
    res = tool.execute("echo remote", node="king", dry_run=True)
    assert res.exit_code == 0
