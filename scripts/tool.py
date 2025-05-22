from langchain.tools import tool
from datetime import datetime
import json,os
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
credentials_path = os.path.join(base_dir, "..", "..", "cred.json")
credentials_path = os.path.abspath(credentials_path)
print(credentials_path)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
from google.cloud import pubsub_v1
from google.cloud import pubsub_v1

global should_close
should_close = False

# Define tools
@tool
def publish_data(name: str, email: str, doc_category: str, datetime: str) -> str:
    """This tool is used to publish data to a Google Pub/Sub topic."""
    project_id = "appointment-setter-by-me"
    topic_id = "appointment_setter"
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    # Message payload (can be just a summary or ID)
    data_str = f"{name} is booking an appointment for {doc_category} on {datetime}"
    data = data_str.encode("utf-8")

    # Message attributes
    attributes = {
        "name": name,
        "email": email,
        "doc_category": doc_category,
        "datetime": datetime,
    }

    future = publisher.publish(topic_path, data, **attributes)
    return f"Data Published. Message ID: {future.result(timeout=10)}"
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
            if doctor_name.lower() in doc.get("name", "").lower():
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

        doctors = set()
        for entry in data:
            # Adjust the key depending on your JSON structure
            doctor_name =  entry.get('name')
            doctor_desc = entry.get('description')
            if doctor_name:
                doctors.add((doctor_name, doctor_desc))


        return list(doctors)

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
    Save collected user info to a JSON file. Info must contain 'name','doctor_name' 'date_time_appointment', and 'email'.
    """
    try:
        user_data = json.loads(info)
        required_fields = ['name','doctor_name','date_time_appointment', 'email']
        
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

@tool
def current_date_time() -> str:
    """
    Returns the current date and time.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def check_appointment(info: str) -> str:
    """
    Check If the Appointment booked or not. Ensure the input is a valid JSON string with an 'email' field.
    """
    try:
        payload = json.loads(info)
        email = payload.get("email")

        if not os.path.exists('user_info.json'):
            return "No appointment records found."

        with open('user_info.json', 'r') as f:
            data = json.load(f)

        for entry in data:
            if entry.get('email') == email:
                return f"Appointment found for email: {email}. Details: {json.dumps(entry, indent=4)}"   

        return f"No appointment found for email: {email}"

    except json.JSONDecodeError:
        return "Error: Invalid JSON format"
    except Exception as e:
        return f"Error updating information: {str(e)}"
    
@tool
def update_time(info: str) -> str:
    """
    Update the time of the appointment. Ensure the input is a valid JSON string with 'email' and 'new_time' fields.
    """
    try:
        payload = json.loads(info)
        email = payload.get("email")
        new_time = payload.get("new_time")

        if not os.path.exists('user_info.json'):
            return "No appointment records found."

        with open('user_info.json', 'r') as f:
            data = json.load(f)

        for entry in data:
            if entry.get('email') == email:
                doctor_name = entry.get('doctor_name')
                with open(availability_file_path, "r") as f:
                    doctors = json.load(f)
                for doc in doctors:
                    if doctor_name.lower() in doc.get("name", "").lower():
                        date1 = doc.get("availableDates_start")
                        date2 = doc.get("availableDates_end")
                        if date1 <= new_time <= date2:
                            entry['date_time_appointment'] = new_time
                            break
                        else:
                            return f"New time {new_time} is not within the doctor's availability window."
                        

        with open('user_info.json', 'w') as f:
            json.dump(data, f, indent=4)

        return f"Appointment time updated to {new_time} for email: {email}"

    except json.JSONDecodeError:
        return "Error: Invalid JSON format"
    except Exception as e:
        return f"Error updating information: {str(e)}"
    
