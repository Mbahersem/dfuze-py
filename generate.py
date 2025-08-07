import json
from datetime import timedelta
from pathlib import Path

def generate_json(results, tuesday, last_date):
    tuesday = tuesday - timedelta(days=1)
    file_name = f"dpe_dump_{tuesday.strftime('%Y-%m-%d')}.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump([r.__dict__ if hasattr(r, '__dict__') else r for r in results], f, ensure_ascii=False, indent=2)
    print("Total elements:", len(results))
    print("Last date:", last_date)

def generate_sql_dump(results, tuesday):
    tuesday = tuesday - timedelta(days=1)
    file_name = f"dpe_dump_{tuesday.strftime('%Y-%m-%d')}.sql"
    create_stmt = """
CREATE TABLE IF NOT EXISTS dpe_resume (
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
    date_derniere_modification_dpe TEXT
);
"""
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(create_stmt)
        for element in results:
            # Convert object to dict if needed
            if hasattr(element, '__dict__'):
                e = element.__dict__
            else:
                e = element
            # Remove single quotes from string fields to avoid SQL errors
            def clean(val):
                if isinstance(val, str):
                    return val.replace("'", "")
                return val
            sql = (
                "INSERT INTO dpe_resume (ban_x, ban_y, ban_city, ban_house_number, ban_post_code, ban_street, adresse_brut, "
                "ban_city_code, ban_department, ban_score, ban_region, ban_label, ban_type, code_postal_brut, nom_commune_brut, "
                "compl_etage_appartement, compl_nom_residence, compl_ref_batiment, compl_ref_logement, ban_id, administratif_id, "
                "date_etablissement_dpe, date_visite_diagnostiqueur, dpe_id, identifiant_dpe, annee_construction, "
                "surface_habitable_logement, nombre_niveau_logement, enum_methode_application_dpe_log_id, type_batiment, "
                "date_derniere_modification_dpe) VALUES "
                f"({e.get('coordonne_cartographique_x_ban', 0)},{e.get('coordonne_cartographique_y_ban', 0)},'{clean(e.get('nom_commune_ban', ''))}','{clean(e.get('numero_voie_ban', ''))}',"
                f"'{clean(e.get('code_postal_ban', ''))}','{clean(e.get('nom_rue_ban', ''))}','{clean(e.get('adresse_brut', ''))}',"
                f"'{clean(e.get('code_insee_ban', ''))}','{clean(e.get('code_departement_ban', ''))}',{e.get('score_ban', 0)},"
                f"'{clean(e.get('code_region_ban', ''))}','{clean(e.get('adresse_ban', ''))}','{clean(e.get('statut_geocodage', ''))}',"
                f"{e.get('code_postal_brut', 0)},'{clean(e.get('nom_commune_brut', ''))}',{e.get('numero_etage_appartement', 0)},"
                f"'{clean(e.get('nom_residence', ''))}','{clean(e.get('complement_adresse_batiment', ''))}','{clean(e.get('complement_adresse_logement', ''))}',"
                f"'{clean(e.get('identifiant_ban', ''))}',{e.get('_i', 0)},'{clean(e.get('date_etablissement_dpe', ''))}',"
                f"'{clean(e.get('date_visite_diagnostiqueur', ''))}','{clean(e.get('numero_dpe', ''))}','{clean(e.get('etiquette_dpe', ''))}',"
                f"{e.get('annee_construction', 0)},{e.get('surface_habitable_logement', 0)},{e.get('nombre_niveau_logement', 0)},"
                f"'{clean(e.get('methode_application_dpe', ''))}','{clean(e.get('type_batiment', ''))}',"
                f"'{clean(e.get('date_derniere_modification_dpe', ''))}');\n"
            )
            f.write(sql)
    return file_name

def generate_dockerfile(file_name):
    dockerfile_content = f"""
FROM postgis/postgis
COPY ./{file_name} /docker-entrypoint-initdb.d/
ENV POSTGRES_PASSWORD=j2m2025
"""
    with open("Dockerfile", "w", encoding="utf-8") as f:
        f.write(dockerfile_content)
    print("Dockerfile generated successfully.")

def generate_kubernetes_file(file_name):
    file_generated = f"{file_name}.yaml"
    date_part = file_name.split("_")[2] if len(file_name.split("_")) > 2 else "unknown"
    k8s_content = f"""apiVersion: v1
kind: Pod
metadata:
  name: {file_name.replace('_', '-')}
  namespace: update
  labels:
    type: delta
    date: {date_part}
spec:
  nodeSelector:
    test: "true"
  imagePullSecrets:
  - name: regcred
  containers:
  - image: localhost:5000/{file_name}
    name: dump
    ports:
    - containerPort: 5432
      protocol: TCP
"""
    with open(file_generated, "w", encoding="utf-8") as f:
        f.write(k8s_content)
    print("Kubernetes file generated successfully:", file_generated)
    return file_generated