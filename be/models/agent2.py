from langchain.prompts import ChatPromptTemplate, FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from ..contents import agent2_algorithm_explanation_prompt, agent2_algorithm_explanation_example
from . import llm

def agent2_algorithm_explanation_chain(human_input: str):
    example_prompt = PromptTemplate(
        input_variables=["question", "answer"],
        template="Question: {question}\nAnswer: {answer}"
    )

    few_shot_prompt = FewShotPromptTemplate(
        examples=[agent2_algorithm_explanation_example],
        example_prompt=example_prompt,
        prefix=agent2_algorithm_explanation_prompt,
        suffix="Human: {human_prompt}\nAssistant: ",
        input_variables=["human_prompt"]
    )

    chain = few_shot_prompt | llm

    response = chain.invoke({"human_prompt": human_input})

    return response
