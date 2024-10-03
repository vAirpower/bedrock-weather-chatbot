import json
import urllib3

def lambda_handler(event, context):
    try:
        # Extract necessary details from the event
        session_attributes = event.get('sessionAttributes', {})
        parameters = event.get('parameters', [])

        city = None
        latitude = session_attributes.get('latitude', None)
        longitude = session_attributes.get('longitude', None)

        for param in parameters:
            if param['name'] == 'city':
                city = param['value']

        if not city or not latitude or not longitude:
            response_body = {
                'TEXT': {
                    'body': "Missing required parameters: city, latitude, or longitude."
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
                'sessionAttributes': session_attributes,
                'promptSessionAttributes': event.get('promptSessionAttributes', {})
            }

        # NOAA Weather API call to get the weather data
        api_url = f'https://api.weather.gov/points/{latitude},{longitude}'
        http = urllib3.PoolManager()
        response = http.request('GET', api_url)
        data = json.loads(response.data.decode('utf-8'))

        # Extract the forecast URL
        forecast_url = data['properties']['forecast']
        forecast_response = http.request('GET', forecast_url)
        forecast_data = json.loads(forecast_response.data.decode('utf-8'))

        forecast_summary = forecast_data['properties']['periods'][0]['detailedForecast']

        response_body = {
            'TEXT': {
                'body': f"The weather in {city} (Lat: {latitude}, Lon: {longitude}) is: {forecast_summary}"
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
            'sessionAttributes': session_attributes,
            'promptSessionAttributes': event.get('promptSessionAttributes', {})
        }