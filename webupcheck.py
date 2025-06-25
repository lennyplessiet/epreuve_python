import os, sys, json, requests, datetime
from discord_webhook import DiscordWebhook

from verification_ssl import verifier_certificat_ssl

# Ouverture du fichier json, creation du fichier si inexistant
if not(os.path.isfile('websiteList.json')):
    print("Creation du fichier json...")
    websiteJsonFile = open('websiteList.json', "w")
    websiteJsonFile.write('{"websites": {}, "discordUrl": "https://discord.com/api/webhooks/1387350099973247077/ZtfZWKJrYEWxTyFSI3yJkn7haTEeFvaSy06etsPxD2qN__plpVKFaBFkqd2gVSlpvLXl"}')
else:
    print("Lecture du fichier json...")
    websiteJsonFile = open('websiteList.json')
websiteJsonFile.close()

#Verification de l'intégrité du fichier
try:
    websiteJsonFile = open('websiteList.json')
    websiteJson = websiteJsonFile.read()
    websiteJson = json.loads(websiteJson)
except Exception as e:
    print(e)
    print("Erreur lors de la lecture du fichier websiteList.json. Veuillez supprimer le fichier ou le remettre au bon format.")
    exit()
websiteJsonFile.close()

# Lecture des paramètres
websites = websiteJson['websites']
discordUrl = websiteJson['discordUrl']
parametres = sys.argv

# Ajout d'un site
if "--add" in parametres:
    position_parametre = parametres.index('--add')
    if "--"  in parametres[position_parametre + 1] or "--" in parametres[position_parametre + 2]:
        print("Erreur dans le parametre --add.")
        print("Usage: --add <nom> <url>")
    else:
        nom_site = parametres[position_parametre + 1]
        url_site = parametres[position_parametre + 2]
        if not("https://" in url_site or "http://" in url_site):
            url_site = ''.join(("https://", url_site))
        print(f"Ajout du nouveau site \"{nom_site}\"  dans le fichier...")

        websites[nom_site] = {
            "url": url_site,
            "status": "UP"
        }
        try:
            websiteJsonFile = open('websiteList.json', "w")
            websiteJsonFile.write(json.dumps(websiteJson))
            websiteJsonFile.close()
            print(f"Le site {nom_site} correspondant à l'url {url_site} a bien été ajouté au fichier.")
        except Exception as e:
            print(e)
            print("Erreur lors de l'ajout du site au fichier.")
            print("Usage: --add <nom> <url>")

# Suppression d'un site
if "--remove" in parametres:
    position_parametre = parametres.index('--remove')
    if "--"  in parametres[position_parametre + 1]:
        print("Erreur dans le parametre --remove.")
        print("Usage: --remove <nom>")
    else:
        nom_site = parametres[position_parametre + 1]
        try:
            print(f"Suppression du site {nom_site}...")
            del websites[nom_site]
            websiteJsonFile = open('websiteList.json', "w")
            websiteJsonFile.write(json.dumps(websiteJson))
            websiteJsonFile.close()
            print(f"Le site {nom_site} a bien été supprimé.")
        except Exception as e:
            print(f"Erreur lors de la suppression du site: {e}")

# Liste des sites ajoutés
if "--list" in parametres:
    print("Voici la liste des sites enregistrés pour la vérification")
    for website in websites:
        print(f"Site \"{website}\" associé à l'url {websites[website]['url']}")

# Verification des sites
if "--check" in parametres:
    position_parametre = parametres.index('--check')
    if not(os.path.isdir('log')):
        print('Creation du dossier log...')
        os.mkdir('log')
    print("Lancement de la vérification du statut des sites enregistrés...")
    for website in websites:
        requete_statuscode = requests.get(websites[website]['url']).status_code
        if 200 <= int(requete_statuscode) <= 299:
            status = "UP"
        else:
            status = "DOWN"
        certificat_ssl = json.loads(verifier_certificat_ssl(websites[website]['url']))
        if len(parametres) > position_parametre+1:
            if "--discord" in parametres[position_parametre + 1] and status != websites[website]["status"]:
                print("discord", "--discord" in parametres[position_parametre + 1] and status != websites[website]["status"])
                message = f"Le site {website} associé à l'url {websites[website]['url']} est {status} (précédemment {websites[website]["status"]}). Statut du certificat ssl: {certificat_ssl['statut']}"
                webhook = DiscordWebhook(url=discordUrl, content=message)
                response = webhook.execute()
        websites[website]["status"] = status
        websiteJsonFile = open('websiteList.json', "w")
        websiteJsonFile.write(json.dumps(websiteJson))
        websiteJsonFile.close()
        date = datetime.datetime.now()
        date = f"{date.year}_{date.month}_{date.day}_{date.hour}_{date.minute}_{date.second}"
        request_log = {
            'date': date,
            'url': websites[website]['url'],
            'http_code': requete_statuscode,
            'status' : status,
            'certificat_ssl': certificat_ssl
        }
        log_file = open(f"log/log_{website}_{date}.json", "w")
        log_file.write(json.dumps(request_log))
        log_file.close()
        print(requests.get(websites[website]['url']).status_code, verifier_certificat_ssl(websites[website]['url']))

if "--export" in parametres:
    position_parametre = parametres.index('--export')
    if not(os.path.isdir('exports')):
        print('Creation du dossier exports...')
        os.mkdir('exports')
    if len(parametres) > position_parametre + 1:
        if "--" in parametres[position_parametre + 1]:
            print("Erreur dans le parametre --export.")
            print("Usage: --export <nom>")
        else:
            csvContent = "nom du site; url du site; date; code http; statut; date d'expiration du certificat ssl; validite \n"
            nom_site = parametres[position_parametre + 1]
            for file in os.listdir("log"):
                filename = os.fsdecode(file)
                print(filename)
                if nom_site in filename:
                    file = open(f"log/{filename}")
                    fileContent = file.read()
                    fileContentJson = json.loads(fileContent)
                    csvContent += f"{nom_site}; {fileContentJson['url']}; {fileContentJson['date']}; {fileContentJson['http_code']}; {fileContentJson['status']}; {fileContentJson['certificat_ssl']['date_expiration']}; {fileContentJson['certificat_ssl']['statut']} \n"
            print(csvContent)
            date = datetime.datetime.now()
            date = f"{date.year}_{date.month}_{date.day}_{date.hour}_{date.minute}_{date.second}"
            csvFile = open(f"exports/export_{nom_site}_{date}.csv", "w")
            csvFile.write(csvContent)