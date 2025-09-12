## Personal Notes & Knowledge Base

This repository contains the source code and content for my personal notes website, hosted as a GitHub Pages site. It's designed to be a living collection of my thoughts, learnings, and project documentation.

### How It Works

This site is built using **MkDocs** with the excellent **Material for MkDocs** theme. The process is fully automated using a custom Python script and a GitHub Actions workflow.

The core idea is to allow notes to live alongside the projects or topics they relate to. Each subdirectory can contain a `README.md` file, which is then automatically discovered and integrated into the final website.

### Key Components

1.  **Content (`**/README.md`)**: All content is written in Markdown. Any `README.md` file within any directory (that isn't ignored) will be treated as a page on the site.

2.  **MkDocs Configuration (`docs-site/mkdocs.yml`)**: This file configures the site's name, theme, navigation, and Markdown extensions.

3.  **Preparation Script (`prepare_docs.py`)**: This Python script is the heart of the automation. It runs before the MkDocs build and performs the following steps:
    *   Scans the entire repository for `README.md` files.
    *   Copies them into a temporary `docs_src/` directory, preserving the original folder structure.
    *   Renames each `README.md` to `index.md` within its respective subdirectory in `docs_src/` to create clean URLs.
    *   Copies over any non-Markdown files (like images) to be used as assets.
    *   Intelligently fixes relative links within the Markdown files to ensure they work correctly in the final built site.

4.  **GitHub Actions Workflow (`.github/workflows/mkdocs-deploy.yml`)**: This workflow automates the entire deployment process. On every push to the `main` branch, it:
    *   Checks out the repository.
    *   Sets up a Python environment and installs the necessary dependencies (MkDocs, plugins, etc.).
    *   Runs the `prepare_docs.py` script to gather all content.
    *   Executes the `mkdocs build` command, which converts the Markdown in `docs_src/` into a static HTML website.
    *   Commits the generated static site files (HTML, CSS, JS) to the root of the repository.
    *   Pushes the commit, which triggers GitHub Pages to serve the new version of the site.

### Local Development

To run the site locally for development:

1.  **Install dependencies**: `pip install mkdocs-material mkdocs-awesome-pages-plugin pymdown-extensions`
2.  **Prepare the docs**: `python prepare_docs.py`
3.  **Serve the site**: `mkdocs serve --config-file docs-site/mkdocs.yml --docs-dir docs_src`

The site will be available at `http://127.0.0.1:8000`.
