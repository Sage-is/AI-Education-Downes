import os
import re
from datetime import datetime

def sanitize_for_filename(text: str) -> str:
    """Sanitizes a string to be used as a valid filename or directory name."""
    # Remove invalid characters
    text = re.sub(r'[\\/*?:"<>|]', "", text)
    # Replace spaces and multiple hyphens with a single hyphen
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-+', '-', text)
    # Truncate to a reasonable length
    return text.strip().lower()[:50]

class Vault:
    """
    Manages the creation and organization of artifacts in a structured folder hierarchy.
    All artifacts are saved as Markdown (.md) files for human readability.
    """
    def __init__(self, base_dir: str = "vault"):
        self.base_dir = base_dir
        self.run_dir = None

    def create_run_dir(self, initial_prompt: str):
        """Creates a new directory for a single agent run, timestamped."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prompt_slug = sanitize_for_filename(initial_prompt)
        self.run_dir = os.path.join(self.base_dir, f"{timestamp}_{prompt_slug}")
        os.makedirs(self.run_dir, exist_ok=True)
        return self.run_dir

    def save_artifact(self, task_name: str, artifact_name: str, content: any):
        """
        Saves an artifact to the vault within a task-specific subfolder.
        All artifacts are saved as Markdown (.md) files.
        """
        if not self.run_dir:
            print("Warning: Run directory not created. Call create_run_dir first.")
            # Create a default run directory if none exists
            self.create_run_dir("default_run")

        task_slug = sanitize_for_filename(task_name)
        task_dir = os.path.join(self.run_dir, task_slug)
        os.makedirs(task_dir, exist_ok=True)

        artifact_slug = sanitize_for_filename(artifact_name)
        
        # Everything is Markdown now!
        ext = ".md"
        
        # Convert content to Markdown string
        if isinstance(content, str):
            content_str = content
        else:
            # For non-string content, wrap in code block
            import json
            content_str = f"```json\n{json.dumps(content, indent=2)}\n```"

        # Find a unique filename
        i = 1
        while True:
            filename = f"{artifact_slug}_{i}{ext}"
            filepath = os.path.join(task_dir, filename)
            if not os.path.exists(filepath):
                break
            i += 1
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content_str)
        
        print(f"Artifact saved: {filepath}")
        return filepath
