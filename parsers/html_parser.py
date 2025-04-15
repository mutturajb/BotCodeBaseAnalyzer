from bs4 import BeautifulSoup

def parse_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    tags = [tag.name for tag in soup.find_all()]
    return {
        "Classes": [],
        "Functions": [],
        "Variables": list(set(tags))
    }
