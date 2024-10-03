import json
import urllib3

def lambda_handler(event, context):
    try:
        # Extract necessary details from the event
        parameters = event.get('parameters', [])
        
        # Extract the city parameter from the event parameters
        city = None
        for param in parameters:
            if param['name'] == 'city':
                city = param['value']
                break
        
        if not city:
            response_body = {
                'TEXT': {
                    'body': "The 'city' parameter is missing. Please provide a valid city name."
                }
            }
            
            function_response = {
                'actionGroup': event['actionGroup'],
                'function': event['function'],
                'functionResponse': {
                    'responseState': 'REPROMPT',
                    'responseBody': response_body
                }
            }
            
            return {
                'messageVersion': '1.0',
                'response': function_response,
                'sessionAttributes': event.get('sessionAttributes', {}),
                'promptSessionAttributes': event.get('promptSessionAttributes', {})
            }

        # Use OpenStreetMap Nominatim API to convert city name to latitude and longitude
        geocode_url = f'https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1'
        http = urllib3.PoolManager()
        geocode_response = http.request('GET', geocode_url)
        geocode_data = json.loads(geocode_response.data.decode('utf-8'))

        if not geocode_data:
            response_body = {
                'TEXT': {
                    'body': f"Could not find location data for the city: {city}."
                }
            }
            
            function_response = {
                'actionGroup': event['actionGroup'],
                'function': event['function'],
                'functionResponse': {
                    'responseState': 'FAILURE',
                    'responseBody': response_body
                }
            }
            
            return {
                'messageVersion': '1.0',
                'response': function_response,
                'sessionAttributes': event.get('sessionAttributes', {}),
                'promptSessionAttributes': event.get('promptSessionAttributes', {})
            }

        latitude = geocode_data[0]['lat']
        longitude = geocode_data[0]['lon']

        # Store the latitude and longitude in session attributes
        session_attributes = event.get('sessionAttributes', {})
        session_attributes['latitude'] = latitude
        session_attributes['longitude'] = longitude

        response_body = {
            'TEXT': {
                'body': f"Retrieved coordinates: Latitude {latitude}, Longitude {longitude} for {city}."
            }
        }
        
        function_response = {
            'actionGroup': event['actionGroup'],
            'function': event['function'],
            'functionResponse': {
                'responseState': 'REPROMPT',  # Still using REPROMPT since Bedrock expects this.
                'responseBody': response_body
            }
        }
        
        return {
            'messageVersion': '1.0',
            'response': function_response,
            'sessionAttributes': session_attributes,
            'promptSessionAttributes': event.get('promptSessionAttributes', {})
        }

    except Exception as e:
        response_body = {
            'TEXT': {
                'body': f"An error occurred: {str(e)}"
            }
        }
        
        function_response = {
            'actionGroup': event['actionGroup'],
            'function': event['function'],
            'functionResponse': {
                'responseState': 'FAILURE',
                'responseBody': response_body
            }
        }
        
        return {
            'messageVersion': '1.0',
            'response': function_response,
            'sessionAttributes': event.get('sessionAttributes', {}),
            'promptSessionAttributes': event.get('promptSessionAttributes', {})
        }