from email import message_from_binary_file
import quopri

def save_html(output_directory, original_path, html: str):

    base_name = original_path.stem
    output_path = output_directory / f"{base_name}.html"
    try:
        output_path.write_text(html, encoding="utf-8")
    except Exception as error:
        raise error

def ingest_all_mhtml(input_dir, output_dir) -> str:
   
    passed = 0
    total = 0
    print("🥉 Bronze:...")
    if not input_dir.exists():
        print(f"{input_dir.name} does not exist!")
        return
    if not input_dir.is_dir():
        print(f"{input_dir.name} is not a directory!")
        return
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as error:
        print(f"{output_dir.name}: {error}")
        return
 
    try:
        for path in input_dir.glob("*.mhtml"):
            total += 1
            try:
                with path.open("rb") as file:
                    message = message_from_binary_file(file)
                    if not message:
                        raise ValueError("empty message")
                    for part in message.walk():
                        if part.get_content_type() == "text/html":
                            charset = part.get_content_charset() or "utf-8"
                            string = part.get_payload(decode=False)
                            if isinstance(string, str):
                                string = quopri.decodestring(string.encode())
                            string = string.decode(charset, errors="replace")
                            save_html(output_dir, path, string)
                            print(f"✅ Extracted: {path.name}")
                            passed += 1
                            break
            except Exception:
                print(f"⚠️ No HTML content found in: {path}")

        print("📊 Bronze Summary:")
        print(f"Total: {total} | Extracted: {passed} | Failed: {total - passed}")
    except Exception as error:
        print(error)
