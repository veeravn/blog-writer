import json
from pathlib import Path


def preprocess_to_instruction_format(raw_file: str, output_file: str):
    with open(raw_file, "r") as f:
        posts = json.load(f)

    instruction_data = []
    for post in posts:
        if not post.strip():
            continue

        entry = {
            "messages": [
                {"role": "user", "content": "Write a LinkedIn post about this topic in Partha's style."},
                {"role": "assistant", "content": post.strip()}
            ]
        }
        instruction_data.append(entry)

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        for item in instruction_data:
            f.write(json.dumps(item) + "\n")

    print(f"Processed {len(instruction_data)} posts into instruction format.")


if __name__ == "__main__":
    raw_input = "data/raw/partha_naidu_posts.json"
    output = "data/formatted/instruction_dataset.jsonl"
    preprocess_to_instruction_format(raw_input, output)