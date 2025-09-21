# Component: FileWriterTool

-   **Name**: FileWriterTool
-   **Type**: TOOL
-   **Description**: Writes given text content to a specified file path.

### Inputs

-   `content_file_path` (string): The path to a file within the `workspace/` directory containing the content to be written.
-   `output_file_path` (string): The final destination path for the file (relative to the project root).

### Outputs

-   A new file created at `output_file_path` with the specified content.

### Logic

1.  Read the content from `content_file_path`.
2.  Write that exact content to a new file at `output_file_path`.
3.  This tool is for creating the final, user-facing output file.