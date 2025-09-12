import os
import re
import shutil
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent.resolve()
SOURCE_REPO_PATH = SCRIPT_DIR
DOCS_SOURCE_PATH = SCRIPT_DIR / 'docs_src' # The source for MkDocs markdown files
IGNORED_DIRS = {'.git', 'docs-site', 'venv', '__pycache__'}  # Directories to ignore

print("--- MkDocs Preparation Script ---")
print(f"Starting documentation build from: {SOURCE_REPO_PATH}")
print(f"Outputting to: {DOCS_OUTPUT_PATH}")

# Ensure the docs output directory exists and is clean
if DOCS_SOURCE_PATH.exists():
    # Be careful with this! It deletes the existing docs folder.
    # We only remove sub-items, not the main index.md or the folder itself.
    for path in DOCS_SOURCE_PATH.iterdir():
        if path.name != 'index.md': # Keep the root index.md if it exists
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
else:
    DOCS_SOURCE_PATH.mkdir(parents=True, exist_ok=True)

# Find all README.md files and copy them
copied_markdown_files = []

for root_str, dirs, files in os.walk(SOURCE_REPO_PATH, topdown=True):
    root = Path(root_str)
    # Exclude ignored directories
    dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

    for file in files:
        source_path = root / file
        relative_path_from_repo = source_path.parent.relative_to(SOURCE_REPO_PATH)

        if file.lower() == 'readme.md':
            # Determine destination directory
            if relative_path_from_repo == '.':
                # This is the root README.md
                dest_path = DOCS_SOURCE_PATH / 'index.md'
            else:
                dest_dir = DOCS_SOURCE_PATH / relative_path_from_repo
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_path = dest_dir / 'index.md'

            print(f"Copying '{source_path}' to '{dest_path}'")
            shutil.copyfile(source_path, dest_path)
            copied_markdown_files.append((dest_path, relative_path_from_repo))
        elif not file.lower().endswith('.md'):
            # This is a potential asset file (image, etc.)
            dest_dir = DOCS_SOURCE_PATH / relative_path_from_repo
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = dest_dir / file
            print(f"Copying asset '{source_path}' to '{dest_path}'")
            shutil.copyfile(source_path, dest_path)

print("\n--- Fixing relative links in Markdown files ---")

# Regex to find markdown image/links like ![...](path) or [...]...(path)
link_regex = re.compile(r'(\[.*?\]\()([^\s\)]+)(.*?\))')

for md_file_path, original_relative_dir in copied_markdown_files:
    content = md_file_path.read_text(encoding='utf-8')

    def replace_link(match):
        prefix, link_target, suffix = match.groups()
        if "://" in link_target or link_target.startswith('/'):
            return match.group(0) # Absolute URL, ignore

        # Split link into path and anchor
        link_parts = link_target.split('#')
        link_path = link_parts[0]
        link_anchor = f"#{link_parts[1]}" if len(link_parts) > 1 else ""

        # Ignore pure anchor links to the same page
        if not link_path:
            return match.group(0)

        # Check if the link is already correct relative to the new file location
        if (md_file_path.parent / link_path).exists():
            # Link is already valid, no change needed.
            return match.group(0)

        try:
            # Resolve the absolute path of the link target from its original location
            absolute_link_path = (SOURCE_REPO_PATH / original_relative_dir).joinpath(link_path).resolve(strict=True)
        except FileNotFoundError:
            # The linked file doesn't exist, so we can't fix it. Leave it as is.
            print(f"  In '{md_file_path.name}', could not find linked file: '{link_target}'")
            return match.group(0)

        # Calculate the new relative path from the markdown file's new location
        new_relative_link = Path(os.path.relpath(absolute_link_path, md_file_path.parent))
        print(f"  In '{md_file_path.name}', rewriting '{link_target}' -> '{new_relative_link}{link_anchor}'")
        return f"{prefix}{new_relative_link}{link_anchor}{suffix}"

    new_content = link_regex.sub(replace_link, content)
    md_file_path.write_text(new_content, encoding='utf-8')

print("\nDocumentation build finished.")
