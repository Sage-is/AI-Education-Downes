import os
import tempfile
import unittest

from downes.utils.vault import Vault, sanitize_for_filename


class TestVaultNaming(unittest.TestCase):
    def test_first_artifact_uses_step_folder_name(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Vault(base_dir=tmpdir)
            vault.create_run_dir("Test Query")

            step_name = "04 Draft a 3-module syllabus on AI agents"
            step_slug = sanitize_for_filename(step_name)

            first_path = vault.save_artifact(
                step_name=step_name,
                artifact_name="06_llm_response",
                content="first",
            )
            self.assertEqual(os.path.basename(first_path), f"{step_slug}.md")

            second_path = vault.save_artifact(
                step_name=step_name,
                artifact_name="06_llm_response",
                content="second",
            )
            self.assertEqual(os.path.basename(second_path), "06_llm_response_1.md")


if __name__ == "__main__":
    unittest.main()
