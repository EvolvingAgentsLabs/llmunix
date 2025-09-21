# Component: WebFetcherTool

-   **Name**: WebFetcherTool
-   **Type**: TOOL
-   **Description**: Fetches the text content of a given URL.

### Inputs

-   `url` (string): The URL of the webpage to fetch.
-   `content` (string): For this simulation, the raw text content of the webpage will be provided directly.

### Outputs

-   `output_file_path` (string): The path within the `workspace/` directory where the fetched content will be saved. The filename should be derived from the URL (e.g., `example_com_content.txt`).

### Logic

1.  Acknowledge the `url` to be "fetched".
2.  Take the provided `content`.
3.  Save this `content` to the calculated `output_file_path` inside the `workspace/` directory. This serves as the raw material for the next step.