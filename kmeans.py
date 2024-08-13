from flask import Flask, send_file, request, jsonify # Import web service
import os
import random
import firebase_admin # Import library firebase python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from firebase_admin import credentials, firestore
from datetime import date 
import json # Import library JSON untuk mengelola JSON
import matplotlib.pyplot as plt
import pandas as pd # Import library pandas untuk mengelola data

# Menjalankan Web Service
app = Flask(__name__)

# Membuka file akses kunci firebase
cred = credentials.Certificate("key.json")
# Mengambil akses ke firebase database firestore
firebase_admin.initialize_app(cred)
# Mengakses firestore dari firebase ke dalam bentuk client
db = firestore.client()

# Menginisialisasikan nilai-nilai variabel ke dalam bentuk angka
variable_kerusakan = {
    "mati": 10,
    "hidup": 1,
    "blue_screen": 9,
    "komponen_tidak_terdeteksi": 4,
    "tidak_ada_koneksi": 3,
    "tampilan_buram": 5,
    "no_display": 8,
    "bunyi_aneh": 2,
    "tidak_ada_tampilan": 7,
    "tidak_dingin": 6,
    "tidak_ada_kerusakan": 0,
}

# Menukar key-value pada variabel "variable_kerusakan"
swapped_variable_kerusakan = {value : key for key, value in variable_kerusakan.items()}

### Hyperparameters variabel untuk K-Means ###
# Menentukan banyak label
n_features = 2
# Menentukan nilai tengah dalam K-Means
centers = 2
##############################################

# Mengakses firestore database "kmeans" di dalam database firebase dengan metode stream
documents = db.collection("kmeans").stream()

data = []
data_without_time = []

for doc in documents:
    data.append(doc.to_dict())
    data_without_time.append(doc.to_dict()[list(doc.to_dict().keys())[0]])

pd_data = pd.DataFrame({
    "detail_kerusakan": [i['detail_kerusakan'] for i in data_without_time],
    "user": [i['user'] for i in data_without_time],
    "komputer": [i['komputer'] for i in data_without_time],
    "lab": [i['lab'] for i in data_without_time],
    "kerusakan_komputer": [i['kerusakan_komputer'] for i in data_without_time],
    "nilai_kerusakan": [variable_kerusakan[i['kerusakan_komputer']] for i in data_without_time],
})

# Menginisialisasikan data untuk di latih pada model K-Means
x = [[i] for i in list(pd_data['nilai_kerusakan'])]

# Menginisialisasikan model K-Means
kmeans = KMeans(n_clusters=centers, random_state=42)

# Melatih model K-Means
kmeans.fit(x)

@app.route("/")
def Home():
    return jsonify({
        "message": "API Berhasil Berjalan"
    })

@app.route('/riwayat_kerusakan', methods=['GET'])
def AmbilData():
    # Mengambil semua dokumen dari koleksi "laporanlab" di database.
    documents = db.collection("laporanlab").stream()

    # Membuat daftar kosong untuk menyimpan data dari dokumen yang diambil.
    data = []

    # Membuat daftar kosong untuk menyimpan data kerusakan ringan dan berat.
    kerusakan_ringan = []
    kerusakan_berat = []

    # Loop untuk memproses setiap dokumen yang diambil dari koleksi "laporanlab".
    for doc in documents:
        # Menyimpan data dokumen dalam bentuk dictionary dan menambahkan waktu/dokumen ID ke dalam 'data'.
        data.append({
            'doc': doc.to_dict(),
            'time': doc.id
        })

    # Loop untuk mengubah nilai kerusakan_komputer dari dokumen berdasarkan nilai yang ada di variable_kerusakan.
    for i in data:
        for j in i['doc']:
            # Mengganti nilai 'kerusakan_komputer' di setiap entry dokumen dengan nilai yang sesuai dari variable_kerusakan.
            i['doc'][j]['kerusakan_komputer'] = variable_kerusakan[i['doc'][j]['kerusakan_komputer']]

    # Loop untuk memprediksi kategori kerusakan (ringan/berat) berdasarkan model KMeans dan mengkategorikan data.
    for i in data:
        for j in i['doc']:
            # Menggunakan model KMeans untuk memprediksi apakah kerusakan komputer adalah ringan atau berat.
            result = kmeans.predict([[i['doc'][j]['kerusakan_komputer']]])
            
            # Jika hasil prediksi adalah kategori 'ringan' (diasumsikan hasil prediksi '1' adalah ringan),
            # maka data tersebut dimasukkan ke dalam daftar kerusakan_ringan.
            if result[0] == 1:
                kerusakan_ringan.append({
                    "time": j,
                    "data": i['doc'][j],
                    "tanggal": i['time'],
                })
            # Jika hasil prediksi bukan kategori 'ringan', maka dianggap sebagai kerusakan berat dan
            # data tersebut dimasukkan ke dalam daftar kerusakan_berat.
            else:
                kerusakan_berat.append({
                    "time": j,
                    "data": i['doc'][j],
                    "tanggal": i['time'],
                })

    # Loop untuk mengembalikan nilai kerusakan_komputer di daftar kerusakan_ringan ke nilai awalnya
    # berdasarkan nilai yang ada di swapped_variable_kerusakan.
    for i in kerusakan_ringan:
        i["data"]['kerusakan_komputer'] = swapped_variable_kerusakan[i["data"]['kerusakan_komputer']]

    # Loop untuk mengembalikan nilai kerusakan_komputer di daftar kerusakan_berat ke nilai awalnya
    # berdasarkan nilai yang ada di swapped_variable_kerusakan.
    for i in kerusakan_berat:
        i["data"]['kerusakan_komputer'] = swapped_variable_kerusakan[i["data"]['kerusakan_komputer']]

    # Mengembalikan hasil akhir dalam bentuk JSON yang terdiri dari kategori kerusakan komputer,
    # yaitu kerusakan berat dan kerusakan ringan.
    return jsonify({
        "kategori_kerusakan": {
            "kerusakan_berat": kerusakan_berat,
            "kerusakan_ringan": kerusakan_ringan,
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
    
    # with open('./model_kmeans.pkl', 'wb') as f:
    #     pickle.dump(kmeans, f)
    
    # # Print the cluster centers
    # print("Cluster centers:")
    # print(kmeans.cluster_centers_)
    # # Print the inertia (sum of squared distances to the closest cluster center)
    # print("Inertia:", kmeans.inertia_)
    
    # # print(x)
    # y_kmeans = kmeans.predict(x)
    # plt.figure(figsize=(10, 6))
    # plt.scatter(x[:, 0], x[:, 0], s=50, cmap='viridis')
    # plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 0], s=300, c='red', marker='x')
    # plt.title("K-means Clustering")
    # plt.xlabel("Feature 1")
    # # plt.ylabel("Feature 2")
    # plt.show()