# dfuze-py
Version Python de `dfuze`.

## Avant de commencer
Il est préférable d'avoir un cluster Kubernetes configuré avec un registre privé et Docker installé. Par la suite, il nous faut créer un environnement virtuel via :
```bash
python3 -m venv dpe-env
```
Puis il faudra l'activer :
```bash
source dpe-env/bin/activate
```
Une fois cela effectué, on peut procéder à l'installation des bibliothèques nécessaires :
```bash
pip install -r requirements.txt
```
Voilà ! Nous voici parés.

## `apply.py`
Il s'agit du module chargé de la récupération des données, de la création des dumps, de la conteneurisation et du déploiement. On peut l'exécuter simplement ou lui passer des arguments car il est fait pour fonctionner comme une invite de commande. On va d'abord commencer par présenter les arguments :
* `--build` : qui est de type booléen, permet d'effectuer la conteneurisation, le push sur le registre privé et le déploiement sur Kubernetes.
* `--json` : qui est de type booléen, permet de demander la création d'un dump JSON.
* `--from` : qui est de type string au format *yyyy-mm-dd*, qui nous permet de contourner le comportemnt de base du module afin de récupérer les données à partir d'une date précise.
* `--to` : qui est de type string au format *yyyy-mm-dd*, qui s'utilise toujours en complément de `--from` et renseigne sur la date de fermeture de l'intervalle de récupération.

Comme énoncé, on peut exécuter sans arguments :
```bash
python3 apply.py
```
Cela aura pour conséquence de récupérer les données de la semaine passée à partir de mardi, car on suppose qu'à partir de ce jour, la base de données sera à jour s'il y a eu des modifications. En effet, on s'est rendus compte que la base de données est mise à jour entre dimanche et lundi; par sécurité, on a donc choisi mardi. Enfin, il en créera le dump SQL.

Cependant
```bash
python3 apply.py --from=2025-07-20 --to=2025-07-28 --build --json
```
Cette commande aura pour effet de récupérer les données entre le 20/07/2025 et le 28/07/2025, de créer le dump SQL, de créer le dump JSON, de créer l'image Docker, de publier l'image Docker sur le registre privé et de déployer le composant sur Kubernetes.

## `job.py`
Module contenant la requête effectuée à l'organisme gérant la base de données. Il contient également les structures de données définies et quelques fonctions d'utilité pour `generate.py` et `apply.py`.

## `generate.py`
Module qui a trait à tout ce qui concerne la génération de fichiers comme les dumps JSON ou SQL en passant par le Dockerfile et le fichier de configuration Kubernetes.

## `agregator.py`
Ce module joue le rôle de composant intermédiaire chargé d'effectuer les requêtes à toutes les versions et d'agréger les réponses pour n'en retourner qu'une seule au format JSON. Il utilise Kubernetes pour fonctionner, notamment le serveur DNS afin d'effectuer des requêtes à tous les pods concernés. De plus, il fonctionne comme un serveur d'API qui est exposé sur le port 4500.

On le lance avec la commande :
```bash
python3 agregator.py
```
Comme exemple de requête, on a  celle-ci qui couvre toute la superficie de la France :
```bash
curl -v "http://localhost:4500/geolocdpe/api/v0/dpe/get?topLeft=7335619.84,125949.19&bottomRight=5758413.10,1976627.53"
```