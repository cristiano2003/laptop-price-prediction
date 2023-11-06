import openai
import os
import sys
sys.path.append(os.path.join(os.getcwd()))  # NOQA


def chat_completion(api_key: str, content: str) -> dict:
    """
    Returns:
    ```python
        {
            'status': 'success' or 'error',
            'message': 'str'
        }
    ```

    """

    openai.api_key = api_key

    try:
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            temperature=0.7,
            messages=[
                {
                    'role': 'user',
                    'content': content
                }
            ]
        )

        return {
            'status': 'success',
            'message': response['choices'][0]['message']['content'].strip()
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
        }
