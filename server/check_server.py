from mcp.server.mcpserver import MCPServer

from buyer.check import check_all
from buyer.intent import IntentRecord
from buyer.prepared import Prepared
from server.guard import is_public_url

# Initialize the MCP Server
mcp = MCPServer("check_server")

@mcp.tool()
def check_purchase(intent: dict, prepared_answer: dict, rpc_url: str | None = None) -> dict:
    """Checks whether a prepared purchase is safe to sign based on the pinned intent."""
    
    # 1. Validate the RPC URL using the guard if one is provided
    if rpc_url is not None:
        if not is_public_url(rpc_url):
            return {
                "passed": False, 
                "field": "rpc_url", 
                "asked": "public https url", 
                "found": rpc_url
            }
            
    # 2. Rebuild the objects (keyless operation, no signers loaded)
    try:
        intent_record = IntentRecord(**intent)
        prepared = Prepared.from_answer(prepared_answer)
    except Exception as e:
        return {"passed": False, "field": "parse", "asked": "valid inputs", "found": str(e)}
        
    # 3. Run the checks you wrote in check.py
    verdict = check_all(intent_record, prepared)
    
    # 4. Return the result
    if verdict.passed:
        return {"passed": True}
        
    # 5. On refusal, return the field, asked, and found per the requirements
    if verdict.refusal:
        return {
            "passed": False,
            "field": verdict.refusal.field,
            "asked": verdict.refusal.asked,
            "found": verdict.refusal.found
        }
        
    return {"passed": False, "field": "unknown", "asked": "valid", "found": "invalid"}

if __name__ == "__main__":
    # Serve the tools over stdio
    mcp.run()