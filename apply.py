import argparse
import json
import subprocess
import datetime
from typing import List
from job import DPEResume, get_elements_from_api, parse_time, pick_tuesday, handle_cmd_outputs, get_ip
from generate import generate_json, generate_sql_dump, generate_docker_file, generate_kubernetes_file


def main():
    parser = argparse.ArgumentParser(description="Process DPE data.")
    parser.add_argument("--json", action="store_true", help="Generate JSON file with DPE data")
    parser.add_argument("--from", dest="from_date", type=str, help="Date to read data from, with format yyyy-mm-dd")
    parser.add_argument("--to", dest="to_date", type=str, help="Date to read data to, with format yyyy-mm-dd")
    parser.add_argument("--build", action="store_true", help="Build and deploy on Kubernetes")
    args = parser.parse_args()

    from_date = parse_time(args.from_date) if args.from_date else None
    to_date = parse_time(args.to_date) if args.to_date else None
    file_name = ""

    total_json_elements: List[DPEResume] = []
    data = get_elements_from_api(FIRST_URL)

    json_response = json.loads(data)
    tuesday = pick_tuesday(datetime.date.today())
    least = tuesday - datetime.timedelta(days=8)  # A week before this Tuesday
    max_date = tuesday - datetime.timedelta(days=15)  # Two weeks before this Tuesday
    date_from_last_value = parse_time(json_response["results"][-1]["date_derniere_modification_dpe"])

    if not from_date or not to_date:
        while least <= date_from_last_value <= max_date:
            total_json_elements.extend([DPEResume(result) for result in json_response["results"]])
            data = get_elements_from_api(json_response["next"])
            json_response = json.loads(data)
            date_from_last_value = parse_time(json_response["results"][-1]["date_derniere_modification_dpe"])
        file_name = generate_sql_dump(total_json_elements, tuesday)
    else:
        while date_from_last_value >= from_date:
            data = get_elements_from_api(json_response["next"])
            json_response = json.loads(data)
            date_from_last_value = parse_time(json_response["results"][-1]["date_derniere_modification_dpe"])
            if date_from_last_value <= to_date:
                total_json_elements.extend([DPEResume(result) for result in json_response["results"]])
        file_name = generate_sql_dump(total_json_elements, from_date)

    if args.json:
        if not from_date or not to_date:
            generate_json(total_json_elements, tuesday, date_from_last_value)
        else:
            generate_json(total_json_elements, from_date, date_from_last_value)

    if args.build:
        generate_docker_file(file_name)
        cmd = ["sudo", "docker", "build", "-t", file_name.split(".")[0], "."]
        handle_cmd_outputs(cmd)

        cmd = ["sudo", "docker", "tag", file_name.split(".")[0], f"{get_ip()}:5000/{file_name.split('.')[0]}"]
        handle_cmd_outputs(cmd)

        cmd = ["sudo", "docker", "push", f"{get_ip()}:5000/{file_name.split('.')[0]}"]
        handle_cmd_outputs(cmd)

        file_name = generate_kubernetes_file(file_name.split(".")[0])
        cmd = ["kubectl", "apply", "-f", file_name]
        handle_cmd_outputs(cmd)


if __name__ == "__main__":
    main()