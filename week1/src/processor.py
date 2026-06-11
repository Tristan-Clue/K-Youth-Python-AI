from bs4 import BeautifulSoup
from pydantic import BaseModel

class JobListing(BaseModel):
    source_id: str
    job_title: str
    company: str
    description: str

def get_soup_text(html, detail):
    attr = html.find(attrs={"data-automation": detail})
    if (attr):
        return attr.get_text(separator=" ", strip=True)
    return None

def save_json(output_directory, original_path, toJSON):

    output_path = output_directory / (original_path.stem + ".json")
    try:
        output_path.write_text(toJSON.model_dump_json(indent=2), encoding="utf-8")
    except Exception as error:
        raise error

def process_all_html(input_dir, output_dir): # processor.py
        
    count = 0
    passed = 0
    
    print("🥈 Silver:...")
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
    
    for path in input_dir.glob("*.html"):
        try:
            count += 1
            with open(path, "r", encoding="utf-8", ) as file:
                html = BeautifulSoup(file, 'html.parser')
                
                id = html.find("meta", property={"og:url"})["content"].rstrip("/").split("/")[-1]
                job_title = get_soup_text(html, "job-detail-title")
                if not job_title:
                    print(f"⚠️ Missing job_title in: {path.name}")
                    continue
                company = get_soup_text(html, "advertiser-name")
                if not company:
                    print(f"⚠️ Missing company in: {path.name}")
                    continue
                description = get_soup_text(html, "jobAdDetails")
                if not description:
                    print(f"⚠️ Missing description in: {path.name}")
                    continue
            jl = JobListing(source_id=id, job_title=job_title, company=company, description=description)
            save_json(output_dir, path, jl)
            print(f"✅ Extracted: {path.name}")
            passed += 1
        except Exception as error:
                print(error)
    print("📊 Silver Summary:")
    print(f"Total: {count} | Extracted: {passed} | Failed: {count - passed}")