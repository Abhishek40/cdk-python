#!/usr/bin/env python3

import aws_cdk as cdk

from static_website.static_website_stack import StaticWebsiteStack


app = cdk.App()
StaticWebsiteStack(app, "static-website")

app.synth()
