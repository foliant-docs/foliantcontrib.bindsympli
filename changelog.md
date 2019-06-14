# 1.0.13

-    Set 2-minutes timeout instead of default 30-seconds when launching Chromium.
-    Use `page.waitForSelector()` instead of `page.waitForNavigation()`.
-    Use custom `sleep()` function for intentional delays.

# 1.0.12

-   Capture the output of the Puppeter-based script and write it to STDOUT.

# 1.0.11

-   Disable images downloading from design pages only, but not from login page.

# 1.0.10

-   Check if the design page exists and the image URL is valid.

# 1.0.9

-   Move the `while` loop from JavaScript code to Python code.
-   Add the `max_attempts` config option.
-   Require Foliant 1.0.8 because of using the `utils.output()` method.

# 1.0.8

-   Do not rewrite source Markdown file if an error occurs.

# 1.0.7

-   Use 60-seconds timeout instead of 30-seconds. Provide multiple attempts to open pages.

# 1.0.6

-   Do not disable images downloading. Use delays when filling email and password fields. Wait for idle network connections when loading pages.

# 1.0.5

-   Add logging.

# 1.0.4

-   Describe the preprocessor usage in `README.md`.

# 1.0.3

-   Eliminate external Perl scripts, rewrite the preprocessor code in Python.

# 1.0.2

-   Change the path for non-Python scripts once more.

# 1.0.1

-   Change the path for non-Python scripts.
