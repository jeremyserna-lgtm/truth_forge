# Model Endpoint Matrix (King)

| Model      | Endpoint            | Status            | Storage (symlinked)                                                   |
|------------|---------------------|-------------------|------------------------------------------------------------------------|
| Scout      | http://localhost:8765/v1 | ✅ running        | `~/.cache/huggingface/hub/models--mlx-community--Llama-4-Scout-17B-16E-Instruct-8bit` → `/Volumes/Sabrent 8TB External/models/cache/huggingface/hub/...` |
| Maverick   | http://localhost:8766/v1 | ✅ running        | `~/.cache/huggingface/hub/models--mlx-community--DeepSeek-R1-4bit` (278GB) → external drive |
| R1         | http://localhost:8767/v1 | ⏳ downloading    | `~/.cache/huggingface/hub/models--mlx-community--DeepSeek-R1-4bit` (159GB/400GB) |

Notes:
- LaunchAgent uses internal cache symlinks to reach models on external drive (macOS permission workaround).
- Cognitive Bridge is enabled (`cognitive_bridge_enabled: true`) and will route based on availability; R1 will fallback until download completes.
