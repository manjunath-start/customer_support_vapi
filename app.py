from flask import Flask, request
import requests
import time
from config import VAPI_API_KEY, VAPI_BASE_URL, API_URL
import re

app = Flask(__name__)

@app.route('/get_interactions', methods=['POST'])
def get_interactions():
    user_input = request.json.get('user_input')

    if not user_input:
        return "Please provide a valid input."

    try:
        delay_message = "Please wait for a moment; I'm checking your information."
        print(delay_message)
        time.sleep(2)  

     
        user_id_match = re.search(r'\d+', user_input)  
        if not user_id_match:
            return "Could not extract a valid user ID from the input."

        user_id = int(user_id_match.group(0))  

       
        response = requests.get(API_URL)
        if response.status_code != 200:
            return "There was an issue fetching your information. Please try again later."

        data = response.json()
        interactions = [obj for obj in data if obj["User ID"] == user_id]

        if not interactions:
            return f"No interactions found for User ID: {user_id}."

        
        sorted_interactions = sorted(interactions, key=lambda x: x["Timestamp (UTC)"], reverse=True)

        most_recent = sorted_interactions[0]
        recent_message = f"The most recent interaction was on {most_recent['Timestamp (UTC)']}: {most_recent['Message Body']}."

        
        all_messages = "\n".join([f"{msg['Timestamp (UTC)']}: {msg['Message Body']}" for msg in sorted_interactions])

        response_message = (
            f"{recent_message}\n"
            "Would you like to hear more interactions?\n\n"
            f"Here are all the messages:\n{all_messages}"
        )

       
        vapi_response = requests.post(
            VAPI_BASE_URL,
            json={"input": response_message},
            headers={"Authorization": f"Bearer {VAPI_API_KEY}"}
        )

        if vapi_response.status_code != 200:
            return "An error occurred while communicating with Vapi."

        
        return vapi_response.json()

    except requests.exceptions.RequestException as e:
        return f"An error occurred while fetching data: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

if __name__ == '__main__':
    app.run(port=5000)