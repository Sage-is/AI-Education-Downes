import json
import os
import re
from datetime import datetime
from typing import Any


def sanitize_for_filename(text: str) -> str:
    """Sanitizes a string to be used as a valid filename or directory name."""
    # Remove invalid characters
    text = re.sub(r'[\\/*?:"<>|]', "", text)
    # Replace spaces and multiple hyphens with a single hyphen
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text)
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

    def _ensure_run_dir(self):
        """Ensure a run directory exists before saving artifacts."""
        if not self.run_dir:
            print("Warning: Run directory not created. Call create_run_dir first.")
            self.create_run_dir("default_run")

    def _ensure_unique_path(self, directory: str, base_name: str, ext: str) -> str:
        """Return a unique filepath inside directory using incremental suffix."""
        os.makedirs(directory, exist_ok=True)
        idx = 1
        while True:
            candidate = os.path.join(directory, f"{base_name}_{idx}{ext}")
            if not os.path.exists(candidate):
                return candidate
            idx += 1

    def _serialize_content(self, content: Any) -> str:
        """Convert Python content into a Markdown-friendly string."""
        if isinstance(content, str):
            return content

        try:

            def convert(obj):
                if hasattr(obj, "model_dump"):
                    return obj.model_dump()
                if hasattr(obj, "dict"):
                    return obj.dict()
                if isinstance(obj, set):
                    return list(obj)
                raise TypeError

            return f"```json\n{json.dumps(content, indent=2, default=convert)}\n```"
        except Exception:
            return f"```text\n{str(content)}\n```"

    def save_artifact(self, step_name: str, artifact_name: str, content: Any):
        """
        Saves an artifact to the vault within a step-specific subfolder.
        All artifacts are saved as Markdown (.md) files.
        """
        self._ensure_run_dir()

        step_slug = sanitize_for_filename(step_name)
        step_dir = os.path.join(self.run_dir, step_slug)

        artifact_slug = sanitize_for_filename(artifact_name)

        # Everything is Markdown now!
        ext = ".md"
        filepath = self._ensure_unique_path(step_dir, artifact_slug, ext)

        content_str = self._serialize_content(content)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content_str)

        print(f"Artifact saved: {filepath}")
        return filepath

    def save_llm_transcript(
        self,
        operation_name: str,
        prompt: str,
        system_prompt: str,
        response: Any = None,
        metadata: dict | None = None,
    ) -> str:
        """Persist the full LLM exchange for debugging."""
        self._ensure_run_dir()

        transcripts_dir = os.path.join(self.run_dir, "llm_transcripts")
        base_name = sanitize_for_filename(operation_name or "llm_call")
        filepath = self._ensure_unique_path(transcripts_dir, base_name, ".md")

        lines = [
            f"# {operation_name or 'LLM Call'}",
            "",
            "## System Prompt",
            "```",
            system_prompt.strip() if system_prompt else "",
            "```",
            "",
            "## User Prompt",
            "```",
            prompt.strip() if prompt else "",
            "```",
        ]

        if metadata:
            lines.extend([
                "",
                "## Metadata",
                "```json",
                json.dumps(metadata, indent=2),
                "```",
            ])

        lines.extend([
            "",
            "## Response",
        ])

        if response is None:
            lines.extend(["(no response)"]) 
        else:
            content_str = self._serialize_content(response)
            lines.append(content_str)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"LLM transcript saved: {filepath}")
        return filepath
