# Bedrock Agents Weather App

This project deploys a weather application using AWS CDK, integrating Amazon Bedrock Agents with a Streamlit frontend. The application can be deployed on either EC2 or ECS, and uses Lambda functions to fetch weather data and geocode city names. This is for learning or dev/test and not meant for production.  

![unnamed](https://github.com/user-attachments/assets/edbc07a4-5063-4962-8cee-2002a0241713)


## Prerequisites

Before you begin, ensure you have the following:

1. An AWS account with appropriate permissions
2. AWS CLI installed and configured with your credentials
3. Node.js and npm installed (for CDK)
4. Python 3.9 or later installed
5. Git installed (for version control)

## Setup

1. Install the AWS CDK CLI:
   ```
   npm install -g aws-cdk
   ```

2. Clone this repository:
   ```
   git clone <your-repo-url>
   cd cdk_bedrock_agents_weather_app
   ```

3. Create and activate a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

4. Install the required Python dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Bootstrap your AWS environment (if you haven't already):
   ```
   cdk bootstrap aws://YOUR_ACCOUNT_NUMBER/YOUR_REGION
   ```

## Configuration

1. Open `cdk.json` and set your preferred deployment type:
   ```json
   {
     "context": {
       "deployment_type": "ECS"  // or "EC2"
     }
   }
   ```

2. If you're using EC2 deployment, update the S3 bucket name in `cdk_bedrock_agents_weather_app_stack.py`:
   ```python
   "aws s3 cp s3://your-bucket/streamlit_app/weather_app.py /home/ec2-user/weather_app.py",
   ```

3. Ensure your AWS account has the necessary permissions to create and manage the required resources (EC2, ECS, Lambda, VPC, etc.).

## Deployment

1. Synthesize the CloudFormation template:
   ```
   cdk synth
   ```

2. Deploy the stack:
   ```
   cdk deploy
   ```

3. After deployment, the CDK will output the URL where you can access the Streamlit app.

## Application Structure

- `app.py`: The entry point for the CDK application
- `cdk_bedrock_agents_weather_app/`:
  - `cdk_bedrock_agents_weather_app_stack.py`: Defines the main CDK stack
- `lambda_functions/`:
  - `get_weather/`: Contains the Lambda function for fetching weather data
  - `geocode_city/`: Contains the Lambda function for geocoding city names
- `streamlit_app/`:
  - `weather_app.py`: The Streamlit application
  - `Dockerfile`: For containerizing the Streamlit app (used in ECS deployment)

## Customization

- To modify the Streamlit app, edit `streamlit_app/weather_app.py`
- To change Lambda function behavior, modify the respective Python files in `lambda_functions/`
- To adjust the infrastructure, update `cdk_bedrock_agents_weather_app_stack.py`

## Cleanup

To avoid incurring future charges, remember to destroy the resources when you're done:

```
cdk destroy
```

## Troubleshooting

- If you encounter permission issues, ensure your AWS CLI is configured with the correct credentials and your account has the necessary permissions.
- For deployment errors, check the CloudFormation console in the AWS Management Console for detailed error messages.
- If the Streamlit app fails to load, check the EC2 instance logs or ECS task logs for any application-specific errors.

## Contributing

Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

## License
See LICENSE for more information 
