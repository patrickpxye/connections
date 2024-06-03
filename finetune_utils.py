from baseline import transform_test_data
import json
import random


# this function is used to output the right formate for each row in the dataset
def create_text_row(output, input):
    instruction = """Given 16 words, split them into 4 groups of 4 words, so each group is related by a certain theme or category.

    Follow the restrictions at the end of the instruction.
    
    Here are some hints.
    1. The 4 words can be items that belong in the same category.
    Example:
    Fish: BASS, SALMON, TROUT, FLOUNDER
    Body parts: HEAD, KNEES, SHOULDER, TOES

    2. The 4 words can each form a common phrase when paired with another word.
    Example:
    Fire __: ANT, DRILL, ISLAND, OPAL
    ___ Change: CHUMP, CLIMATE, LOOSE, SEA

    3. The 4 words can be associated with a certain verb phrase or action
    Example:
    Things to crack: EGG, KNUCKLES, SMILE, WINDOW
    Removes the covering of: PARES, PEELS, SHELLS, SHUCKS
    
    Follow these restrictions when outputing your answers.
    1. Respond in 4 lines, with a group of 4 words on each line. ONLY include the words given. Include each word ONLY ONCE.
    2. DO NOT include any word that is not in the 16 words given. DO NOT include preceding text like "Answers:" or line numbers like "1."
    3. Start by identifying the easiest group, which is usually four items that belong in the same category of objects.
    
    Make sure that your 4 groups of 4 words follow the following format EXACTLY. Otherwise, you will suffer penalty beyond imagination. 
    Only replace [REPLACE_THIS] with the words. Each word should only be used once. Each line is a group of 4 words related by a certain theme or category.
    
    Format:
    [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS]
    [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS]
    [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS]
    [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS]

    Double check that your response follows the above format. Make sure the [REPLACE_THIS] tokens are replaced with your words.
    Verify that you ONLY have 4 lines of 4 words and NOTHING else.
    """

    text_row = f"""<s>[INST] {instruction}

{input} [/INST]
{output} </s>"""
    return text_row


# input should be json.load('data.json')
def create_mistral_finetune_data(data, str):
    transformed_data = transform_test_data(data, False)
    result = []
    for puzzle in transformed_data:
        entries_string = ", ".join(random.sample(puzzle["entries"], 16))  # shuffle
        answer_string = "\n".join([", ".join(group) for group in puzzle["solutions"]])
        result.append(create_text_row(answer_string, entries_string))

    with open(f"data/splits/connections_{str}.jsonl", "w") as f:
        for text in result:
            f.write(json.dumps({"text": text}) + "\n")

    return result
