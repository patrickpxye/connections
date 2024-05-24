from baseline import transform_test_data
import json
import random


# this function is used to output the right formate for each row in the dataset
def create_text_row(output, input):
    instruction = """Given 16 items, find groups of four items that share something in common.

Category Examples
Fish: BASS, FLOUNDER, SALMON, TROUT
Fire ___: ANT, DRILL, ISLAND, OPAL
Categories will always be more specific than “5-letter-words,” “Names” or “Verbs.”
Each puzzle has exactly one solution. Watch out for words that seem to belong to multiple categories!

Now answer for these 16 words. Follow these restrictions for the output:
1. Respond in 4 lines, with a group of 4 words on each line. ONLY include the 16 words given. There should be NO OTHER WORDS.
2. DO NOT include the descriptions. DO NOT have any "Descriptions:" text.
3. DO NOT include any preceding text, like "Answers:", or line numbers, like "1."."""

    text_row = f"""<s>[INST] {instruction}

{input} [/INST]
{output} </s>"""
    return text_row


# input should be json.load('data.json')
def create_mistral_finetune_data(data):
    transformed_data = transform_test_data(data, False)
    result = []
    for puzzle in transformed_data:
        entries_string = ", ".join(random.sample(puzzle["entries"], 16))  # shuffle
        answer_string = "\n".join([", ".join(group) for group in puzzle["solutions"]])
        result.append(create_text_row(answer_string, entries_string))

    with open("data/splits/connections_train.jsonl", "w") as f:
        for text in result:
            f.write(json.dumps({"text": text}) + "\n")

    return result
