from importlib.metadata import distribution
from importlib.resources import path
from typing_extensions import runtime
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_s3 as _s3,
    RemovalPolicy,
    aws_s3_deployment as s3Deployment,
    aws_cloudfront as _CloudFront,
    aws_cloudfront_origins as origins,
    aws_apigateway as _apigw,
    aws_lambda as _lambda,
    aws_dynamodb as ddb,
)

#from cdk_dynamo_table_view import TableViewer

#from .hitcounter import HitCounter

class StaticWebsiteStack(Stack):

    @property
    def table(self):
            return self._table

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #S3 bucket creation and upload website to S3
        bucket = _s3.Bucket(self, id="Bucket",
                        bucket_name="my-static-web-abhi",
                        public_read_access=True,
                        removal_policy=RemovalPolicy.DESTROY,
                        website_index_document="index.html",
        )
        
        #create CDN CloudFront to host static website
        distribution = _CloudFront.Distribution(self,
                        "Distribution",
                        default_behavior=_CloudFront.BehaviorOptions(
                            origin= origins.S3Origin(bucket)
                        ),
                        #defaultRootObject="index.html",
        )

        #Static website deploy
        deployment = s3Deployment.BucketDeployment(
            self,
            "DeployWebsite",
            sources = [s3Deployment.Source.asset("website")],
            destination_bucket= bucket,
            distribution=distribution,
            #distributionPaths= ["/*"],
        )
        #create dynamodb
        counter_table = ddb.Table(
            self,
            "count_table",
            partition_key=ddb.Attribute(
                name='path',
                type = ddb.AttributeType.STRING
            )
        )

        #lambda function to update DB with path and count
        my_lambda = _lambda.Function(
            self, 'website-hitcounter-test',
            runtime = _lambda.Runtime.PYTHON_3_7,
            code = _lambda.Code.from_asset('lambda'),
            handler='hitcount.handler'
        )

        #Adding permission to lambda
        #my_lambda.add_environment("Hit_Function", my_lambda.function_name )
        my_lambda.add_environment("Table_Name", counter_table.table_name)
        counter_table.grant_read_write_data(my_lambda)

        #viewer lambda function
        viewer_lambda = _lambda.Function(
            self, 'website-hit-viewer',
            runtime = _lambda.Runtime.PYTHON_3_7,
            code = _lambda.Code.from_asset('lambda'),
            handler = 'countViewer.handler'
        )
        #add to env variable and providing permission
        viewer_lambda.add_environment("Table_Name", counter_table.table_name)
        counter_table.grant_read_data(viewer_lambda)

        #create API Gateway for viewer lambda function
        viewer_api = _apigw.RestApi(
            self,
            'APIGatewayViewTable',
            rest_api_name='APIGatewayViewTable'
        )
        viewer_entity = viewer_api.root.add_resource(
            'viewerResource',
            default_cors_preflight_options=_apigw.CorsOptions(
                allow_methods=['GET', 'OPTIONS'],
                allow_origins=_apigw.Cors.ALL_ORIGINS
            )
        )
        #API Gateway and Lambda integration
        viewer_lambda_integration = _apigw.LambdaIntegration(
            viewer_lambda,
            proxy=False,
            integration_responses=[
                _apigw.IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    }
                )
            ]
        )
        viewer_entity.add_method(
            'GET',
            viewer_lambda_integration,
            method_responses=[
                _apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ]
        )