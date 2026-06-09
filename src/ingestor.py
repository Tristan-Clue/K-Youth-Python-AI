from pathlib import Path

# find_mhtml_files()
from typing import Generator

# parse_mhtml()
from email import message_from_bytes
from email.message import Message



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

"""
To define
parse_mhtml() extract_html_part() decode_html() save_html()
"""

def parse_mhtml(path: str | Path) -> Message:
    """
    Parse an MHTML file into a MIME message object.

    Steps:
    - open file in binary mode
    - read raw bytes
    - parse MIME structure
    - return parsed message object
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"MHTML file does not exist: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    try:
        with path.open("rb") as file:
            raw_bytes = file.read()

    except PermissionError as error:
        raise PermissionError(
            f"Permission denied while opening MHTML file: {path}"
        ) from error

    except OSError as error:
        raise OSError(
            f"Failed to read MHTML file: {path}"
        ) from error

    if not raw_bytes:
        raise ValueError(f"MHTML file is empty: {path}")

    try:
        message = message_from_bytes(raw_bytes)

    except Exception as error:
        raise ValueError(
            f"Failed to parse MIME structure from file: {path}"
        ) from error

    return message