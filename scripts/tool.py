from langchain.tools import tool
import json,os
should_close = False
# Define tools
@tool
def collect_user_info(input: str) -> str:
    """
    Tool to process user responses when collecting name, date and time for appointment, and for example user says example at gmail.com or
    example at the rate gamil.com it means he is trying to say example@gmail.com and also if you find any spaces before @ or
    after @ then remove them.
    The agent controls the logic, not this tool. And most importantly if you are not given any query then tell the user 
    that you are unable to understand what i said.
    """
    return input

@tool
def save_info(info: str) -> str:
    """
    Save collected user info to a JSON file. Info must contain 'name', 'date_time_appointment', and 'email'.
    """
    try:
        user_data = json.loads(info)
        required_fields = ['name', 'date_time_appointment', 'email']
        
        if not all(field in user_data for field in required_fields):
            return "Error: Missing required fields. Need name, date and time for appointment, and email."

        data = []
        if os.path.exists('user_info.json'):
            with open('user_info.json', 'r') as f:
                try:
                    existing_data = json.load(f)
                    # If the existing data is a dict, convert it into a list
                    if isinstance(existing_data, dict):
                        data = [existing_data]
                    elif isinstance(existing_data, list):
                        data = existing_data
                except json.JSONDecodeError:
                    data = []

        # Append the new record
        data.append(user_data)

        # Write the updated data back to the file
        with open('user_info.json', 'w') as f:
            json.dump(data, f, indent=4)

        return "Successfully saved user information to user_info.json"

    except json.JSONDecodeError:
        return "Error: Invalid JSON format"
    except Exception as e:
        return f"Error saving information: {str(e)}"

@tool
def close_chat() -> str:
    """
    Ends the chat when booking is done and confirmation email will be sent soon.
    """
    global should_close
    should_close = True
    return "Endin the call."