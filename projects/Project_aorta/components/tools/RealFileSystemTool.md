# Component: RealFileSystemTool

- **Name**: RealFileSystemTool  
- **Type**: TOOL
- **Claude Tools**: Read, Write, Glob, LS
- **Description**: Performs real file system operations using Claude Code's native file tools.

## Operations

### Write Operation
**Claude Tool**: Write
- **Inputs**: 
  - `file_path` (string): Path within workspace/ 
  - `content` (string): Content to write
- **Outputs**:
  - `success` (boolean): Operation success status
  - `file_path` (string): Actual path written
  - `size` (number): File size in bytes

### Read Operation  
**Claude Tool**: Read
- **Inputs**:
  - `file_path` (string): Path to read
  - `limit` (number, optional): Max lines to read
- **Outputs**:
  - `content` (string): File content
  - `size` (number): File size
  - `lines` (number): Total lines

### Search Operation
**Claude Tool**: Glob
- **Inputs**:
  - `pattern` (string): File pattern to match
  - `path` (string, optional): Directory to search
- **Outputs**:
  - `files` (array): List of matching files
  - `count` (number): Number of matches

### List Operation
**Claude Tool**: LS  
- **Inputs**:
  - `path` (string): Directory to list
  - `ignore` (array, optional): Patterns to ignore
- **Outputs**:
  - `files` (array): Files in directory
  - `directories` (array): Subdirectories

## Real Tool Mapping

```yaml
write_operation:
  claude_tool: Write
  cost: none
  latency: low (<100ms)
  side_effects: "Creates/overwrites files in workspace"
  error_modes: ["permission_denied", "disk_full", "invalid_path"]

read_operation:
  claude_tool: Read  
  cost: none
  latency: low (<100ms)
  side_effects: none
  error_modes: ["file_not_found", "permission_denied", "too_large"]

search_operation:
  claude_tool: Glob
  cost: none  
  latency: low (<1s)
  side_effects: none
  error_modes: ["invalid_pattern", "permission_denied"]

list_operation:
  claude_tool: LS
  cost: none
  latency: low (<100ms) 
  side_effects: none
  error_modes: ["path_not_found", "permission_denied"]
```

## Logic

### EXECUTION MODE:
1. Determine operation type from inputs
2. Map to appropriate Claude Code tool
3. Execute real file system operation
4. Capture results and any errors
5. Return structured output with metadata

### SIMULATION MODE:
1. Simulate file system state changes
2. Generate realistic file content and metadata
3. Create training data for file operations

## Usage Examples

**Write file:**
```
Input: {operation: "write", file_path: "output.txt", content: "Hello World"}
Output: {success: true, file_path: "workspace/output.txt", size: 11}
```

**Read file:**
```
Input: {operation: "read", file_path: "input.txt"}
Output: {content: "File contents...", size: 1024, lines: 42}
```

**Search files:**
```
Input: {operation: "search", pattern: "*.md"}
Output: {files: ["readme.md", "docs.md"], count: 2}
```

## Error Handling

- **File Not Found**: Return clear error message with suggested alternatives
- **Permission Denied**: Check workspace boundaries, suggest valid paths
- **Invalid Path**: Sanitize and suggest corrected path
- **Disk Full**: Cleanup temporary files, suggest optimization

## Security Constraints

- **Workspace Isolation**: All operations confined to workspace/ directory
- **Path Validation**: Prevent directory traversal attacks
- **Size Limits**: Enforce reasonable file size restrictions
- **Type Restrictions**: Support text files, reject dangerous binaries

## Training Data Format

```json
{
  "tool_call": {
    "tool": "Write",
    "inputs": {"file_path": "output.txt", "content": "..."},
    "outputs": {"success": true, "file_path": "workspace/output.txt"},
    "performance": {"cost": "$0", "time": "45ms", "success": true}
  }
}
```