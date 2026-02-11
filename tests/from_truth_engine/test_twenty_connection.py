from src.services.central_services.contacts.twenty_crm import get_twenty_service
from src.services.central_services.core.secrets import get_secret

print("Secret retrieval test (TWENTY_API_KEY):")
secret = get_secret("TWENTY_API_KEY")
if secret:
    print(f"Found secret of length {len(secret)}")
else:
    print("Secret not found (expected if not set in GSM or Env)")

print("\nService initialization test:")
try:
    service = get_twenty_service()
    print("TwentyCRMService initialized successfully.")
    print(f"Base URL: {service.base_url}")
except Exception as e:
    print(f"Failed to initialize TwentyCRMService: {e}")

print("\nTool import test (MCP):")
try:
    from primitive_engine_mcp.tools.twenty_crm import twenty_crm_tool
    print(f"Tool {twenty_crm_tool.name} imported successfully.")
except Exception as e:
    print(f"Failed to import MCP tool: {e}")
