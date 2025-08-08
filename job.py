import requests
import datetime
import subprocess
import socket
from typing import List, Dict, Any

FIRST_URL = (
    "https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines?"
    "size=10000&select=date_derniere_modification_dpe%2Ccoordonnee_cartographique_x_ban%2C"
    "coordonnee_cartographique_y_ban%2Cnom_commune_ban%2Cnumero_voie_ban%2Ccode_postal_ban%2C"
    "nom_rue_ban%2Cadresse_brut%2Ccode_insee_ban%2Ccode_departement_ban%2Cscore_ban%2Ccode_region_ban%2C"
    "identifiant_ban%2Cstatut_geocodage%2Ccode_postal_brut%2Cnom_commune_brut%2Cnumero_etage_appartement%2C"
    "nom_residence%2Ccomplement_adresse_batiment%2Ccomplement_adresse_logement%2C_i%2Cdate_etablissement_dpe%2C"
    "date_visite_diagnostiqueur%2Cnumero_dpe%2Cetiquette_dpe%2Cannee_construction%2Csurface_habitable_logement%2C"
    "nombre_niveau_logement%2Cmethode_application_dpe%2Ctype_batiment%2C_id%2Cadresse_ban%2Cemission_ges_5_usages%2C"
    "emission_ges_chauffage%2Cemission_ges_ecs%2Cetiquette_ges%2Cconso_5_usages_ep%2Cnombre_niveau_logement%2C"
    "typologie_logement&sort=-date_derniere_modification_dpe"
)


class DPEResume:
    def __init__(self, data: Dict[str, Any]):
        self.ban_x = data.get("coordonnee_cartographique_x_ban", 0.0)
        self.ban_y = data.get("coordonnee_cartographique_y_ban", 0.0)
        self.ban_city = data.get("nom_commune_ban", "")
        self.ban_house_number = data.get("numero_voie_ban", "")
        self.ban_post_code = data.get("code_postal_ban", "")
        self.ban_street = data.get("nom_rue_ban", "")
        self.adresse_brut = data.get("adresse_brut", "")
        self.ban_city_code = data.get("code_insee_ban", "")
        self.ban_department = data.get("code_departement_ban", "")
        self.ban_score = data.get("score_ban", 0.0)
        self.ban_region = data.get("code_region_ban", "")
        self.ban_label = data.get("adresse_ban", "")
        self.ban_type = data.get("statut_geocodage", "")
        self.code_postal_brut = data.get("code_postal_brut", 0)
        self.nom_commune_brut = data.get("nom_commune_brut", "")
        self.compl_etage_appartement = data.get("numero_etage_appartement", 0)
        self.compl_nom_residence = data.get("nom_residence", "")
        self.compl_ref_batiment = data.get("complement_adresse_batiment", "")
        self.compl_ref_logement = data.get("complement_adresse_logement", "")
        self.ban_id = data.get("identifiant_ban", "")
        self.administratif_id = data.get("_i", 0)
        self.date_etablissement_dpe = data.get("date_etablissement_dpe", "")
        self.date_visite_diagnostiqueur = data.get("date_visite_diagnostiqueur", "")
        self.dpe_id = data.get("numero_dpe", "")
        self.identifiant_dpe = data.get("etiquette_dpe", "")
        self.annee_construction = data.get("annee_construction", 0)
        self.surface_habitable_logement = data.get("surface_habitable_logement", 0.0)
        self.nombre_niveau_logement = data.get("nombre_niveau_logement", 0)
        self.enum_methode_application_dpe_log_id = data.get("methode_application_dpe", "")
        self.type_batiment = data.get("type_batiment", "")
        self.date_derniere_modification_dpe = data.get("date_derniere_modification_dpe", "")
        self.emission_ges_5_usages = data.get("emission_ges_5_usages", 0.0)
        self.emission_ges_ch = data.get("emission_ges_chauffage", 0.0)
        self.emission_ges_ecs = data.get("emission_ges_ecs", 0.0)
        self.classe_emission_ges = data.get("etiquette_ges", "")
        self.ep_conso_5_usages = data.get("conso_5_usages_ep", 0.0)
        self.enum_position_etage_logement_id = data.get("nombre_niveau_logement", 0)
        self.enum_typologie_logement_id = data.get("typologie_logement", "")


class JSONResponse:
    def __init__(self, data: Dict[str, Any]):
        self.total = data.get("total", 0)
        self.next = data.get("next", "")
        self.results = [DPEResume(result) for result in data.get("results", [])]


def get_elements_from_api(url: str) -> bytes:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return b""


def parse_time(date_str: str) -> datetime.date:
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def pick_tuesday(date: datetime.date) -> datetime.date:
    if date.weekday() == 1:  # Tuesday
        return date

    delta = (1 - date.weekday()) % 7
    return date + datetime.timedelta(days=delta)


def handle_cmd_outputs(cmd: List[str]):
    try:
        output = subprocess.check_output(cmd, text=True)
        print(output)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")


def get_ip() -> str:
    try:
        # Create a temporary socket to determine the local IP address
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Connect the socket to an external address (Google DNS)
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception as e:
        print(f"Error getting IP address: {e}")
        return ""