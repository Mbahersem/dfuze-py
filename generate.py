import json
import os
import datetime
from typing import List
from job import DPEResume, get_ip


def generate_json(results: List[DPEResume], tuesday: datetime.date, last_date: datetime.date):
    """
    Génère un fichier JSON contenant les résultats.
    """
    tuesday = tuesday - datetime.timedelta(days=1)
    file_name = f"dpe_dump_{tuesday.strftime('%Y-%m-%d')}.json"
    with open(file_name, "w") as file:
        json.dump([result.__dict__ for result in results], file, indent=4)
    print("Total elements:", len(results))
    print("Last date:", last_date)


def generate_sql_dump(results: List[DPEResume], tuesday: datetime.date) -> str:
    """
    Génère un fichier SQL contenant les résultats.
    """
    tuesday = tuesday - datetime.timedelta(days=1)
    file_name = f"dpe_dump_{tuesday.strftime('%Y-%m-%d')}.sql"
    with open(file_name, "w") as file:
        create_stmt = """
        CREATE TABLE IF NOT EXISTS dpe_resume (
            id SERIAL,
            ban_x REAL,
            ban_y REAL,
            ban_city TEXT,
            ban_house_number TEXT,
            ban_post_code TEXT,
            ban_street TEXT,
            adresse_brut TEXT,
            ban_city_code TEXT,
            ban_department TEXT,
            ban_score REAL,
            ban_region TEXT,
            ban_label TEXT,
            ban_type TEXT,
            code_postal_brut INTEGER,
            nom_commune_brut TEXT,
            compl_etage_appartement INTEGER,
            compl_nom_residence TEXT,
            compl_ref_batiment TEXT,
            compl_ref_logement TEXT,
            ban_id TEXT,
            administratif_id BIGINT,
            date_etablissement_dpe TEXT,
            date_visite_diagnostiqueur TEXT,
            dpe_id TEXT,
            identifiant_dpe TEXT,
            annee_construction INTEGER,
            surface_habitable_logement REAL,
            nombre_niveau_logement INTEGER,
            enum_methode_application_dpe_log_id TEXT,
            type_batiment TEXT,
            date_derniere_modification_dpe TEXT,
            emission_ges_5_usages REAL,
            emission_ges_ch REAL,
            emission_ges_ecs REAL,
            classe_emission_ges TEXT,
            ep_conso_5_usages REAL,
            enum_position_etage_logement_id INTEGER,
            enum_typologie_logement_id TEXT,
            geom GEOMETRY(POINT, 2154)
        );

        CREATE INDEX IF NOT EXISTS idx_dpe_resume_ban_x ON dpe_resume (ban_x);
        CREATE INDEX IF NOT EXISTS idx_dpe_resume_ban_y ON dpe_resume (ban_y);

        CREATE INDEX IF NOT EXISTS dpe_index_geom ON dpe_resume USING GIST (geom);

        CREATE TABLE IF NOT EXISTS dpe_defaillant (
            dpe_id TEXT
        );
        """
        file.write(create_stmt)

        for element in results:
            sql = f"""
            INSERT INTO dpe_resume (
                ban_x, ban_y, ban_city, ban_house_number, ban_post_code, ban_street, adresse_brut, ban_city_code,
                ban_department, ban_score, ban_region, ban_label, ban_type, code_postal_brut, nom_commune_brut,
                compl_etage_appartement, compl_nom_residence, compl_ref_batiment, compl_ref_logement, ban_id,
                administratif_id, date_etablissement_dpe, date_visite_diagnostiqueur, dpe_id, identifiant_dpe,
                annee_construction, surface_habitable_logement, nombre_niveau_logement,
                enum_methode_application_dpe_log_id, type_batiment, date_derniere_modification_dpe,
                emission_ges_5_usages, emission_ges_ch, emission_ges_ecs, classe_emission_ges, ep_conso_5_usages,
                enum_position_etage_logement_id, enum_typologie_logement_id, geom
            ) VALUES (
                {element.ban_x}, {element.ban_y}, '{element.ban_city.replace("'", "")}', '{element.ban_house_number.replace("'", "")}',
                '{element.ban_post_code.replace("'", "")}', '{element.ban_street.replace("'", "")}', '{element.adresse_brut.replace("'", "")}',
                '{element.ban_city_code.replace("'", "")}', '{element.ban_department.replace("'", "")}', {element.ban_score},
                '{element.ban_region.replace("'", "")}', '{element.ban_label.replace("'", "")}', '{element.ban_type.replace("'", "")}',
                {element.code_postal_brut}, '{element.nom_commune_brut.replace("'", "")}', {element.compl_etage_appartement},
                '{element.compl_nom_residence.replace("'", "")}', '{element.compl_ref_batiment.replace("'", "")}',
                '{element.compl_ref_logement.replace("'", "")}', '{element.ban_id.replace("'", "")}', {element.administratif_id},
                '{element.date_etablissement_dpe.replace("'", "")}', '{element.date_visite_diagnostiqueur.replace("'", "")}',
                '{element.dpe_id.replace("'", "")}', '{element.identifiant_dpe.replace("'", "")}', {element.annee_construction},
                {element.surface_habitable_logement}, {element.nombre_niveau_logement}, '{element.enum_methode_application_dpe_log_id.replace("'", "")}',
                '{element.type_batiment.replace("'", "")}', '{element.date_derniere_modification_dpe.replace("'", "")}', {element.emission_ges_5_usages},
                {element.emission_ges_ch}, {element.emission_ges_ecs}, '{element.classe_emission_ges.replace("'", "")}', {element.ep_conso_5_usages},
                {element.enum_position_etage_logement_id}, '{element.enum_typologie_logement_id.replace("'", "")}',
                ST_SetSRID(ST_MakePoint({element.ban_x}, {element.ban_y}), 2154)
            );
            """
            if element.ban_x == 0 or element.ban_y == 0 or not element.identifiant_dpe:
                sql += f"""
                INSERT INTO dpe_defaillant (dpe_id) VALUES ('{element.dpe_id.replace("'", "")}');\n
                """
            file.write(sql)

    return file_name


