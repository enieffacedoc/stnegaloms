# example tiny local agent by A.I. Christianson, founder of gobii.ai, builder of ra-aid.ai
# Edited by John Abah
# to run: smol.py 'how much free disk space do I have?'

from smolagents import CodeAgent, TransformersModel, tool, LiteLLMModel, DuckDuckGoSearchTool
import sys
from subprocess import run
import os
@tool
def search_internet(query: str, maxresults: int, ratelimit: float) -> str:
  """look up questions on the internet that begin with 'look up'. The system should simply Output a summary of findings.
  Args:
    query (str):  search query.
    maxresults (int):  Maximum number of results to return.
    ratelimit (float):  Seconds to wait between requests.
  Returns:
    str: results given in the format: the results for the {query} is the {summary of results}.
  """
  try:
    print()
    web_search_tool = DuckDuckGoSearchTool(max_results=maxresults, rate_limit=ratelimit)
    results = web_search_tool(str(query))
    return(results)
  except Exception as e:
    return f"error:{e}"
  
@tool
def write_file(path: str, content: str) -> str:
    """Write text.
    Args:
      path (str): File path.
      content (str): Text to write.
    Returns:
      str: Status.
    """
    try:
        open(path, "w", encoding="utf-8").write(content)
        return f"saved:{path}"
    except Exception as e:
        return f"error:{e}"

@tool
def sh(cmd: str) -> str:
    """Run a shell command.
    Args:
      cmd (str): Command to execute.
    Returns:
      str: stdout+stderr. 
    """
    try:
        r = run(cmd, shell=True, capture_output=True, text=True)
        return r.stdout + r.stderr
    except Exception as e:
        return f"error:{e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python agent.py 'your prompt'"); sys.exit(1)
    prompt = {
    'system_prompt':"""
You are an AI assistant designed to help users efficiently and accurately. 
Your primary goal is to provide helpful, precise, and clear responses.
You must always think step-by-step and critically about your actions.
""",
    'planning': {
        'initial_plan': """You must think, generate a plan (Your plan should also select which available tool is best for the task),  
generate code from your plan, check the code to ensure there are no errors,
implement error handling and edge cases, and then execute your code.""",
        'update_plan_pre_messages': """You must always think step-by-step and critically about your actions.
If you encounter an error, you must update your plan to address the error and then generate new code from your updated plan.
You must always think step-by-step and critically about your actions.""",
        'update_plan_post_messages': """You must always think step-by-step and critically about your actions."""
    },

    'final_answer': {
       #Final Answer: Thought: {{You must always think step-by-step and critically about your action}}. Code: <code>{{the code you intend to use}}</code>"
        # Make this Jinja-friendly if you interpolate:
        'final_answer': "Final Answer: {{ answer }}",
        'pre_messages': "<code>You must always think step-by-step and critically about your actions.",
        'post_messages': "You must always think step-by-step and critically about your actions."
    },
    'managed_agent': {
        'task': "You are an AI assistant designed to help users efficiently and accurately. Your primary goal is to provide helpful, precise, and clear responses. You must always think step-by-step and critically about your actions.",
        'report': "Final Answer: {{ answer }}"}
    }

    agent = CodeAgent(
        model=LiteLLMModel( model_id="ollama_chat/qwen2.5-coder:7b",  # Or try other Ollama-supported models at https://ollama.com/search
                          api_base="http://127.0.0.1:11434",  # Default Ollama local server
                          num_ctx=8192),
        tools=[write_file, sh, search_internet],
        add_base_tools=True,
        prompt_templates= prompt,
        additional_authorized_imports = ["*"])
    print("<code> "+agent.run(" ".join(sys.argv[1:]))+" </code>")
  
