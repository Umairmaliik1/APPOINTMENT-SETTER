from langchain.tools import tool
import json,os
global should_close
should_close = False
# Define tools
availability_file_path= "admin_availability.json"
@tool
def fetch_doc_details(doctor_name: str) -> str:
    """
    Returns only the 'details' field of a doctor from the JSON file.
    """
    try:
        with open(availability_file_path, "r") as f:
            doctors = json.load(f)

        for doc in doctors:
            if doc.get("name", "").lower() == doctor_name.lower():
                return json.dumps(doc.get("details", {}), indent=4)

        return f"No details found for doctor: {doctor_name}"

    except FileNotFoundError:
        return "Doctor data file not found."
    except json.JSONDecodeError:
        return "Doctor data file is not valid JSON."
    except Exception as e:
        return f"An error occurred: {str(e)}"

@tool
def extract_unique_doctor_names()->list:
    """
    Extract the unique doctor names from the JSON file.
    """
    
    if not os.path.exists(availability_file_path):
        return f"Error: File not found at {availability_file_path}"

    try:
        with open(availability_file_path, 'r') as f:
            data = json.load(f)

        # Flatten the list if the JSON is a list of records
        if not isinstance(data, list):
            data = [data]

        doctor_names = set()
        for entry in data:
            # Adjust the key depending on your JSON structure
            doctor_name = entry.get('doctor_name') or entry.get('doctor') or entry.get('name')
            if doctor_name:
                doctor_names.add(doctor_name)

        return list(doctor_names)

    except json.JSONDecodeError:
        return "Error: Failed to decode JSON file."
    except Exception as e:
        return f"Error: {str(e)}"

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