def generate_docker_file(file_name: str):
    """
    Génère un fichier Dockerfile.
    """
    content = f"""FROM node AS api
WORKDIR /app
COPY /express .
RUN npm install

FROM postgis/postgis AS db
COPY --from=api /app /var/www/app
COPY docker-entrypoint.sh docker-entrypoint.sh

RUN chmod +x docker-entrypoint.sh && \\
    chmod +x /var/www/app/init.sh

RUN apt update -y && \\
    apt install nodejs npm -y && \\
    apt install supervisor nginx -y && \\
    adduser j2m
    
ENV POSTGRES_PASSWORD=j2m2025

COPY ./{file_name} /docker-entrypoint-initdb.d/
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY nginx.conf /etc/nginx/sites-available/default.conf
# Launching of the Express API through Nginx
RUN service nginx start

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
"""
    with open("Dockerfile", "w") as file:
        file.write(content)
    print("Dockerfile generated successfully.")


def generate_kubernetes_file(file_name: str) -> str:
    """
    Génère un fichier Kubernetes YAML.
    """
    file_generated = f"{file_name}.yaml"
    content = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {file_name.replace('_', '-')}
  namespace: update
spec:
  replicas: 1
  selector: 
    matchLabels:
      type: delta
  template:
    metadata:
      labels:
        type: delta
        date: {file_name.split('_')[2]}
    spec:
      containers:
      - image: {get_ip()}:5000/{file_name}
        name: dump
        ports:
        - containerPort: 3000
          name: web
          protocol: TCP
        readinessProbe:
          httpGet: 
            path: /api/healthcheck/ready
            port: web
          initialDelaySeconds: 30
        livenessProbe:
          httpGet:
            path: /api/healthchecker
            port: web
"""
    with open(file_generated, "w") as file:
        file.write(content)
    print("Kubernetes file generated successfully:", file_generated)
    return file_generated