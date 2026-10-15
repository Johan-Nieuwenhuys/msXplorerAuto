import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from msxplorer_auto import (
    CHECKER_WORKBOOK,
    ProjectPaths,
    clear_attribute_validation_folder,
    collect_user_details,
    normalize_user_name,
    parse_asset_naming,
)


class StepOneTests(unittest.TestCase):
    def test_identity_and_asset_name_are_derived(self):
        self.assertEqual(normalize_user_name("johan Nieuwenhuys"), "JohanNieuwenhuys")
        self.assertEqual(
            parse_asset_naming("  HS2-012345678 Asset Name  "),
            ("HS2-012345678", "Asset Name"),
        )

    def test_paths_follow_user_and_allow_documents_override(self):
        with patch.dict(os.environ, {}, clear=True):
            paths = ProjectPaths.for_user("JohanNieuwenhuys", "HS2-012345678")
            self.assertEqual(
                paths.documents,
                Path("C:/Users/JohanNieuwenhuys/OneDrive - EKFB/Documents"),
            )
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"MSXPLORERAUTO_DOCUMENTS_DIR": directory}):
                paths = ProjectPaths.for_user("ColleagueName", "HS2-012345678")
                self.assertEqual(
                    paths.downloads,
                    Path(directory) / "_Assets" / "HS2-012345678" / "HS2-012345678 - Downloads",
                )

    def test_collects_details_and_email(self):
        answers = iter((
            "johan Nieuwenhuys",
            "HS2-012345678 Asset Name",
            "https://example.invalid/docset",
        ))
        details = collect_user_details(lambda _prompt: next(answers))
        self.assertEqual(details.user_email, "johan.nieuwenhuys@ekfb.com")
        self.assertEqual(details.uaid_2, "HS2-012345678")
        self.assertEqual(details.asset_name, "Asset Name")

    def test_cleanup_preserves_checker_and_removes_other_files(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            checker = folder / CHECKER_WORKBOOK
            other = folder / "old.xlsx"
            nested = folder / "archive" / "old.csv"
            checker.touch()
            other.touch()
            nested.parent.mkdir()
            nested.touch()

            removed = clear_attribute_validation_folder(folder)

            self.assertEqual({path.name for path in removed}, {"old.xlsx", "old.csv"})
            self.assertTrue(checker.exists())
            self.assertFalse(other.exists())
            self.assertFalse(nested.exists())


if __name__ == "__main__":
    unittest.main()