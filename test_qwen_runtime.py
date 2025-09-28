#!/usr/bin/env python3
"""
Test script for the Qwen Runtime
This validates the core functionality without requiring an API key
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_manifest_loading():
    """Test that the manifest file loads correctly"""
    print("Testing manifest loading...")

    if not os.path.exists("QWEN.md"):
        print("❌ QWEN.md not found")
        return False

    with open("QWEN.md", "r") as f:
        content = f.read()

    # Check for required sections
    if "### NATIVE TOOLS" not in content:
        print("❌ NATIVE TOOLS section not found in manifest")
        return False

    # Check for essential tools
    required_tools = ["read_file", "write_file", "list_files", "execute_bash"]
    for tool in required_tools:
        if f'<tool name="{tool}">' not in content:
            print(f"❌ Required tool '{tool}' not found in manifest")
            return False

    print("✅ Manifest structure validated")
    return True

def test_tool_extraction():
    """Test that tools can be extracted from the manifest"""
    print("\nTesting tool extraction...")

    import re

    with open("QWEN.md", "r") as f:
        content = f.read()

    parts = content.split("### NATIVE TOOLS")
    if len(parts) < 2:
        print("❌ Could not split manifest at NATIVE TOOLS marker")
        return False

    tool_blocks = re.findall(r'<tool name="(.*?)">(.*?)</tool>', parts[1], re.DOTALL)

    if not tool_blocks:
        print("❌ No tools found in manifest")
        return False

    print(f"✅ Found {len(tool_blocks)} tools:")
    for name, _ in tool_blocks:
        print(f"   - {name}")

    return True

def test_tool_compilation():
    """Test that tool Python code can be compiled"""
    print("\nTesting tool compilation...")

    import re

    with open("QWEN.md", "r") as f:
        content = f.read()

    parts = content.split("### NATIVE TOOLS")
    tool_blocks = re.findall(r'<tool name="(.*?)">(.*?)</tool>', parts[1], re.DOTALL)

    compiled_count = 0
    failed_tools = []

    for name, block in tool_blocks:
        code_match = re.search(r'<python_code>(.*?)</python_code>', block, re.DOTALL)
        if not code_match:
            print(f"⚠️  No python_code found for tool '{name}'")
            continue

        code = code_match.group(1).strip()

        # Skip special tools
        if name in ["call_llm"]:
            print(f"   - {name}: Skipped (special handler)")
            continue

        try:
            namespace = {}
            exec(code, globals(), namespace)

            # Check if function was created
            func_found = False
            for key, value in namespace.items():
                if callable(value) and not key.startswith('_'):
                    func_found = True
                    break

            if func_found:
                print(f"   - {name}: ✅ Compiled successfully")
                compiled_count += 1
            else:
                print(f"   - {name}: ⚠️  No callable function found")
                failed_tools.append(name)

        except Exception as e:
            print(f"   - {name}: ❌ Compilation failed: {e}")
            failed_tools.append(name)

    print(f"\n✅ Successfully compiled {compiled_count} tools")
    if failed_tools:
        print(f"⚠️  Failed tools: {', '.join(failed_tools)}")

    return compiled_count > 0

def test_runtime_initialization():
    """Test that the runtime can be initialized (without API key)"""
    print("\nTesting runtime initialization...")

    # Create a mock .env file temporarily
    temp_env = ".env.test"
    with open(temp_env, "w") as f:
        f.write("OPENROUTER_API_KEY=test-key-not-real\n")

    try:
        # Set environment variable temporarily
        os.environ["OPENROUTER_API_KEY"] = "test-key-not-real"

        # Try to import and initialize
        from qwen_runtime import QwenRuntime

        runtime = QwenRuntime()

        # Check that tools were loaded
        if not runtime.tools:
            print("❌ No tools loaded in runtime")
            return False

        print(f"✅ Runtime initialized with {len(runtime.tools)} tools")

        # Test individual tool execution (local only, no API calls)
        print("\nTesting local tool execution...")

        # Test list_files
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runtime.tools["list_files"](tmpdir)
            print(f"   - list_files: {'✅' if isinstance(result, list) else '❌'}")

        # Test write_file and read_file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
            test_content = "Hello, Qwen Runtime!"
            tmp_path = tmp.name

        write_result = runtime.tools["write_file"](tmp_path, test_content)
        print(f"   - write_file: {'✅' if 'Successfully' in write_result else '❌'}")

        read_result = runtime.tools["read_file"](tmp_path)
        print(f"   - read_file: {'✅' if read_result == test_content else '❌'}")

        # Clean up
        os.unlink(tmp_path)

        return True

    except ImportError as e:
        print(f"❌ Could not import runtime: {e}")
        return False
    except Exception as e:
        print(f"❌ Runtime initialization failed: {e}")
        return False
    finally:
        # Clean up test env file
        if os.path.exists(temp_env):
            os.remove(temp_env)

def test_workspace_structure():
    """Test workspace directory structure"""
    print("\nTesting workspace structure...")

    workspace_dir = Path("workspace")

    if not workspace_dir.exists():
        print("Creating workspace directory...")
        workspace_dir.mkdir(exist_ok=True)

    # Create expected subdirectories
    state_dir = workspace_dir / "state"
    state_dir.mkdir(exist_ok=True)

    # Check structure
    if workspace_dir.exists() and state_dir.exists():
        print("✅ Workspace structure ready")
        print(f"   - workspace/")
        print(f"   - workspace/state/")
        return True
    else:
        print("❌ Could not create workspace structure")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("         Qwen Runtime Test Suite")
    print("="*60)

    tests = [
        ("Manifest Loading", test_manifest_loading),
        ("Tool Extraction", test_tool_extraction),
        ("Tool Compilation", test_tool_compilation),
        ("Runtime Initialization", test_runtime_initialization),
        ("Workspace Structure", test_workspace_structure),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*60)
    print("                    TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")

    print("-"*60)
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! The Qwen Runtime is ready to use.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your OpenRouter API key")
        print("3. Run: python qwen_runtime.py")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()