from pathlib import Path
from typing import Generator


VALID_SUFFIXES = {".mhtml", ".mht"}

# How many bytes to inspect for MIME headers
HEADER_SNIFF_SIZE = 4096

"""
!TODO 
- [] File Validation
-   [] Directory existence
-   [/] Invalid file suffix (skips)
-   [/] Empty .mhtml
-   [/] Permmission error
-   [/] File not containing MIME header (lightweight checking)
"""
def find_mhtml_files(directory: str | Path) -> Generator[Path, None, None]:
    """
    Yield probable MHTML files from a directory.

    Validation steps:
    - file exists and is a regular file
    - extension matches .mhtml or .mht
    - file is not empty
    - file header vaguely resembles MIME/MHTML
    """

    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory}")

    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    for path in directory.glob("*"):

        # Skip non-files
        if not path.is_file():
            continue

        # Normalize suffix case
        if path.suffix.lower() not in VALID_SUFFIXES:
            continue

        try:
            # Read only a small chunk for header sniffing
            with path.open("rb") as file:
                header = file.read(HEADER_SNIFF_SIZE)
            
            # Skip empty files
            if path.stat().st_size == 0:
                print(f"[SKIP] Empty file: {path}")
                continue

        except PermissionError:
            print(f"[ERROR] Permission denied: {path}")
            continue

        except OSError as error:
            print(f"[ERROR] Failed to read {path}: {error}")
            continue

        # Lightweight MIME/MHTML validation
        header_lower = header.lower()

        looks_like_mhtml = (
            b"mime-version" in header_lower
            or b"content-type" in header_lower
            or b"multipart/" in header_lower
        )

        if not looks_like_mhtml:
            print(f"[SKIP] Not recognized as MHTML: {path}")
            continue

        yield path