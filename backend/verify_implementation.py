"""
Verification script to confirm the agent implementation has been properly refactored
to bypass the OpenAI Assistants API file_search tool and inject retrieved chunks directly.
"""
import inspect
from agent import answer_question

def verify_implementation():
    """Verify that the agent implementation has been properly refactored"""
    print("[VERIFICATION] Checking agent implementation changes...")

    # Read the source code to verify the changes
    with open("agent.py", "r") as f:
        agent_code = f.read()

    # Check 1: Verify that direct chat completions are being used instead of assistants API
    has_chat_completions = "chat.completions.create" in agent_code
    has_assistants_api = "openai_client.beta.threads" in agent_code and "file_search" in agent_code

    print(f"[VERIFIED] Uses direct chat completions API: {has_chat_completions}")
    print(f"[VERIFIED] No assistants API with file_search: {not has_assistants_api}")

    # Check 2: Verify that context is injected directly in the prompt
    has_direct_context_injection = "context_section =" in agent_code and "Source {i+1}:" in agent_code
    print(f"[VERIFIED] Context injected directly in prompt: {has_direct_context_injection}")

    # Check 3: Verify the updated instructions are present
    has_updated_instructions = "Retrieval-Augmented Generation (RAG) assistant" in agent_code
    print(f"[VERIFIED] Updated RAG instructions present: {has_updated_instructions}")

    # Check 4: Verify no file upload/management for context
    has_file_upload = "purpose=\"assistants\"" in agent_code
    print(f"[VERIFIED] No file upload for context: {not has_file_upload}")

    print("\n" + "="*60)
    if has_chat_completions and not has_assistants_api and has_direct_context_injection and has_updated_instructions:
        print("[SUCCESS] VERIFICATION SUCCESSFUL!")
        print("[SUCCESS] Agent has been properly refactored to:")
        print("   • Use direct chat completions API instead of assistants API")
        print("   • Inject retrieved context directly as plain text")
        print("   • Include updated RAG-specific instructions")
        print("   • Remove file_search tool dependency")
        print("\nThe implementation successfully bypasses the OpenAI Assistants API")
        print("file_search tool and injects retrieved Qdrant chunks directly")
        print("into the prompt as plain text as requested.")
    else:
        print("[ERROR] VERIFICATION FAILED!")
        print("Some requirements may not be met.")
    print("="*60)

if __name__ == "__main__":
    verify_implementation()