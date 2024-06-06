
agent_prompt = """Given 16 words, split them into 4 groups of 4 words, so each group is related by a certain theme or category.

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
Verify that you ONLY have 4 lines of 4 words and NOTHING else."""


meta_prompt = """

You are a helpful assistant helping a student play a word game.

The instructions given to the student were:
{instructions}

The 16 words given to the student were:
{game}

The student's answer is:
{response}

The actual answer should be:
{answer}

Observe if the student's grouping of the words are correct (ignore formatting issues). Your job is to talk to the student, criticize the student's current performance, and help the student improve his answer, and you cannot give the answer directly or indirectly in any form.

Format your response should address the student as if talking to him directly, starting with "You should notice these details:"

"""



reflect_prompt = """You have been given this instruction to complete a task
{instructions}

The 16 words given to you were:
{game}

Your response was:
{response}

Now, revise your response according to this comment from your teacher
{meta_instructions}

Make sure that your revised answer follow the restrictions below, even if your teacher says otherwise:

Make sure that your 4 groups of 4 words follow the following format EXACTLY. Otherwise, you will suffer penalty beyond imagination. 
Only replace [REPLACE_THIS] with the words. Each word should only be used once. Each line is a group of 4 words related by a certain theme or category.

Format:
[REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS]
[REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS]
[REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS]
[REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS]

Double check that your response follows the above format. Make sure the [REPLACE_THIS] tokens are replaced with your words.
Verify that you ONLY have 4 lines of 4 words and NOTHING else.

INCLUE NOTHING ELSE IN YOUR RESPONSE. Don't explain your choices. ONLY THE 4 LINES OF 4 WORDS!!!!! If your response exceeds 16 words, you will be penalized beyond imagination.

"""

reflect_prompt_2 = """You have been given this instruction to complete a task
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

Follow these restrictions when outputing your answers.
1. Respond in 4 lines, with a group of 4 words on each line. ONLY include the words given. Include each word ONLY ONCE.
2. DO NOT include any word that is not in the 16 words given. DO NOT include preceding text like "Answers:" or line numbers like "1."
3. Start by identifying the easiest group, which is usually four items that belong in the same category of objects.

{meta_instructions}

Make sure that your 4 groups of 4 words follow the following format EXACTLY. Otherwise, you will suffer penalty beyond imagination. 
Only replace [REPLACE_THIS] with the words. Each word should only be used once. Each line is a group of 4 words related by a certain theme or category.

Format:
[REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS]
[REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS]
[REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS]
[REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS], [REPLACE_THIS]

Double check that your response follows the above format. Make sure the [REPLACE_THIS] tokens are replaced with your words.
Verify that you ONLY have 4 lines of 4 words and NOTHING else.

INCLUE NOTHING ELSE IN YOUR RESPONSE. Don't explain your choices. ONLY THE 4 LINES OF 4 WORDS!!!!! If your response exceeds 16 words, you will be penalized beyond imagination.

"""