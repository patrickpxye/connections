import os
import asyncio
from together import Together, AsyncTogether
import random

def unflatten_response(response):
    return "\n".join([", ".join(group) for group in response])

async def run_meta_inference(prompt, instructions, games, responses, model):

    async_client = AsyncTogether(api_key=os.environ.get("TOGETHER_API_KEY"))

    #assert that the number of games is equal to the number of responses
    assert len(games) == len(responses)

    prompts = [
        prompt.format(instructions=instructions, game=(", ".join(random.sample(games[i]["entries"], len(games[i]["entries"])))).upper(), response = unflatten_response(responses[i]), answer = unflatten_response(games[i]["solutions"]))
        for i in range(len(games))
    ]

    all_answers = []
    for message in prompts:

        response = await async_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
        )
        answer = []
        output = response.choices[0].message.content
        
        all_answers += [output]

    print(all_answers)
    return all_answers


async def run_agent_inference(prompt, instructions, games, responses, meta_instructions, model):

    async_client = AsyncTogether(api_key=os.environ.get("TOGETHER_API_KEY"))
    #prompt.format(instructions=instructions, game=(", ".join(random.sample(games[i]["entries"], len(games[i]["entries"])))).upper(), response=unflatten_response(responses[i]), meta_instructions = meta_instructions[i])
    prompts = [
        prompt.format(meta_instructions = meta_instructions[i])
        for i in range(len(games))
    ]

    all_answers = []
    for message in prompts:

        response = await async_client.chat.completions.create(
            model= model,
            messages=[{"role": "user", "content": message}],
        )
        answer = []
        output = response.choices[0].message.content
        groups = output.split("\n")

        for group in groups:
            split_group = group.split(", ")
            answer += [["".join([i for i in s if i.isalpha()]) for s in split_group]]
        all_answers += [answer]

    print(all_answers)
    return all_answers