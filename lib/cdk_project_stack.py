from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr_assets as ecr_assets,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_elasticloadbalancingv2 as elbv2,
    CfnOutput
)
from constructs import Construct

class CdkBedrockAgentsWeatherAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get deployment preference from context
        deployment_type = self.node.try_get_context("deployment_type") or "ECS"

        # Create VPC
        vpc = ec2.Vpc(self, "WeatherAppVPC", max_azs=2)

        # Define Lambda functions
        get_weather_lambda = _lambda.Function(
            self, 'GetWeatherLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='NOAA_API_Weather_Lambda.lambda_handler',
            code=_lambda.Code.from_asset('lambda_functions/get_weather'),
        )

        geocode_city_lambda = _lambda.Function(
            self, 'GeocodeCityLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='OpenStreamMapAPI_Lambda.lambda_handler',
            code=_lambda.Code.from_asset('lambda_functions/geocode_city'),
        )

        if deployment_type == 'EC2':
            # EC2 Deployment
            instance = ec2.Instance(
                self, "WeatherAppInstance",
                instance_type=ec2.InstanceType("t3.micro"),
                machine_image=ec2.MachineImage.latest_amazon_linux(),
                vpc=vpc,
            )

            # Allow inbound traffic on port 8501
            instance.connections.allow_from_any_ipv4(
                ec2.Port.tcp(8501),
                description="Allow Streamlit traffic"
            )

            # User data to set up the Streamlit app
            instance.add_user_data(
                "yum update -y",
                "yum install -y python3 python3-pip",
                "pip3 install streamlit geopy folium streamlit-folium boto3",
                "aws s3 cp s3://your-bucket/streamlit_app/weather_app.py /home/ec2-user/weather_app.py",
                "streamlit run /home/ec2-user/weather_app.py --server.port 8501 --server.address 0.0.0.0"
            )

            CfnOutput(self, "AppURL",
                      value=f"http://{instance.instance_public_dns_name}:8501",
                      description="URL of Streamlit App on EC2")

        elif deployment_type == 'ECS':
            # ECS Deployment
            cluster = ecs.Cluster(self, "WeatherAppCluster", vpc=vpc)

            task_definition = ecs.FargateTaskDefinition(
                self, "WeatherAppTaskDef",
                memory_limit_mib=512,
                cpu=256,
            )

            container = task_definition.add_container(
                "WeatherAppContainer",
                image=ecs.ContainerImage.from_asset("streamlit_app"),
                port_mappings=[ecs.PortMapping(container_port=8501)],
            )

            service = ecs.FargateService(
                self, "WeatherAppService",
                cluster=cluster,
                task_definition=task_definition,
                assign_public_ip=True,
            )

            lb = elbv2.ApplicationLoadBalancer(
                self, "WeatherAppLB",
                vpc=vpc,
                internet_facing=True
            )

            listener = lb.add_listener(
                "WeatherAppListener",
                port=80,
            )

            listener.add_targets(
                "WeatherAppTarget",
                port=8501,
                targets=[service]
            )

            CfnOutput(self, "AppURL",
                      value=f"http://{lb.load_balancer_dns_name}",
                      description="URL of Streamlit App on ECS")

        # Bedrock Agent setup would go here
        # This part requires custom implementation as there's no native CDK construct for Bedrock Agents yet
        # You might need to use custom resources or the AWS SDK (boto3) to set this up

        # Output Lambda ARNs for use in Bedrock Agent setup
        CfnOutput(self, "GetWeatherLambdaArn", value=get_weather_lambda.function_arn)
        CfnOutput(self, "GeocodeCityLambdaArn", value=geocode_city_lambda.function_arn)
