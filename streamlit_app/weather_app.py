import streamlit as st
import folium  # For generating maps
from streamlit_folium import st_folium  # To display maps in Streamlit
from geopy.geocoders import Nominatim  # For geocoding (converting city to lat/lon)
import boto3  # For AWS Bedrock connection
import json  # For handling JSON responses
import uuid  # For generating unique session IDs
from streamlit_chat import message  # For chatbot messages

# Set up Bedrock client for LLM
def get_bedrock_client():
    if "aws_credentials" not in st.secrets:
        raise ValueError("AWS credentials not found in Streamlit secrets")
    
    session = boto3.Session(
        aws_access_key_id=st.secrets.aws_credentials.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=st.secrets.aws_credentials.AWS_SECRET_ACCESS_KEY,
        region_name=st.secrets.aws_credentials.AWS_DEFAULT_REGION
    )
    bedrock_client = session.client('bedrock-runtime')
    return bedrock_client

# Set up Bedrock client for Agent
def get_bedrock_agent_client():
    if "aws_credentials" not in st.secrets:
        raise ValueError("AWS credentials not found in Streamlit secrets")
    
    session = boto3.Session(
        aws_access_key_id=st.secrets.aws_credentials.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=st.secrets.aws_credentials.AWS_SECRET_ACCESS_KEY,
        region_name=st.secrets.aws_credentials.AWS_DEFAULT_REGION
    )
    bedrock_agent_client = session.client('bedrock-agent-runtime')
    return bedrock_agent_client

# Function to invoke Bedrock Agent (for weather data)
def invoke_bedrock_agent(agent_id, input_text, bedrock_agent_client):
    try:
        session_id = str(uuid.uuid4())  # Generate a new unique session ID

        response_stream = bedrock_agent_client.invoke_agent(
            agentId=agent_id,
            agentAliasId='380YCVUBPD',  # Alias ID from your settings
            sessionId=session_id,
            inputText=input_text,
            enableTrace=True  # Optional but recommended for debugging
        )

        # Initialize variable to collect the chunks from EventStream
        full_response = ""

        # Iterate over the EventStream
        for event in response_stream['completion']:
            if 'PayloadPart' in event:
                part_data = event['PayloadPart'].get('bytesValue')
                if part_data:
                    full_response += part_data.decode('utf-8')
            elif 'chunk' in event:
                chunk_data = event['chunk'].get('bytes')
                if chunk_data:
                    full_response += chunk_data.decode('utf-8')
        
        # Parse the full response
        if full_response:
            return full_response
        else:
            return "No response from agent"
    except Exception as e:
        st.error(f"Error invoking Bedrock agent: {str(e)}")
        return f"Error invoking agent: {str(e)}"

# Function to get weather data using the Bedrock agent
def get_weather_data(city, bedrock_agent_client):
    agent_id = 'ED0C3Z6GB6'  # Your weather agent ID from your settings
    input_text = f"What is the weather in {city}?"

    return invoke_bedrock_agent(agent_id, input_text, bedrock_agent_client)

# Function to extract temperature from weather data (ensure you modify it based on actual data structure)
def extract_temperature(weather_data):
    # Assuming temperature is embedded in weather_data response.
    # This is a placeholder - you'll need to adjust according to the actual data format you receive.
    return "64"  # Placeholder value, update as needed

# Function to display map with weather data and temperature
def display_map(latitude, longitude, weather_data, temperature):
    m = folium.Map(location=[latitude, longitude], zoom_start=10)
    
    # Add weather info as a circle
    folium.Circle(
        location=[latitude, longitude],
        radius=5000,
        color='blue',
        fill=True,
        fill_opacity=0.5,
        popup=f"Weather: {weather_data}"
    ).add_to(m)
    
    # Add temperature marker
    folium.Marker(
        location=[latitude, longitude],
        popup=f"Temperature: {temperature}°F",
        icon=folium.Icon(color='red')
    ).add_to(m)
    
    # Display map in Streamlit
    st_folium(m, width=700, height=500)

# Main Streamlit app layout
def main():
    st.markdown("""
    # ☁️ Weather and Data Visualization App for AWS NatSec by Adam Bluhm ☀️
    """)

    try:
        # Initialize Bedrock clients
        if 'bedrock_client' not in st.session_state:
            st.session_state['bedrock_client'] = get_bedrock_client()
        if 'bedrock_agent_client' not in st.session_state:
            st.session_state['bedrock_agent_client'] = get_bedrock_agent_client()

        bedrock_client = st.session_state['bedrock_client']
        bedrock_agent_client = st.session_state['bedrock_agent_client']

        # Sidebar for chatbot
        st.sidebar.title("Anthropic's Claude 3.5 Sonnent Chatbot - Running on Amazon Bedrock!")
        st.sidebar.markdown("""
        **This weather app demonstrates Amazon Bedrock Inference and Amazon Bedrock Agents. The Amazon Bedrock Agent, powered by a foundation model like Claude, orchestrates the interaction and can use defined action groups to make API calls to public weather APIs. The agent then integrates this information to provide a comprehensive response.**
        """)

        if 'chat_history' not in st.session_state:
            st.session_state['chat_history'] = []
        
        if 'last_query' not in st.session_state:
            st.session_state['last_query'] = ""

        user_input = st.sidebar.text_input("Ask something to the chatbot:")

        if user_input and user_input != st.session_state['last_query']:
            with st.spinner('Generating response...'):
                # If user asks for weather, detect the city from the input
                if "weather" in user_input.lower():
                    try:
                        city = user_input.lower().split("in")[-1].strip()
                        geolocator = Nominatim(user_agent="weather_app")
                        location = geolocator.geocode(city)
                        if location:
                            latitude, longitude = location.latitude, location.longitude
                            weather_data = get_weather_data(city, bedrock_agent_client)
                            temperature = extract_temperature(weather_data)  # Placeholder, modify based on actual weather data
                            st.session_state['weather_data'] = (latitude, longitude, weather_data, temperature)
                            bot_response = f"Here is the weather in {city}: {weather_data}"
                        else:
                            bot_response = "Sorry, I couldn't find that city."
                    except Exception as e:
                        bot_response = f"Error processing city: {str(e)}"
                else:
                    # Standard non-weather query handling
                    bot_response = invoke_bedrock_agent('ED0C3Z6GB6', user_input, bedrock_agent_client)
                
                st.session_state.chat_history.append({"user": user_input, "bot": bot_response})
                st.session_state['last_query'] = user_input

        if st.session_state.chat_history:
            for i, chat in enumerate(st.session_state.chat_history):
                message(chat['user'], is_user=True, key=f"user_{i}")
                message(chat['bot'], is_user=False, key=f"bot_{i}")

        # Display the map if weather data is present
        if 'weather_data' in st.session_state and st.session_state['weather_data']:
            latitude, longitude, weather_data, temperature = st.session_state['weather_data']
            display_map(latitude, longitude, weather_data, temperature)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
