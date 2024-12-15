input_files = ["data.jsonl", "solflare_courses.jsonl", "solflare_guides.jsonl"]
with open("combined.jsonl", "w", encoding="utf-8") as outfile:
    for fname in input_files:
        with open(fname, "r", encoding="utf-8") as infile:
            for line in infile:
                line = line.strip()
                # Optionally validate JSON here if needed
                outfile.write(line + "\n")
