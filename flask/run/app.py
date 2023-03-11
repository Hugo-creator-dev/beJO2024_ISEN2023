from flask import Flask, request, jsonify, g
import sqlite3
import time
from prometheus_flask_exporter import PrometheusMetrics
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import requests
import json
from flask_oidc import OpenIDConnect
from threading import Thread

app = Flask(__name__)
metrics = PrometheusMetrics(app)
info = metrics.info('Score', 'Last score added')

load_dotenv()
MAIL_ADDRESS = os.getenv('MAIL_ADRESS')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_PORT = os.getenv('MAIL_PORT')
MAIL_SERVER = os.getenv('MAIL_SERVER')
URL_IA = os.getenv('URL_IA')

app.config.update({
    'SECRET_KEY':  os.getenv('SECRET_PASSWORD'),
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_RESOURCE_SERVER_ONLY': True ,
    'OIDC_TOKEN_TYPE_HINT':'access_token',
    'OIDC_INTROSPECTION_AUTH_METHOD':'client_secret_post',
    'OIDC_SCOPES':'openid profile',
})
oidc = OpenIDConnect(app)

def select(Table,Athlete_sub):
    Athlete_ID = Athlete_sub
    conn = sqlite3.connect('../storage/database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM "+Table+" WHERE Athlete_ID = ?",(Athlete_ID,))
    data = c.fetchall()
    conn.close()
    return data

def format_return(code=0,message='',data=None):
    return jsonify({'code':code,'message': message,'data': data})


@app.route('/identity', methods=['POST'])
@oidc.accept_token(require_token=True)
def identity():
    Athlete_ID = g.oidc_token_info['sub']

    Sport = request.json['Sport']
    Birth_Date = request.json['Birth_Date']
    Sex = request.json['Sex']
    Taille = request.json['Taille']

    conn = sqlite3.connect('../storage/database.db')
    c = conn.cursor()
    c.execute("INSERT INTO Identity (Athlete_ID, Sport, Birth_Date, Sex, Taille) VALUES (?, ?, ?, ?, ?)", (Athlete_ID, Sport, Birth_Date, Sex, Taille))
    conn.commit()
    conn.close()

    metrics.counter('users_added', 'Nombre d\'utilisateurs ajoutés à la base de données')

    return format_return(message='Les données de l\'utilisateur ont bien été ajoutées')

@app.route('/identity', methods=['GET'])
@oidc.accept_token(require_token=True)
def get_identity():
    return format_return(data=select("Identity",g.oidc_token_info['sub']))

""" @app.route('/sport', methods=['POST'])
@oidc.accept_token(require_token=True)
def sport():
    Athlete_ID = g.oidc_token_info['sub']

    Date_of_last_competition = request.json['Date_of_last_competition']
    Date_of_last_training = request.json['Date_of_last_training']
    Muscle_used_in_the_last_workout = request.json['Muscle_used_in_the_last_workout']
    Recovery_status = request.json['Recovery_status']
    frequence_training_week = request.json['frequence_training_week']

    conn = sqlite3.connect('../storage/database.db')
    c = conn.cursor()
    c.execute("INSERT INTO Sport (Athlete_ID, Date_of_last_competition, Date_of_last_training, Muscle_used_in_the_last_workout, Recovery_status, frequence_training_week) VALUES (?, ?, ?, ?, ?, ?)", (Athlete_ID, Date_of_last_competition, Date_of_last_training, Muscle_used_in_the_last_workout, Recovery_status, frequence_training_week))
    conn.commit()
    conn.close()

    metrics.counter('sport_added', 'Nombre de\'sport ajoutés à la base de données', labels={'Sport': Date_of_last_competition})

    return format_return(message='Les données du Sport ont bien été ajoutées')


@app.route('/sport', methods=['GET'])
@oidc.accept_token(require_token=True)
def get_sport():
    return format_return(data=select("Sport",g.oidc_token_info['sub'])) """



# Injuries
@app.route('/injuries', methods=['POST'])
@oidc.accept_token(require_token=True)
def injuries():
    Athlete_ID = g.oidc_token_info['sub']

    Date = request.json['Date']
    Position = request.json['Position']
    Intensity = request.json['Intensity']
    Injury_status = request.json['Injury_status']

    conn = sqlite3.connect('../storage/database.db')
    c = conn.cursor()
    c.execute("INSERT INTO Injuries (Athlete_ID, Date, Position, Intensity, Injury_status) VALUES (?, ?, ?, ?, ?)", (Athlete_ID, Date, Position, Intensity, Injury_status))
    conn.commit()
    conn.close()

    return format_return(message='Les données concernant la dernière blessure ont bien été ajoutées')

@app.route('/injuries', methods=['GET'])
@oidc.accept_token(require_token=True)
def get_injuries():
    return format_return(data=select("Injuries",g.oidc_token_info['sub']))

#Training Stat
@app.route('/trainingstat', methods=['POST'])
@oidc.accept_token(require_token=True)
def trainingstat():
    Athlete_ID = g.oidc_token_info['sub']

    Title = request.json['Title']
    Description = request.json['Description']
    Date = request.json['Date']
    Duration_time = request.json['Duration_time']
    Intensity_of_last_training = request.json['Intensity_of_last_training']

    conn = sqlite3.connect('../storage/database.db')
    c = conn.cursor()
    c.execute("INSERT INTO Training_stat (Athlete_ID, Title, Description, Date, Duration_time, Intensity_of_last_training) VALUES (?, ?, ?, ?, ?, ?)", (Athlete_ID, Title, Description, Date, Duration_time, Intensity_of_last_training))
    conn.commit()
    conn.close()

    return format_return(message='Les données concernant le dernier entrainement ont bien été ajoutées')


@app.route('/trainingstat', methods=['GET'])
@oidc.accept_token(require_token=True)
def get_trainingstat():
    return format_return(data=select("Training_stat",g.oidc_token_info['sub']))


@app.route('/selfeval', methods=['POST'])
@oidc.accept_token(require_token=True)
def selfeval():
    Athlete_ID = g.oidc_token_info['sub']

    Sleep = request.json['Sleep']
    General_tiredness = request.json['General_tiredness']
    Aches_pains = request.json['Aches_pains']
    Mood_stress = request.json['Mood_stress']
    Weight = request.json['Weight']
    Date = time.strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect('../storage/database.db')
    c = conn.cursor()
    c.execute("INSERT INTO Self_evaluation (Athlete_ID, Sleep, General_tiredness, Aches_pains, Mood_stress, Weight, Date) VALUES (?, ?, ?, ?, ?, ?, ?)", (Athlete_ID, Sleep, General_tiredness, Aches_pains, Mood_stress, Weight, Date))
    conn.commit()
    
    try: 
        c.execute("SELECT * FROM Identity WHERE Athlete_ID = ?", (Athlete_ID,))
        Identityjson = c.fetchone()
        columns = [col[0] for col in c.description]
        IdentityDict = dict(zip(columns, Identityjson))
        Identityout = json.dumps(IdentityDict)

        '''c.execute("SELECT * FROM Sport WHERE Athlete_ID = ?", (Athlete_ID))
        Sportjson = c.fetchone()
        columns = [col[0] for col in c.description]
        SportDict = dict(zip(columns, Sportjson))
        Sportout = json.dumps(SportDict)'''

        c.execute("SELECT * FROM Self_evaluation WHERE Athlete_ID = ? ORDER BY Date DESC LIMIT 1;", (Athlete_ID,))
        Self_evaluationjson = c.fetchone()
        columns = [col[0] for col in c.description]
        Self_evaluationDict = dict(zip(columns, Self_evaluationjson))
        Self_evaluationout = json.dumps(Self_evaluationDict)

        c.execute("SELECT * FROM Injuries WHERE Athlete_ID = ?", (Athlete_ID,))
        Injuriesjson = c.fetchone()
        columns = [col[0] for col in c.description]
        InjuriesDict = dict(zip(columns, Injuriesjson))
        Injuriesout = json.dumps(InjuriesDict)
  
        c.execute("SELECT * FROM Training_stat WHERE Athlete_ID = ?", (Athlete_ID,))
        Training_statjson = c.fetchone()
        columns = [col[0] for col in c.description]
        Training_statDict = dict(zip(columns, Training_statjson))
        Training_statout = json.dumps(Training_statDict)
        conn.commit()
    
    except:
        return format_return(code=1,message='Une erreur c\'est porduite, veuillez remplire toutes les autres évalutions avant celle-ci')
    
    conn.close()
    
    json_data = [{
    "Identity":Identityout,
    #"Sport":Sportout,
    "Self_evaluation":Self_evaluationout,
    "Injuries":Injuriesout,
    "Training_stat":Training_statout
    }]

    Thread(target=score,args=(Athlete_ID,json_data,g.oidc_token_info['given_name'],g.oidc_token_info['family_name'])).start()

    return format_return(message='Les données de votre auto-évaluation ont bien été enregistrées, votre score vas etre mis à jour')

@app.route('/selfeval', methods=['GET'])
@oidc.accept_token(require_token=True)
def get_selfeval():
    return format_return(data=select("Self_evaluation",g.oidc_token_info['sub']))

@app.route('/staff', methods=['POST'])
@oidc.accept_token(require_token=True)
def staff():
    Athlete_ID = g.oidc_token_info['sub']

    Name = request.json['Name']
    FamilyName = request.json['FamilyName']
    Speciality = request.json['Speciality']
    Phone_number = request.json['Phone_number']
    email = request.json['email']

    conn = sqlite3.connect('../storage/database.db')
    c = conn.cursor()
    c.execute("INSERT INTO Staff (Name, FamilyName, Speciality, Phone_number, email, Athlete_ID) VALUES (?, ?, ?, ?, ?, ?)", (Name, FamilyName, Speciality, Phone_number, email, Athlete_ID))
    conn.commit()
    conn.close()
    return format_return(message='Les données du staff ont bien été ajoutées')

@app.route('/staff', methods=['GET'])
@oidc.accept_token(require_token=True)
def get_staff():
    return format_return(data=select("Staff",g.oidc_token_info['sub']))

#ADVICE
@app.route('/advice', methods=['POST'])
def advice():
    titre = request.json['titre']
    description = request.json['description']
    conn = sqlite3.connect('../storage/database.db')
    c = conn.cursor()
    c.execute("INSERT INTO Advice (titre, description) VALUES (?, ?)", (titre, description))
    conn.commit()
    conn.close()
    return format_return(message='Le conseil '+ titre + ' a bien été ajoutées')


@app.route('/advice', methods=['GET'])
def get_advice():
    conn = sqlite3.connect('../storage/database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Advice")
    Advice = c.fetchall()
    conn.close()
    return format_return(data=Advice)


def score(Athlete_ID,json_data,prenom,nom):
    response = requests.post(url=URL_IA, json=json_data, headers={'Content-type': 'application/json'})

    if response.status_code != 200 or response.json()['code'] < 0:
        return -2

    Score = response.json()['data']

    Date = time.strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect('../storage/database.db')
    c = conn.cursor()
    c.execute("INSERT INTO Score (Athlete_ID, Score, Date) VALUES (?, ?, ?)", (Athlete_ID, Score, Date))
    conn.commit()
    c.execute("SELECT Score FROM Score ORDER BY Date DESC LIMIT 1")
    last_score = c.fetchone()[0]
    c.execute("SELECT email FROM Staff WHERE Athlete_ID = ?", (Athlete_ID,))
    email = c.fetchone()[0]


    last_score_entier = int(last_score)
    conn.close()

    info.set(last_score)
    #Si le score est supérieur à 5 alors envoie de mail
    if last_score_entier > 4:
        try:
                # Définir les détails du message
            msg = MIMEMultipart()
            msg['From'] = MAIL_ADDRESS
            msg['To'] = email
            msg['Subject'] = 'Attention ! Votre sportif vient d\'atteindre une valeur de fatigue critique !'

            # Définition du style CSS dans l'en-tête du message
            html = """
                <html>
                    <head>
                        <style>
                            p {{
                                font-size: 20pt;
                            }}
                            span {{
                                color: red;
                                font-size: 20pt;
                            }}
                        </style>
                    </head>
                    <body>
                        <p>Bonjour,</p>
                        <p>Nous avons estimé que le sportif <span>{} {}</span> a atteint une valeur critique de fatigue.</p>
                        <p>Cette valeur est de <span>{}</span>/10.</p>
                        <p>Veuillez prendre les mesures nécessaires pour éviter toutes blessures.</p>
                    </body>
                </html>
            """.format(prenom, nom, str(last_score_entier))

            msg.attach(MIMEText(html, 'html'))

            
            server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
            server.starttls()
            server.login(MAIL_ADDRESS, MAIL_PASSWORD)
            server.sendmail(MAIL_ADDRESS, email, msg.as_string())
            server.quit()
            return 1
        except:
            return -1
    return 0


@app.route('/score', methods=['GET'])
@oidc.accept_token(require_token=True)
def get_score():
    return format_return(data=select("Score",g.oidc_token_info['sub']))

if __name__ == '__main__':
    if os.path.exists('../storage/database.db') == False :
        connection = sqlite3.connect('../storage/database.db')
        with open('schema.sql') as f:
            connection.executescript(f.read())
        cur = connection.cursor()
        connection.commit()
        connection.close()
    app.run('0.0.0.0',8443,ssl_context=('../certificate/cert.pem', '../certificate/key.pem'))
