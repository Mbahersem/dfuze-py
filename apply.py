import argparse
import subprocess
import sys
from datetime import datetime, timedelta
import os
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Import from local modules
from job import get_elements_from_api, FIRST_URL, JSONResponse, pick_tuesday, parse_time, handle_cmd_outputs
from generate import generate_sql_dump, generate_dockerfile, generate_kubernetes_file, generate_json

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Process DPE data")
    parser.add_argument('--json', action='store_true', help='Generate JSON file with DPE data')
    args = parser.parse_args()

    # Simulate in-memory DB with a list (no ORM needed for this script)
    total_json_elements = []

    # Get first page of data
    data = get_elements_from_api(FIRST_URL)
    if not data:
        print("Failed to fetch data from API.")
        sys.exit(1)

    json_response = JSONResponse.from_json(requests.get(FIRST_URL).json())

    tuesday = pick_tuesday(datetime.now())
    least = tuesday - timedelta(days=7)
    max_ = tuesday - timedelta(days=15)
    date_from_last_value = parse_time(json_response.results[9999].date_derniere_modification_dpe)

    while date_from_last_value and least > date_from_last_value > max_:
        total_json_elements.extend(json_response.results)
        if not json_response.next:
            break
        data = get_elements_from_api(json_response.next)
        if not data:
            print("Failed to fetch next page from API.")
            break
        json_response = JSONResponse.from_json(requests.get(json_response.next).json())
        date_from_last_value = parse_time(json_response.results[9999].date_derniere_modification_dpe)

    file_name = generate_sql_dump(total_json_elements, tuesday)
    generate_dockerfile(file_name)
    image_tag = file_name.split(".")[0]

    # Build Docker image
    cmd = ["sudo", "docker", "build", "-t", image_tag, "."]
    handle_cmd_outputs(cmd)

    # Tag Docker image
    cmd = ["sudo", "docker", "tag", image_tag, f"localhost:5000/{image_tag}"]
    handle_cmd_outputs(cmd)

    # Push Docker image
    cmd = ["sudo", "docker", "push", f"localhost:5000/{image_tag}"]
    handle_cmd_outputs(cmd)

    # Generate and apply Kubernetes file
    k8s_file = generate_kubernetes_file(image_tag)
    cmd = ["kubectl", "apply", "-f", k8s_file]
    handle_cmd_outputs(cmd)

    if args.json:
        generate_json(total_json_elements, tuesday, date_from_last_value)

if __name__ == "__main__":
    main()