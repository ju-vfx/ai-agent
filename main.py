import argparse
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import sys

from prompts import system_prompt
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.run_python_file import schema_run_python_file, run_python_file
from functions.write_file import schema_write_file, write_file

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if api_key == None:
    raise RuntimeError("GEMINI_API_KEY not found in environment variables.")

parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

available_functions = types.Tool(
    function_declarations=[schema_get_files_info, schema_get_file_content, schema_run_python_file, schema_write_file],
)

def call_function(function_call, verbose=False):
    if verbose:
        print(f"Calling function: {function_call.name}({function_call.args})")
    else:
        print(f" - Calling function: {function_call.name}")

    function_map = {
        "get_file_content": get_file_content,
        "get_files_info": get_files_info,
        "run_python_file": run_python_file,
        "write_file": write_file,
    }

    function_name = function_call.name or ""

    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ]
        )
    
    args = dict(function_call.args) if function_call.args else {}
    args["working_directory"] = "./calculator"

    function_result = function_map[function_name](**args)

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )

def main():
    client = genai.Client(api_key=api_key)
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
    prompt_tokens = 0
    reponse_tokens = 0
    for _ in range(20):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages,
            config=types.GenerateContentConfig(system_instruction=system_prompt, tools=[available_functions]),
        )
        if response.usage_metadata == None:
            raise RuntimeError("Could not get response from Gemini API.")
        
        if response.candidates:
            for candidate in response.candidates:
                messages.append(candidate.content)

        prompt_tokens += response.usage_metadata.prompt_token_count
        reponse_tokens += response.usage_metadata.candidates_token_count


        if response.function_calls:
            function_results = []
            for function_call in response.function_calls:
                #print(f"Calling function: {function_call.name}({function_call.args})")
                function_call_result = call_function(function_call)
                if len(function_call_result.parts) < 1:
                    raise Exception("Function call result has no parts.")
                if function_call_result.parts[0].function_response == None:
                    raise Exception("Function call result has no function response.")
                if function_call_result.parts[0].function_response.response == None:
                    raise Exception("Function call result has no function response data.")
                function_results.append(function_call_result.parts[0])
                if args.verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")  
            messages.append(types.Content(role="user", parts=function_results))
        else:
            break

    else:
        print("Warning: Reached maximum number of iterations with no result.")
        sys.exit(1)
        

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Response tokens: {reponse_tokens}")
        print("\n")
    
    print(response.text)

if __name__ == "__main__":
    main()
