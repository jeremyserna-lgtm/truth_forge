from truth_forge.services.cluster_execution_tool import ClusterExecutionTool


class DummyClusterState:
    def pick_least_loaded(self) -> str:
        return "dummy-node"


def test_node_any_uses_cluster_state():
    tool = ClusterExecutionTool(timeout=5)
    tool.cluster_state = DummyClusterState()
    res = tool.execute("echo hi", node="any", dry_run=True)
    assert res.node == "dummy-node"
