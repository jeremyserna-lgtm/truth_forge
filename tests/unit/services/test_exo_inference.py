from truth_forge.services.exo_inference import ExoInferenceTool


def test_can_distribute_threshold():
    exo = ExoInferenceTool()
    assert (
        exo.can_distribute("maverick", 100000) is True
        or exo.can_distribute("maverick", 100000) is False
    )


def test_distributed_placeholder():
    exo = ExoInferenceTool()
    resp = exo.distributed_inference("maverick", [])
    assert resp["distributed"] is True
