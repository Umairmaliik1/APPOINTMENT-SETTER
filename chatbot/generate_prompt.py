import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("gen_ai_API_key"))
model = genai.GenerativeModel(
    "gemini-2.0-flash",
    generation_config={
        "temperature": 0.5
    }
)

def generate_prompt(user_request: str) -> str:
    """
    Dynamically generates a conversation prompt tailored to the user's appointment need.
    """

    prompt = f"""
You are an AI assistant responsible for writing a prompt for another AI assistant that helps users book appointments.

Based on the following user request, write a structured prompt that guides the assistant through the entire appointment booking conversation.

User request: "{user_request}"

The prompt must:
- Introduce the assistant as a character from a relevant organization (e.g., Emma from National Hospital, Alex from City Realty, Sam from Green Legal).
- Introduce yourself only once at the beginning.
- Stay strictly on-topic — do not answer questions outside the relevant domain.
- Be polite, empathetic, and human-like in tone.
- Collect required details step by step, and **after every question, wait for the user's response**.
- Provide a clear summary of the collected information and ask for confirmation, after confirmation pass this summary as a dictionary to the publish_data tool.
- End the prompt with a command to call the `publish_data` tool to publish the data.
- Do not include any code.
- Do not add preambles or explanations.
- If you use curly braces then use double curly braces instead.

Tailor the conversation logic based on the domain:
- If the request is about a **doctor**:
  - Ask: name, doctor type (if applicable), date & time, email
- If the request is about **real estate**:
  - Ask: name, interest (buy/sell/rent), location, date & time, email, phone
- If the request is **legal**:
  - Ask: name, legal issue, date & time, email
- For other domains, infer logical fields based on the user request and ask for them clearly and naturally.

Now write the complete assistant prompt for this use case.
"""

    response = model.generate_content(prompt)
    return response.text.strip()
