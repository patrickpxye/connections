import os
import asyncio
from together import Together, AsyncTogether
import random


async def run_inference(test_data):
    async_client = AsyncTogether(api_key=os.environ.get("TOGETHER_API_KEY"))
    prompt = """Given 16 items, find groups of four items that share something in common.

Category Examples
Fish: BASS, FLOUNDER, SALMON, TROUT
Fire ___: ANT, DRILL, ISLAND, OPAL
Categories will always be more specific than “5-letter-words,” “Names” or “Verbs.”
Each puzzle has exactly one solution. Watch out for words that seem to belong to multiple categories!
The following are three examples of 16 words and their corresponding answers. You are also provided a brief description for what each group shares. Learn from these examples and respond with just the answers for the following puzzle. Respond in the same format as the examples: 4 lines, with a group on each line. Follow the restrictions given at the end of the prompt. The order within a group and between groups doesn't matter, but the groups in the example answers and descriptions are given in the order of easiest to trickiest to solve.

Examples:

Example 1. HYPE, HITCH, AMP, ACOUSTIC, GAS, CABLE, ELECTRIC, SONIC, LINK, FIRE, WATER, COUPLE, HEARD, PUMP, AUDITORY, TIE

Answers: 
CABLE, ELECTRIC, GAS, WATER
ACOUSTIC, AUDITORY, HEARD, SONIC
COUPLE, HITCH, LINK, TIE
AMP, FIRE, HYPE, PUMP

Descriptions:
Monthly bills
Related to sound/hearing
Connect
Excite, with “up”

Example 2. COMPLAINT, LAWSUIT, ACTION, HANGAR, FOXGLOVE, CLAIM, RUNWAY, WINDSOCK, TERMINAL, RING, GUMSHOE, CLUB, TURNCOAT, TARMAC, BEANBAG, TORCH

Answers:
HANGAR, RUNWAY, TARMAC, TERMINAL
ACTION, CLAIM, COMPLAINT, LAWSUIT
BEANBAG, CLUB, RING, TORCH
FOXGLOVE, GUMSHOE, TURNCOAT, WINDSOCK

Descriptions:
Parts of an airport
Legal terms
Things a juggler juggles
Words ending in clothing

Example 3. FESTER, SUNDAY, FRIDAY, ROT, LURCH, CAT, CHANCE, LIP, SPOIL, THING, THURSDAY, TURN, SATURDAY, WEDNESDAY, SOUR, TUESDAY

Answers:
FRIDAY, SATURDAY, SUNDAY, THURSDAY
ROT, SOUR, SPOIL, TURN
FESTER, LURCH, THING, WEDNESDAY
CAT, CHANCE, LIP, TUESDAY

Descriptions:
Days of the week
Go bad
The Addams Family characters
Fat ___

Now answer for these 16 words. Follow these restrictions for the output:

1. DO NOT include the descriptions. DO NOT have any "Descriptions:" text.
2. ONLY include the 16 words given. There should be NO OTHER WORDS.
3. DO NOT include any preceding text, like "Answers:", or line numbers, like "1."."""

    prompts = [
        prompt
        + "\n"
        + (
            ", ".join(
                random.sample(
                    test_data[i]["entries"], len(test_data[i]["entries"])
                )  # shuffle
            )
        ).upper()
        for i in range(len(test_data))
    ]
    # tasks = [
    #     async_client.chat.completions.create(
    #         model="databricks/dbrx-instruct",
    #         messages=[{"role": "user", "content": message}],
    #     )
    #     for message in prompts
    # ]

    all_answers = []
    for message in prompts:

        response = await async_client.chat.completions.create(
            model="databricks/dbrx-instruct",
            messages=[{"role": "user", "content": message}],
        )
        answer = []
        output = response.choices[0].message.content
        # if any(str.isdigit(i) for i in response.choices[0].message.content):
        #     print("restarting, digit")
        #     print(output)
        #     continue
        groups = output.split("\n")

        for group in groups:
            split_group = group.split(", ")
            answer += [["".join([i for i in s if i.isalpha()]) for s in split_group]]
        all_answers += [answer]

    print(all_answers)
    return all_answers
