#!/usr/bin/env python3

import aws_cdk as cdk

from static_website.static_website_stack import StaticWebsiteStack

app = cdk.App()
env_EU = cdk.Environment(account="266186731626", region="eu-central-1")
StaticWebsiteStack(app, "static-website", env=env_EU)

app.synth()
