from langchain.prompts import ChatPromptTemplate, FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from ..contents import agent3_theme_provider_prompt, agent3_theme_provider_example
from . import llm

def agent3_theme_provider_chain(human_input: str):
    example_prompt = PromptTemplate(
        input_variables=["question", "answer"],
        template="Question: {question}\nAnswer: {answer}"
    )

    few_shot_prompt = FewShotPromptTemplate(
        examples=[agent3_theme_provider_example],
        example_prompt=example_prompt,
        prefix=agent3_theme_provider_prompt,
        suffix="Human: {human_prompt}\nAssistant: ",
        input_variables=["human_prompt"]
    )

    chain = few_shot_prompt | llm

    response = chain.invoke({"human_prompt": human_input})

    return response
