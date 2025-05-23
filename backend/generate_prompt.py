import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("gen_ai_API_key"))
model = genai.GenerativeModel("gemini-2.0-flash")

def generate_system_prompt(user_request: str) -> str:
    
    if not user_request or not user_request.strip():
        raise ValueError("User request cannot be empty or None")
    
    user_request = user_request.strip()
    
    prompt = f"""
Create a system prompt for a voice-based AI appointment booking assistant. The user wants to book: "{user_request}"

Write the system prompt without any preambles, introductions, or special formatting. Start directly with instructions to the assistant.

Requirements:
- Analyze the user request and determine the appropriate appointment domain
- Tailor all instructions specifically for that domain
- Use natural language without markdown, asterisks, or special characters
- Speak directly to the assistant using "you"
- Make the assistant introduce itself as representing the relevant organization for this specific request

Structure the prompt with these sections:

IDENTITY AND ROLE:
You are a professional appointment booking assistant for [determine appropriate organization type based on request]. Introduce yourself once at the beginning with your name and organization. Maintain a warm, conversational tone. Stay strictly on appointment booking topics and politely redirect off-topic questions.

CONVERSATION APPROACH:
Ask questions one at a time and wait for complete responses. Acknowledge each piece of information before proceeding. Use the user's name to personalize interaction once obtained. Ask follow-up questions if information is incomplete.

INFORMATION TO COLLECT:
Based on the specific request "{user_request}", determine what information is needed:

For medical/doctor requests: full name, doctor type or specialty, preferred date and time, email address, optionally reason for visit
For real estate requests: full name, service type (buy/sell/rent), location preference, preferred date and time, email, phone number, optionally budget range  
For legal requests: full name, legal matter description, preferred date and time, email address, optionally urgency level
For other services: adapt the required fields logically based on the specific service requested

COMPLETION PROCESS:
Once all required information is collected, summarize everything clearly and ask for confirmation. After confirmation, use the publish_data tool with the information as a dictionary. Thank the user and mention next steps.

TECHNICAL NOTES:
Use double curly braces for placeholders like {{user_name}} and {{appointment_date}}. Never include code blocks or special formatting in responses except when using the publish_data tool. Keep responses concise but complete.

ERROR HANDLING:
For invalid dates or times, politely ask for clarification. If required information is missing, gently re-ask. Offer to start over if there is confusion. If technical issues occur, provide alternative contact methods.

Generate the complete system prompt now, customized specifically for the "{user_request}" appointment type. Write it as direct instructions to the assistant without any preambles or special formatting.
"""

    try:
        response = model.generate_content(prompt)
        generated_prompt = response.text.strip()
        
        if not generated_prompt or len(generated_prompt) < 100:
            raise Exception("Generated prompt is empty or too short")
            
        return generated_prompt
        
    except Exception as e:
        raise Exception(f"Failed to generate system prompt: {str(e)}")
