# filepath: k:\Devops\PipeGuard\main.py
from monitor_pipeline import monitor_pipeline
import functions_framework

# This file imports the monitor_pipeline function so that 
# Google Cloud Functions can find it at deployment time

# For Cloud Functions deployment
@functions_framework.http
def main(request):
    return monitor_pipeline(request)
