from langchain.prompts import ChatPromptTemplate, FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from ..contents import agent1_code_reviewer_prompt, agent1_code_reviewer_example
from . import llm

def agent1_code_review_chain(human_input: str):
    example_prompt = PromptTemplate(
        input_variables=["question", "answer"],
        template="Question: {question}\nAnswer: {answer}"
    )

    few_shot_prompt = FewShotPromptTemplate(
        examples=[agent1_code_reviewer_example],
        example_prompt=example_prompt,
        prefix=agent1_code_reviewer_prompt,
        suffix="Human: {human_prompt}\nAssistant: ",
        input_variables=["human_prompt"]
    )

    chain = few_shot_prompt | llm

    response = chain.invoke({"human_prompt": human_input})

    return response