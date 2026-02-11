from truth_forge.services.cluster_execution_tool import ClusterExecutionTool


def test_streaming_output():
    tool = ClusterExecutionTool(timeout=5)
    # Use printf to produce multiple lines predictably
    result = tool.execute("printf 'a\\n'", language="bash", stream=True)
    assert result.exit_code == 0
    assert result.stdout == "a\n"
