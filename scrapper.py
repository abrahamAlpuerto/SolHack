import json
import requests
from bs4 import BeautifulSoup

urls = ["https://academy.solflare.com/guides/my-swap-failed/"
        ]

all_data_pairs = []

for url in urls:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract textual content
    main_content = soup.find('main')
    if not main_content:
        continue  # If main_content is not found, skip this URL

    headings = main_content.find_all(['h2', 'h3','h4'])
    data_pairs = []
    for i, heading in enumerate(headings):
        instruction = heading.get_text().strip()
        answer_parts = []
        # Loop through siblings until next heading
        for sibling in heading.next_siblings:
            if sibling.name in ['h2', 'h3','h4']:
                break
            if sibling.name == 'p':
                answer_parts.append(sibling.get_text().strip())
        answer = " ".join(answer_parts)
        if instruction and answer:
            data_pairs.append({"instruction": "Talk about this relating to the wallet Solflare: ", "input": instruction, "output": answer})

    all_data_pairs.extend(data_pairs)
# print(all_data_pairs)

# Write all_data_pairs to a .jsonl file
with open("test.jsonl", "w", encoding="utf-8") as f:
    for dp in all_data_pairs:
        f.write(json.dumps(dp, ensure_ascii=False) + "\n")
