from baseline import transform_test_data
import json
import random
from api_utils import run_inference, run_inference_prompt


# this function is used to output the right formate for each row in the dataset
def create_text_row(output, input):
    instruction = f"""
# CONTEXT #
You are playing a linguistic game that requires chain-of-thought reasoning and has only one correct answer.
Given 16 words, split 16 words into 4 groups of 4 words, so each group is related by a certain theme or category. 

Provide your reasoning for the groupings along with your answers.

Each of the 16 words is in EXACTLY ONE of 4 groups. Each group has EXACTLY 4 words. Think through this step by step. You should start by identifying the easiest group, which is usually four items that belong in the same category of objects.

Here are some hints.
    1. A reason 4 words are in a group can be that they are items that belong in the same category.
    Example:
    Fish: BASS, SALMON, TROUT, FLOUNDER
    Body parts: HEAD, KNEES, SHOULDER, TOES

    2. A reason 4 words are in a group can be that they each form a common phrase when paired with another word.
    Example:
    Fire __: ANT, DRILL, ISLAND, OPAL
    ___ Change: CHUMP, CLIMATE, LOOSE, SEA

    3. A reason 4 words are in a group can be that they are associated with a certain verb phrase or action.
    Example:
    Things to crack: EGG, KNUCKLES, SMILE, WINDOW
    Removes the covering of: PARES, PEELS, SHELLS, SHUCKS

#########

# OBJECTIVE #

Provide your reasoning and the correct 4 groups of 4 words for these 16 words: {input}

#########

# RESPONSE FORMAT #
        
You answer should follow the following format exactly. Otherwise you will suffer consequences beyond imagination.

Respond with chain-of-thought reasoning for your grouping choices followed by "So the answer is:" and a JSON object with a single key "answer" that has a list of 4 lists, each of which has 4 words. Make sure each of the 16 words appears in EXACTLY one group and each group has EXACTLY 4 words. 

DO NOT include anything after this JSON object.

#########

# EXAMPLE #
Given the 16 words: SHALLOW, MAKE UP, COO, SURFACE, IMPROV, SIDE, AD-LIB, BABBLE, COSMETIC, CRAWL, DOMINO, FREESTYLE, PLACEBO, NURSE, BUTTERFLY, EXTERNAL 

The correct response would be: 

[REASONING_HERE]

So the answer is:

{{"answer": [["AD-LIB","FREESTYLE","IMPROV","MAKE UP"],["BABBLE","COO","CRAWL","NURSE"],["COSMETIC","EXTERNAL","SHALLOW","SURFACE"],["BUTTERFLY","DOMINO","PLACEBO","SIDE"]]}}"""
    text_row = f"""<s>[INST] {instruction} [/INST]
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
        answer_obj = {"answer": puzzle["solutions"]}
        output = f"{distillation}\n\nSo the answer is:\n\n{json.dumps(answer_obj)}"
        # output = f"{distillation}\n\nSo the answer is:\n\n{answer_string}"
        result.append(create_text_row(output, entries_string))

    with open(f"data/splits/connections_{str}.jsonl", "w") as f:
        for text in result:
            f.write(json.dumps({"text": text}) + "\n")

    return result
