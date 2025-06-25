import ssl
import socket
import json
from datetime import datetime, timedelta
from urllib.parse import urlparse

def verifier_certificat_ssl(url):
    resultat = {
        "date_expiration": None,
        "statut": "invalide"
    }
    
    try:
        # Extraire le nom d'hôte et le port
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        port = parsed_url.port or 443  # HTTPS par défaut

        # Créer une connexion SSL
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                
                cert = ssock.getpeercert()
                
                # Extraire la date d'expiration
                expire_date_str = cert['notAfter']
                expire_date = datetime.strptime(expire_date_str, '%b %d %H:%M:%S %Y %Z')

                # Formater la date
                date_expiration_formatee = expire_date.strftime("%Y_%m_%d_%H_%M_%S")
                resultat["date_expiration"] = date_expiration_formatee

                # Calculer le temps restant
                jours_restants = (expire_date - datetime.utcnow()).days

                if jours_restants < 0:
                    resultat["statut"] = "invalide"
                elif jours_restants <= 15:
                    resultat["statut"] = "expire_bientot"
                else:
                    resultat["statut"] = "valide"

    except Exception:
        resultat["statut"] = "invalide"

    return json.dumps(resultat, ensure_ascii=False, indent=4)


# Exemple d'utilisation
if __name__ == "__main__":
    url = input("Entrez une URL (ex: https://www.exemple.com): ")
    print(verifier_certificat_ssl(url))
