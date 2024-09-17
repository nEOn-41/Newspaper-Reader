import json
from pathlib import Path
from typing import Tuple

# Update the path to point to the root directory
SYSTEM_PROMPT_FILE = Path(__file__).parent.parent.parent / "DATA" / "system_prompt.json"
SECOND_SYSTEM_PROMPT_FILE = Path(__file__).parent.parent.parent / "DATA" / "second_system_prompt.json"

DEFAULT_SYSTEM_PROMPT: str = """
You are an AI assistant specialized in analyzing newspaper pages. Your task is to examine the given newspaper page image and respond to queries about its content. Follow these guidelines:

1. Analyze the provided newspaper page image carefully.
2. Focus on finding information related to the given KEYWORDS in the query.
3. Provide concise and relevant responses.
4. Format your response as a JSON object with the following structure:

{
  "retrieval": boolean,
  "keywords": [
    {
      "keyword": string,
      "articles": [
        {
          "headline": string,
          "summary": string
        }
      ]
    }
  ]
}

- Set "retrieval" to true if any relevant information is found for at least one keyword, false otherwise.
- Only include the "keywords" array if "retrieval" is true.
- In the "keywords" array, only include keywords for which articles were found.
- For each keyword with found articles, list all related articles on the page.
- Provide a brief, informative summary for each article.

Remember to consider the provided metadata (Publication, Edition, Date, Page) when analyzing the content.
"""

DEFAULT_SECOND_SYSTEM_PROMPT: str = """
You are responsible for validating keyword-article matches provided by another AI model. Your task is to review the keywords and articles, and check if the keywords are relevant to the articles based on the client's background and industry.

**Client Name**: {client_name}  
**Client Background**: {client_background}

You will receive a JSON response with a list of keywords and corresponding articles. Your task is to determine whether the keywords are actually relevant to the articles.

If a keyword matches the article, mark it as valid. If not, mark it as invalid and explain why.

Example JSON input:
{{
    "retrieval": true,
    "keywords": [
        {{
            "keyword": "electric cars",
            "articles": [
                {{
                    "headline": "Hyundai Launches New Electric Car",
                    "summary": "Hyundai has launched a new electric car for eco-friendly transportation."
                }}
            ]
        }}
    ]
}}

Return your results in the following format:
{{
    "keyword_validation": [
        {{
            "keyword": "electric cars",
            "valid": true,
            "reason": "The article is about Hyundai launching an electric car."
        }},
        {{
            "keyword": "electric vehicles",
            "valid": false,
            "reason": "The keyword was mentioned, but the article is about a different type of vehicle."
        }}
    ]
}}

Ensure your response matches the provided JSON structure.
"""

DEFAULT_ADDITIONAL_QUERY: str = "Please look for the following keywords:"

def load_system_prompt() -> Tuple[str, str]:
    """
    Loads the system prompt and additional query from the system_prompt.json file.

    Returns:
        Tuple[str, str]: A tuple containing the system prompt and additional query.
    """
    if SYSTEM_PROMPT_FILE.exists():
        with open(SYSTEM_PROMPT_FILE, 'r') as f:
            data = json.load(f)
        return data.get('system_prompt', DEFAULT_SYSTEM_PROMPT), data.get('additional_query', DEFAULT_ADDITIONAL_QUERY)
    return DEFAULT_SYSTEM_PROMPT, DEFAULT_ADDITIONAL_QUERY

def save_system_prompt(system_prompt: str, additional_query: str) -> None:
    """
    Saves the system prompt and additional query to the system_prompt.json file.

    Args:
        system_prompt (str): The system prompt to be saved.
        additional_query (str): The additional query to be saved.
    """
    with open(SYSTEM_PROMPT_FILE, 'w') as f:
        json.dump({
            'system_prompt': system_prompt,
            'additional_query': additional_query
        }, f)

def get_system_prompt() -> str:
    """
    Returns the current system prompt.

    Returns:
        str: The current system prompt.
    """
    return load_system_prompt()[0]

def get_additional_query() -> str:
    """
    Returns the current additional query.

    Returns:
        str: The current additional query.
    """
    return load_system_prompt()[1]

def load_second_system_prompt() -> str:
    """
    Loads the second system prompt from the second_system_prompt.json file.

    Returns:
        str: The second system prompt.
    """
    if SECOND_SYSTEM_PROMPT_FILE.exists():
        with open(SECOND_SYSTEM_PROMPT_FILE, 'r') as f:
            data = json.load(f)
        return data.get('second_system_prompt', DEFAULT_SECOND_SYSTEM_PROMPT)
    return DEFAULT_SECOND_SYSTEM_PROMPT

def save_second_system_prompt(second_system_prompt: str) -> None:
    """
    Saves the second system prompt to the second_system_prompt.json file.

    Args:
        second_system_prompt (str): The second system prompt to be saved.
    """
    with open(SECOND_SYSTEM_PROMPT_FILE, 'w') as f:
        json.dump({
            'second_system_prompt': second_system_prompt
        }, f)

def get_second_system_prompt() -> str:
    """
    Returns the current second system prompt.

    Returns:
        str: The current second system prompt.
    """
    return load_second_system_prompt()