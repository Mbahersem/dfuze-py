from dataclasses import dataclass
from datetime import datetime, timedelta
import requests
import subprocess
from typing import List, Optional
from sqlalchemy import Column, Float, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

FIRST_URL = os.getenv("FIRST_URL")

@dataclass
class JSONResponse:
    total: int
    next: str
    results: List['DPEResume']

    @classmethod
    def from_json(cls, data: dict) -> 'JSONResponse':
        return cls(
            total=data['total'],
            next=data['next'],
            results=[DPEResume(**r) for r in data['results']]
        )

class DPEResume(Base):
    __tablename__ = 'dpe_resume'

    id = Column(Integer, primary_key=True)
    coordonne_cartographique_x_ban = Column(Float)
    coordonne_cartographique_y_ban = Column(Float)
    nom_commune_ban = Column(String)
    numero_voie_ban = Column(String)
    code_postal_ban = Column(String)
    nom_rue_ban = Column(String)
    adresse_brut = Column(String)
    code_insee_ban = Column(String)
    code_department_ban = Column(String)
    score_ban = Column(Float)
    code_region_ban = Column(String)
    adresse_ban = Column(String)
    statut_geocodage = Column(String)
    code_postal_brut = Column(Integer)
    nom_commune_brut = Column(String)
    numero_etage_appartement = Column(Integer)
    nom_residence = Column(String)
    complement_adresse_batiment = Column(String)
    complement_adresse_logement = Column(String)
    identifiant_ban = Column(String)
    _i = Column(Integer)
    date_etablissement_dpe = Column(String)
    date_visite_diagnostiqueur = Column(String)
    numero_dpe = Column(String)
    etiquette_dpe = Column(String)
    annee_construction = Column(Integer)
    surface_habitable_logement = Column(Float)
    nombre_niveau_logement = Column(Integer)
    methode_application_dpe = Column(String)
    type_batiment = Column(String)
    date_derniere_modification_dpe = Column(String)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def get_elements_from_api(url: str) -> Optional[bytes]:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Error fetching data from API: {e}")
        return None

def handle_cmd_outputs(cmd: List[str]) -> None:
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")

def pick_tuesday(date: datetime) -> datetime:
    """Find the previous Tuesday."""
    days_to_tuesday = (date.weekday() - 1) % 7
    return date - timedelta(days=days_to_tuesday)

def parse_time(date_str: str) -> Optional[datetime]:
    """Parse a date string into a datetime object."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None

# if __name__ == '__main__':
#     # Example Usage (Database setup and data loading)
#     engine = create_engine('sqlite:///:memory:')  # Use an in-memory SQLite database
#     Base.metadata.create_all(engine)

#     Session = sessionmaker(bind=engine)
#     session = Session()

#     # Fetch data from API
#     data = get_elements_from_api(FIRST_URL)
#     if data:
#         json_data = requests.get(FIRST_URL).json()
#         json_response = JSONResponse.from_json(json_data)

#         # Add data to the database
#         for record in json_response.results:
#             session.add(record)

#         session.commit()

#         # Query the database
#         first_record = session.query(DPEResume).first()
#         if first_record:
#             print(f"First record in database: {first_record.BanCity}")

#     session.close()