from pathlib import Path

import google.generativeai as genai


def generate_message_body(
    quote: str,
    saint: str,
    api_key: str,
    system_prompt_file: Path,
) -> str:
    # Reads the system prompt from file at call time so edits take effect without restarting
    system_prompt = system_prompt_file.read_text(encoding="utf-8").strip()

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_prompt,
    )

    user_message = (
        f'Citazione del giorno: "{quote}"\n'
        f"Santo del giorno: {saint}"
    )

    response = model.generate_content(user_message)
    return response.text.strip()
