import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_bedrock_agents_weather_app.cdk_bedrock_agents_weather_app_stack import CdkBedrockAgentsWeatherAppStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_bedrock_agents_weather_app/cdk_bedrock_agents_weather_app_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkBedrockAgentsWeatherAppStack(app, "cdk-bedrock-agents-weather-app")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
