from flask import Flask, render_template, request
import gspread
import time
import re
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# 🔐 Authentification via variable d’environnement
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
json_creds = os.getenv("GOOGLE_CREDENTIALS_JSON")
info = json.loads(json_creds)
creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key('1s4dLGyLKffDQoAdG-T-rGUgKr_rV2wwNpjYqhIudr3Q').worksheet('SOLDE')

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        compte = request.form.get('compte', '').strip()

        pattern = r'^[A-Za-z]{1}\d{6}-\d{2}$'
        if not re.match(pattern, compte):
            result = "❌ Format du compte invalide"
        else:
            try:
                sheet.update('A2', [[nom]])
                sheet.update('B2', [[compte]])
                result = "⏳ Solde en cours de calcul..."

                solde = None
                for i in range(5):
                    time.sleep(1.5)
                    data = sheet.get('C2')
                    if data and data[0]:
                        solde = data[0][0]
                        break

                if solde:
                    result = f"✅ Solde du membre {nom} : {solde}"
                else:
                    result = "⚠️ Solde non disponible ou formule vide"
            except Exception as e:
                result = f"❌ Erreur : {str(e)}"

    return render_template('index.html', result=result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
