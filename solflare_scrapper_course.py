import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://academy.solflare.com"
COURSE_URL = BASE_URL + "/course/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def get_course_links():
    """Scrape the main courses page and return all course links."""
    resp = requests.get(COURSE_URL, headers=headers)
    if resp.status_code != 200:
        print(f"Error fetching {COURSE_URL}, status: {resp.status_code}")
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')
    # Select all links that contain '/course/' in their href beyond the base page
    # The example shows: <a href="https://academy.solflare.com/course/crypto-fundamentals/blockchain-foundations/">
    # We'll filter out the main COURSE_URL itself.
    links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        # Ensure it's a full URL starting with BASE_URL
        if href.startswith("https://academy.solflare.com/course/") and href != COURSE_URL:
            links.append(href)

    # Remove duplicates if any
    links = list(set(links))
    return links

def scrape_course_page(url):
    """Scrape a single course page and extract instruction-output pairs."""
    print(f"Scraping course page: {url}")
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Error fetching course {url}")
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')

    # Try to identify the main article or content area
    # From the snippet, looks like content might be directly under article or .c-richText-like div
    # If structure differs, adjust the selector accordingly.
    content_area = soup.select_one('article.c-postSingle .c-richText')
    if not content_area:
        content_area = soup.select_one('article.c-postSingle')
    if not content_area:
        # If still not found, just take the main article or entire page
        content_area = soup

    # Title of the course section
    title_el = soup.select_one('article.c-postSingle h1')
    if not title_el:
        # If no h1 found, try h2, or fallback to a generic title
        title_el = soup.select_one('h1') or soup.select_one('h2')
    title_text = title_el.get_text(strip=True) if title_el else "Solflare Course Section"

    instruction_context = f"Talk about this relating to the wallet Solflare: {title_text}"

    # Extract headings and the paragraphs below them
    # If headings are h2, h3 as shown in your snippet
    headings = content_area.find_all(['h2', 'h3'])
    data_pairs = []

    if not headings:
        # No sub-headings, treat all paragraphs as one Q&A
        all_text = ' '.join(p.get_text(strip=True) for p in content_area.find_all('p'))
        if all_text.strip():
            data_pairs.append({
                "instruction": instruction_context,
                "input": "General Instructions",
                "output": all_text.strip()
            })
    else:
        for heading in headings:
            section_title = heading.get_text(strip=True)
            answer_parts = []
            for sibling in heading.next_siblings:
                if sibling.name in ['h2', 'h3']:
                    break
                if sibling.name == 'p':
                    answer_parts.append(sibling.get_text(strip=True))
            answer = " ".join(answer_parts).strip()
            if section_title and answer:
                data_pairs.append({
                    "instruction": instruction_context,
                    "input": section_title,
                    "output": answer
                })

    return data_pairs

def main():
    course_links = get_course_links()
    print(f"Found {len(course_links)} course links.")
    all_data_pairs = []

    for link in course_links:
        pairs = scrape_course_page(link)
        all_data_pairs.extend(pairs)

    # Write to JSONL
    with open("solflare_courses.jsonl", "w", encoding="utf-8") as f:
        for dp in all_data_pairs:
            f.write(json.dumps(dp, ensure_ascii=False) + "\n")

    print(f"Extracted {len(all_data_pairs)} pairs into solflare_courses.jsonl")

if __name__ == "__main__":
    main()
