import argparse
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from functions.call_function import available_functions, call_function


def main():
    parser = argparse.ArgumentParser(description="AI Code Assistant")
    parser.add_argument("user_prompt", type=str, help="Prompt to send to Gemini")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable not set")

    client = genai.Client(api_key=api_key)
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
    if args.verbose:
        print(f"User prompt: {args.user_prompt}\n")
    generate_content(client, messages, args.verbose)



def generate_content(client, messages, verbose):
    for _ in range(20):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0,
                tools=[available_functions])
        )
        for i in response.candidates:
            messages.append(i.content)
        if not response.usage_metadata:
            raise RuntimeError("Gemini API response appears to be malformed")

        if verbose:
            print("Prompt tokens:", response.usage_metadata.prompt_token_count)
            print("Response tokens:", response.usage_metadata.candidates_token_count)

        function_calls = response.function_calls
        if not function_calls:
            print("Response:")
            print(response.text)
            return
        function_results = []
        for function_call in function_calls:
            function_call_result = call_function(function_call, verbose=verbose)
            parts = function_call_result.parts
            if not parts:
                raise Exception("Function call returned no parts")
            part = parts[0]
            function_response = part.function_response
            if function_response is None:
                raise Exception("Not function response object")
            response_payload = function_response.response
            if response_payload is None:
                raise Exception("No response")
            function_results.append(part)
            if verbose:
                print(f"-> {response_payload}")
        messages.append(types.Content(role="user", parts=function_results))
    print("Agent hit max iterations without producing a final response.")
    sys.exit(1)





if __name__ == "__main__":
    main()