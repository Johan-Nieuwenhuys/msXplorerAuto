"""Stage 1, Step 1: collect project details and prepare configurable paths."""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path

LOGGER = logging.getLogger(__name__)
UAID_PATTERN = re.compile(r"HS2-0[A-Za-z0-9]{8}")
CHECKER_WORKBOOK = "DM3 Attribute Checker.xlsx"


@dataclass(frozen=True)
class UserDetails:
    """Values collected during the first workflow step."""

    full_name: str
    user_name: str
    user_email: str
    uaid_2: str
    asset_name: str
    docset_url: str


@dataclass(frozen=True)
class ProjectPaths:
    """Per-user paths, with environment overrides for nonstandard locations."""

    documents: Path
    template: Path
    assets: Path
    tracker: Path
    downloads: Path
    attribute_validation: Path
    bim_checker: Path

    @classmethod
    def for_user(cls, user_name: str, uaid_2: str) -> ProjectPaths:
        documents = Path(
            os.environ.get(
                "MSXPLORERAUTO_DOCUMENTS_DIR",
                str(Path("C:/Users") / user_name / "OneDrive - EKFB" / "Documents"),
            )
        )
        attribute_validation = Path(
            os.environ.get(
                "MSXPLORERAUTO_ATTRIBUTE_VALIDATION_DIR",
                "C:/data/Attribute Validation Checks",
            )
        )
        bim_checker = Path(
            os.environ.get(
                "MSXPLORERAUTO_BIM_CHECKER_DIR",
                "C:/data/BIMXTRA_FILES_FROM_METADATA_REP/ASC/local_HS2",
            )
        )
        assets = documents / "_Assets"
        return cls(
            documents=documents,
            template=documents / "_Template",
            assets=assets,
            tracker=documents / "_Tracker",
            downloads=assets / uaid_2 / f"{uaid_2} - Downloads",
            attribute_validation=attribute_validation,
            bim_checker=bim_checker,
        )


def normalize_user_name(full_name: str) -> str:
    """Return the brief's Title Case identity token with spaces removed."""
    normalized = "".join(part.title() for part in full_name.split())
    if not normalized:
        raise ValueError("A first and last name are required.")
    return normalized


def parse_asset_naming(asset_naming: str) -> tuple[str | None, str | None]:
    """Extract a 13-character UAID and the remaining asset name when present."""
    match = UAID_PATTERN.search(asset_naming)
    if not match:
        return None, None
    asset_name = (asset_naming[: match.start()] + asset_naming[match.end() :]).strip()
    return match.group(), asset_name or None


def collect_user_details(input_fn=input) -> UserDetails:
    """Prompt for Step 1 project values; credentials are intentionally deferred."""
    full_name = input_fn("Enter your first and last name and hit ENTER: ").strip()
    user_name = normalize_user_name(full_name)
    email_string = ".".join(full_name.casefold().split())
    user_email = f"{email_string}@ekfb.com"

    asset_naming = input_fn("Now enter the UAID_2 and Asset Name and hit ENTER: ").strip()
    uaid_2, asset_name = parse_asset_naming(asset_naming)
    if not uaid_2:
        uaid_2 = input_fn("Now enter the UAID_2 and hit ENTER: ").strip()
        if not UAID_PATTERN.fullmatch(uaid_2):
            raise ValueError("UAID_2 must be 13 characters and start with HS2-0.")
    if not asset_name:
        asset_name = input_fn("Now enter the Asset Name and hit ENTER: ").strip()
        if not asset_name:
            raise ValueError("An asset name is required.")

    docset_url = input_fn("Now enter the PW Docset URL and hit Enter: ").strip()
    if not docset_url:
        raise ValueError("A PW Docset URL is required.")
    return UserDetails(full_name, user_name, user_email, uaid_2, asset_name, docset_url)


def clear_attribute_validation_folder(folder: Path) -> list[Path]:
    """Remove files beneath the target while retaining the checker workbook."""
    if not folder.is_dir():
        raise FileNotFoundError(f"Attribute validation folder not found: {folder}")

    removed = []
    for path in folder.rglob("*"):
        if path.is_file() and path.name != CHECKER_WORKBOOK:
            path.unlink()
            removed.append(path)
    LOGGER.info("Removed %d file(s) from %s", len(removed), folder)
    return removed


def run_step_one() -> tuple[UserDetails, ProjectPaths]:
    """Run Step 1 interactively, confirming cleanup before deleting any files."""
    details = collect_user_details()
    paths = ProjectPaths.for_user(details.user_name, details.uaid_2)
    LOGGER.info("Resolved user documents directory: %s", paths.documents)
    if input(f"Clear files in {paths.attribute_validation}? [y/N]: ").strip().casefold() == "y":
        removed = clear_attribute_validation_folder(paths.attribute_validation)
        print(f"Removed {len(removed)} file(s); preserved {CHECKER_WORKBOOK}.")
    else:
        print("Folder cleanup skipped.")
    print(f"Downloads folder: {paths.downloads}")
    return details, paths


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        run_step_one()
    except (OSError, ValueError) as error:
        LOGGER.error("Step 1 failed: %s", error)
        raise SystemExit(1) from error