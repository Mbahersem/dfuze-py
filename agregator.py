import json
import requests
from flask import Flask, request, jsonify
import subprocess
from datetime import datetime

app = Flask(__name__)


def get_from_deltas(top_left: str, bottom_right: str):
    """
    Récupère les données des services delta et les fusionne.
    """
    merged_elements = []

    # Exécute la commande pour obtenir les adresses IP des services delta
    cmd_string = "kubectl exec dnsutils -- nslookup delta-service.update.svc.cluster.local | grep Address:"
    output = subprocess.check_output(["bash", "-c", cmd_string], text=True)
    list_ips = output.split("Address:")

    for e in list_ips[2:]:
        e = e.strip()
        url = f"http://{e}:3000/geolocdpe/api/v0/dpe/get?topLeft={top_left}&bottomRight={bottom_right}"
        data = fetch(url)
        json_response = json.loads(data)

        if not merged_elements:
            merged_elements.extend(json_response)
        else:
            for rep in json_response:
                is_modified = False
                for mer in merged_elements:
                    if (
                        mer["dpe_id"] == rep["dpe_id"]
                        and parse_time(rep["date_derniere_modification_dpe"]) > parse_time(mer["date_derniere_modification_dpe"])
                    ):
                        mer.update(rep)
                        is_modified = True
                        break
                if not is_modified:
                    merged_elements.append(rep)

    return merged_elements


def fetch(url: str):
    """
    Effectue une requête HTTP GET et retourne les données.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return b""


def parse_time(date_str: str):
    """
    Parse une chaîne de date au format yyyy-mm-dd en objet datetime.
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None


@app.route("/geolocdpe/api/v0/dpe/get", methods=["GET"])
def get():
    """
    Endpoint pour récupérer les données DPE.
    """
    query_values = request.args
    top_left = query_values.get("topLeft")
    bottom_right = query_values.get("bottomRight")

    deltas = get_from_deltas(top_left, bottom_right)

    print(len(deltas))
    return jsonify(deltas)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4500)