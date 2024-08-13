from flask import Flask, send_file, request, jsonify
import os
import random
import firebase_admin
from sklearn.cluster import KMeans
from firebase_admin import credentials, firestore
from datetime import date

cred = credentials.Certificate("project-skripsi-febri-firebase-adminsdk-kbykd-d38b33ac27.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# ubah isi disini
total_simulasi = 150
database = "kmeans"
# ===============

app = Flask(__name__)

kerusakan_pc = ['blue_screen', 'komponen_tidak_terdeteksi','tidak_ada_koneksi',
             'tampilan_buram','no_display','bunyi_aneh','tidak_ada_tampilan', ]
kerusakan_ac = ['tidak_dingin','bunyi_aneh',]
batas_kerusakan = 2
def randomDeadPc():
    value = random.random() * 100
    if value < 2:
        return ['mati']
    elif value > 2 and value <= 10:
        return list(set([random.choice(kerusakan_pc) for i in range(batas_kerusakan)]))
    else:
        return ['hidup']
        

@app.route("/")
def index():
    
    days = ['Sunday','Monday','Tuesday','Wednesday','Thrusday','Friday', 'Saturday']
    months = ['July', 'August', 'November', 'October', 'December']
    detail_kerusakan = ['error']
    lab = ['A', 'B', 'C', 'D', 'E']
    names = [
        'febri',
        'annisa tiara',
        'alif',
        'tika',
    ]
    
    today = date.today()
    d2 = today.strftime("%A, %d %B %Y")
    
    
    for i in range(total_simulasi):
        data = {
            f"{random.randrange(0, 23)}:{random.randrange(0, 59)}" : {
                "detail_kerusakan" : random.choice(detail_kerusakan),
                "kerusakan_komputer" : random.choice(kerusakan_pc),
                "komputer" : f"Komputer {random.randrange(1, 41)}",
                "lab" : f"Dasar {random.choice(lab)}",
                "user" : f"{random.choice(names)}",
            }
        }
        db.collection(database).document(f"{random.choice(days)}, {random.randrange(1, 31)} {random.choice(months)} 2024").set(data, merge=True)
    
    
    return jsonify({
        'status': 'success',
        'data' : data,
    })

def main():
    app.run(port=int(os.environ.get('PORT', 3000)))
if __name__ == "__main__":
    main()
# pass