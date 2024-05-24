import os
import asyncio
from together import Together, AsyncTogether
import random


async def run_inference(test_data, prompt, model):
    async_client = AsyncTogether(api_key=os.environ.get("TOGETHER_API_KEY"))

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
            model=model,
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
