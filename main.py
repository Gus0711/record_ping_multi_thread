import concurrent.futures
from ping3 import ping
import os
import time
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import csv
import socket
import ipaddress


# Déclarer la variable globale 'fichier'
fichier = ""

# Fonction de ping qui sera exécutée par chaque thread
def ping_host(host, max_retries):
    retry = 1 # Compteur de tentatives
    while retry <= max_retries:
        result = ping(host, timeout=2) # Utilise la fonction ping de la bibliothèque ping3 avec un timeout de 2 secondes
        if result is not None:
            print(f'{host} est en ligne (temps de ping : {result} ms)')
            break # Sort de la boucle si le ping est réussi
        else:
            print(f'{host} est hors ligne (tentative {retry}/{max_retries})')
            retry += 1 # Incrémente le compteur de tentatives
    else:
        print(f'{host} est toujours hors ligne après {max_retries} tentatives')

# Fonction pour choisir un fichier contenant les adresses à ping
def choisir_fichier():
    file_path = filedialog.askopenfilename()
    fichier_entry.delete(0, tk.END)
    fichier_entry.insert(tk.END, file_path)


def charger_adresses_ip(fichier):
    adresses_ip = {}
    with open(fichier, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        for ligne in reader:
            # Assurez-vous que la ligne contient au moins 2 colonnes
            if len(ligne) >= 2:
                nom, adresse_ip = ligne[0], ligne[1]
                adresse_ip = adresse_ip.strip() # Retirer les espaces en début/fin d'adresse IP
                try:
                    # Vérifier si l'adresse IP est valide
                    ipaddress.ip_address(adresse_ip)
                    adresses_ip[adresse_ip] = nom
                except ValueError:
                    print(f"Adresse IP invalide : {adresse_ip}")
    return adresses_ip

# Fonction pour démarrer le ping avec les paramètres spécifiés
def demarrer_ping():
    global fichier  # Déclarer la variable 'fichier' comme globale
    fichier = fichier_entry.get()
    limite_temps = int(limite_temps_entry.get())
    limite_temps = limite_temps * 60
    retries = int(retries_entry.get())
    sleep_time = int(sleep_time_entry.get())
    port = int(port_test_entry.get())

    try:
        # Charger les adresses IP depuis le fichier
        adresses_ip = charger_adresses_ip(fichier)
        if not adresses_ip:
            messagebox.showerror("Erreur", "Le fichier d'adresses IP est vide ou n'existe pas.")
            return
        print(adresses_ip)

        debut_temps = time.time()
        fin_temps = debut_temps + limite_temps

        while time.time() < fin_temps:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Exécuter la fonction de ping dans chaque thread
                futures = [executor.submit(ping_host, ip, retries, port, adresses_ip[ip]) for ip in adresses_ip]
                # Attendre que tous les threads aient terminé
                concurrent.futures.wait(futures)

            root.update()  # Mise à jour de l'interface utilisateur
            time.sleep(sleep_time)

        print("Limite de temps atteinte. Arrêt du ping.")
    except Exception as e:
        messagebox.showerror("Erreur", str(e))


def ping_host(ip, retries, port, nom):
    result = ping(ip, retries)
    if result:
        print(f"{ip} ({nom}) est en ligne (temps de ping : {result} ms)")
        result_ping = f"Modem en ligne - {result} ms"
    else:
        print(f"{ip} ({nom}) modem est hors ligne.")
        result_ping = "Modem hors ligne"

    # Test du port 8080 de l'automate
    try:
        with socket.create_connection((ip, port), timeout=10) as conn:
            tcp_success = "automate OK"
    except:
        tcp_success = "automate ERREUR"
    print(f"{ip} ({nom}) : {tcp_success}")

    # Obtenir la date et l'heure actuelles
    now = datetime.now()
    date_heure = now.strftime("%d/%m/%Y %H:%M:%S")

    # Obtenir le répertoire parent du chemin de fichier
    repertoire_parent = os.path.dirname(fichier)
    # Combiner le répertoire parent avec le nom de fichier pour enregistrer le fichier CSV
    fichier_log_csv = os.path.join(repertoire_parent, 'log_ping.csv')

    # Logging des résultats dans un fichier CSV
    with open(fichier_log_csv, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([date_heure, ip, nom, result_ping, tcp_success])



# Création de la fenêtre tkinter
root = tk.Tk()
root.title("Application de Ping")

# Création des widgets de la fenêtre
fichier_label = tk.Label(root, text="Fichier d'adresses à ping:")
fichier_entry = tk.Entry(root, width=40)
choisir_fichier_button = tk.Button(root, text="Choisir fichier", command=choisir_fichier)

limite_temps_label = tk.Label(root, text="Limite de temps (en mn):")
limite_temps_entry = tk.Entry(root, width=10)
limite_temps_entry.insert(0, "1")

retries_label = tk.Label(root, text="Nombre maximum de tentatives de ping:")
retries_entry = tk.Entry(root, width=10)
retries_entry.insert(0, "4")

sleep_time_label = tk.Label(root, text="Temps d'attente entre chaque ping (en secondes):")
sleep_time_entry = tk.Entry(root, width=10)
sleep_time_entry.insert(0, "5")

port_test_label = tk.Label(root, text="Test du port :")
port_test_entry = tk.Entry(root, width=10)
port_test_entry.insert(0, "8080")

demarrer_button = tk.Button(root, text="Démarrer le Ping", command=demarrer_ping)

# Placement des widgets dans la fenêtre
fichier_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
fichier_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=10)
choisir_fichier_button.grid(row=0, column=3, padx=10, pady=10)
limite_temps_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
limite_temps_entry.grid(row=1, column=1, padx=10, pady=10)
retries_label.grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
retries_entry.grid(row=2, column=1, padx=10, pady=10)
sleep_time_label.grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
sleep_time_entry.grid(row=3, column=1, padx=10, pady=10)
port_test_label.grid(row=4, column=0, sticky=tk.W, padx=10, pady=10)
port_test_entry.grid(row=4, column=1, padx=10, pady=10)
demarrer_button.grid(row=5, column=0, columnspan=4, padx=10, pady=10)

root.mainloop()