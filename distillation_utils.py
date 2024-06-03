from baseline import transform_test_data
import json
import random
from api_utils import run_inference, run_inference_prompt


# this function is used to output the right formate for each row in the dataset
def create_text_row(output, input):
    instruction = """Given 16 words, split them into 4 groups of 4 words, so each group is related by a certain theme or category. Before you give the answers, explain why you made the grouping choices at the start of your response.

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
    
    Start by identifying the easiest group, which is usually four items that belong in the same category of objects.
    
Make sure that your reasoning and 4 groups of 4 words follow the following format EXACTLY. Otherwise, you will suffer penalty beyond imagination.
Only replace [EXPLAIN THIS] with a justification for your grouping choices.
Only replace [REPLACE_THIS] with the words. Each word should only be used once. Each line is a group of 4 words related by a certain theme or category.
    
Format:
    [EXPLAIN_THIS]

    So the answer is:

    Group 1: [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS]
    Group 2: [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS]
    Group 3: [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS]
    Group 4: [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS]

Double check that your response follows the above format. Make sure the [REPLACE_THIS] tokens are replaced with your words.

Here are the 16 words: """

    text_row = f"""<s>[INST] {instruction} {input} [/INST]
{output} </s>"""
    return text_row


async def get_mistral_distillation_data(data, str):
    train_data = transform_test_data(data, False)
    template = """You are a teacher teaching a student to play the following game.

    Given 16 words, split them into 4 groups of 4 words, so each group is related by a certain theme or category.

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

You have an example game with a answer key and teacher's guide, and your task is to explain to a student how to arrive at the solutions from the 16 words. Here is the example game: {Entries}

Answers:
{Answers}

Teacher's Guide:
{Descriptions}

Explain with clean and clear logic, refer to word-level details and explain how the groups of words are formed sequentially.
"""

    def formulate_prompt(template, entries, answers, descriptions):
        entryss = ", ".join(entries)
        answers_str = "\n".join([", ".join(answer) for answer in answers])
        # print(template.format(Entries=entryss, Answers=answers_str, Descriptions=descriptions))
        return template.format(
            Entries=entryss, Answers=answers_str, Descriptions=descriptions
        )

    def get_guide(answers, descriptions):
        return "\n".join(
            [
                f"{description}: {', '.join(answer)}"
                for answer, description in zip(answers, descriptions)
            ]
        )

    prompts = [
        formulate_prompt(
            template,
            item["entries"],
            item["solutions"],
            get_guide(item["solutions"], item["descriptions"]),
        )
        for item in train_data
    ]

    distillations = await run_inference_prompt(
        prompts, model="databricks/dbrx-instruct"
    )
    # save the predictions in new file
    with open(f"data/distillations_{str}.json", "w") as file:
        json.dump(distillations, file)


# input should be json.load('data.json')
def create_mistral_finetune_distillation_data(data, distillation_data, str):
    transformed_data = transform_test_data(data, False)

    result = []
    for puzzle, distillation in zip(transformed_data, distillation_data):
        entries_string = ", ".join(random.sample(puzzle["entries"], 16))  # shuffle
        answer_string = "\n".join([", ".join(group) for group in puzzle["solutions"]])
        output = f"{distillation}\n\nSo the answer is:\n\n{answer_string}"
        result.append(create_text_row(output, entries_string))

    with open(f"data/splits/connections_{str}.jsonl", "w") as f:
        for text in result:
            f.write(json.dumps({"text": text}) + "\n")

    return result
