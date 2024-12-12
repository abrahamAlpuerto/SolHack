import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://academy.solflare.com/course/"
GUIDES_URL = BASE_URL + "/course/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def get_guide_links():
    guide_links = []
    next_page_url = GUIDES_URL

    while next_page_url:
        print(f"Fetching guide list from: {next_page_url}")
        resp = requests.get(next_page_url,headers=headers)
        if resp.status_code != 200:
            print(f"Error fetching {next_page_url}: Status code {resp.status_code}")
            break

        soup = BeautifulSoup(resp.text, 'html.parser')
        # Select all guide card links
        cards = soup.select('a.c-guideCard__link')
        if not cards:
            print("No guide links found on this page.")
        else:
            for card in cards:
                href = card.get('href')
                if href and href.startswith("/course/"):
                    full_link = BASE_URL + href
                    guide_links.append(full_link)

        # Check for next page link
        next_page_el = soup.select_one('.navigation.posts-navigation .nav-previous a')
        if next_page_el and next_page_el.get('href'):
            next_page_url = BASE_URL + next_page_el.get('href')
        else:
            next_page_url = None

    return guide_links

def scrape_guide(url):
    """Scrape a single guide page for headings and paragraphs."""
    print(f"Scraping guide: {url}")
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Error fetching guide {url}")
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')

    article = soup.select_one('article.c-postSingle .c-richText')
    if not article:
        # Try fallback: entire article
        article = soup.select_one('article.c-postSingle')
    if not article:
        print("No article content found.")
        return []

    # Title as context
    title_el = soup.select_one('article.c-postSingle h1')
    title_text = title_el.get_text(strip=True) if title_el else "Solflare Course"
    instruction_context = f"Talk about this relating to the wallet Solflare: {title_text}"

    # Extract sections by headings
    headings = article.find_all(['h2', 'h3'])
    data_pairs = []

    if not headings:
        # No sub-headings, just treat all paragraphs as one output
        all_text = ' '.join(p.get_text(strip=True) for p in article.find_all('p'))
        if all_text:
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
    guide_links = get_guide_links()
    print(f"Found {len(guide_links)} course links.")
    all_data_pairs = []

    for link in guide_links:
        pairs = scrape_guide(link)
        all_data_pairs.extend(pairs)

    # Write to JSONL
    with open("solflare_courses.jsonl", "w", encoding="utf-8") as f:
        for dp in all_data_pairs:
            f.write(json.dumps(dp, ensure_ascii=False) + "\n")

    print(f"Extracted {len(all_data_pairs)} pairs into solflare_courses.jsonl")

if __name__ == "__main__":
    main()
