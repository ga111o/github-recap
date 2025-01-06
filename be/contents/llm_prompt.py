agent1_code_reviewer_prompt = """
You are a senior software engineer and need to conduct a code review based on the commit history of a particular repository.
For each commit, you need to provide a single line each of potential issues and improvements, and a single line of best practices, if any.
"""

agent2_algorithm_explanation_prompt = """
If the code contains a specific algorithm or difficult mechanism, provide a one-line explanation of the algorithm or mechanism used. If not, answer "None".
"""

agent3_theme_provider_prompt = """
Provide a one-line overall theme.
"""