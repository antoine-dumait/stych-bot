import creds
import json
import re
import requests
import datetime


def fetch_courses():
  planning_url = "http://www.stych.fr/elearning/planning-conduite/get-planning-proposition"

  cookies = {"remember_me" : creds.remember_me}
  resp = requests.get(planning_url, cookies=cookies)

  mentions = "@everyone"

  maxLogLine = 288 #60*24/5 number of 5 min per day

  myMoniteur = open("moniteur.txt", "r").read().split("\n")

  creneaux = re.search(r'"rowsProposition":(\[.*\]),"rowsMoniteur"', resp.text)
  creneaux = json.loads(creneaux.group(1))
  if myMoniteur:
    creneaux = [[d['info_date'], d['heure_debut'], d['heure_fin'], d['moniteur'], d['id_jour'], d['id_lac']] for d in creneaux if d['moniteur'] in myMoniteur]
  else:
    creneaux = [[d['info_date'], d['heure_debut'], d['heure_fin'], d['moniteur'], d['id_jour'], d['id_lac']] for d in creneaux]
  #           date, debut, fin, moniteur, jour, lieu
  #             0     1     2      3        4     5   
  lieux = re.search(r'"rowsPointDeCours":(\[.*\]),"rowsProposition"', resp.text)
  lieux = json.loads(lieux.group(1))
  lieux = {d['id_liste_adresse_cours']: d['adresse'] for d in lieux}

  with open("creneaux.txt", "r", encoding='utf-8') as f:
      old_creneaux = f.read()
      if not old_creneaux: 
        old_creneaux = "[]"
      old_creneaux = json.loads(old_creneaux)

  new_creneaux = [c for c in creneaux if c[:-2] not in old_creneaux]

  with open("log.txt", "r", encoding='utf-8') as f:
    log = f.read().split("\n")

  with open("log.txt", "w", encoding='utf-8') as f:
    f.write(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S") + f" - {len(creneaux)}\n")
    for line in log[-maxLogLine+1:-1]:
      f.write(line + "\n")
    f.write(log[-1])

  if len(new_creneaux) > 0:
    print('NEW COURSES FOUND !')
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    mois = ["Janvier", u"Février", "Mars", "Avril", "Mai", "Juin", "Juillet", u"Août", "Septembre", "Octobre", "Novembre", u"Décembre"]
    
    embeds = []
    for c in new_creneaux:
      jour = jours[int(c[4])]
      heure = c[1][:-3] + " - " + c[2][:-3]
      date = c[0][-2:]
      date_mois = mois[int(c[0][5:6])]
      moniteur = c[3]
      lieu = lieux[c[5]]
      embeds.add({
          "type": "rich",
          "title": f"{jour} {date} {date_mois} - {moniteur} - {lieu}",
          "description": "Nouveau cours de conduite disponible !",
          "color": 0x3366FF,
          "fields": [
              {
              "name": f"Date : **{jour} {date} {date_mois}**",
              "value": "\u200B"
              },
              {
              "name": f"Heure : **{heure}**",
              "value": "\u200B"
              },
              {
              "name": f"Moniteur : **{moniteur}**",
              "value": "\u200B"
              },
              {
              "name": f"Lieu : **{lieu}**",
              "value": "\u200B"
              }
          ],
          "thumbnail": {
              "url": "https://play-lh.googleusercontent.com/izcUVe4M3xRZLj6v-BOPIqgNrPw_NV6WY4Kh1GHOug5LXDi-yF02WBBFaxlNmyQ0VIk=w240-h480-rw",
              "height": 0,
              "width": 0
          },
          "author": {
              "name": "Stych",
              "url": "https://www.stych.fr/elearning/formation-home"
          },
          "url": "https://www.stych.fr/elearning/formation/conduite/reservation/planning"
        })

    webhook_data = {
      "content": mentions,
      "embeds": embeds,
      "username": "Stych",
      "avatar_url": "https://play-lh.googleusercontent.com/izcUVe4M3xRZLj6v-BOPIqgNrPw_NV6WY4Kh1GHOug5LXDi-yF02WBBFaxlNmyQ0VIk",
      "attachments": []
    }

    rest = requests.post(creds.webhooks_url, json=webhook_data)
    print(rest.status_code)

  with open("creneaux.txt", "w", encoding='utf-8') as f:
      f.write(json.dumps([c[:-2] for c in creneaux], ensure_ascii=False))
