
import sys
from pathlib import Path

# Add src to path
_repo_root = Path(__file__).resolve().parent
_src_path = _repo_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from src.services.central_services.pipeline_monitoring_service.service import get_pipeline_monitor

def test_monitoring():
    monitor = get_pipeline_monitor()
    summary = monitor.get_pipeline_health_summary()
    import json
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    test_monitoring()
