from flask import Flask, render_template, request, url_for, redirect, session
from flask_cors import CORS
import pymysql
import json
import bcrypt


app = Flask(__name__)
app.secret_key = "^A%DJAJU^JJ123" #app secret untuk bcrypt, sifatnya rahasia, boleh diisi apa saja

# CORS untuk permission AJAX / API
CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             db='simulasi_cpns',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

@app.route('/generateDB')
def generateDB():

    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users
         (id            INT AUTO_INCREMENT PRIMARY KEY,
         name           VARCHAR(255)             NOT NULL,
         email          VARCHAR(255)   UNIQUE    NOT NULL,
         password       VARCHAR(255)             NOT NULL,
         role           VARCHAR(255)             NOT NULL
         );''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS simulasi
         (id              INT AUTO_INCREMENT PRIMARY KEY,
         nama_simulasi    VARCHAR(255)    NOT NULL,
         sampul           VARCHAR(255)    NULL,
         bgHome           VARCHAR(255)    NULL,
         durasi           INT             NOT NULL,
         panduan          TEXT            NULL,
         bgPanduan        VARCHAR(255)    NULL,
         bgPertanyaan     VARCHAR(255)    NULL
         );''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS paket
         (id           INT AUTO_INCREMENT PRIMARY KEY,
         nama_paket    VARCHAR(255)    NOT NULL);''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS tipe_soal
         (id           INT AUTO_INCREMENT PRIMARY KEY,
         nama_tipe     VARCHAR(255)    NOT NULL);''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS soal
         (id               INT AUTO_INCREMENT PRIMARY KEY,
         pertanyaan_text   VARCHAR(255)    NULL,
         pertanyaan_img    VARCHAR(255)    NULL,
         id_paket          INT             NOT NULL,
         id_tipe           INT             NOT NULL,
         nomor_soal        INT             NOT NULL
         );''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS soal_opsi
         (id         INT AUTO_INCREMENT PRIMARY KEY,
         opsi_text   VARCHAR(255)    NULL,
         opsi_img    VARCHAR(255)    NULL,
         poin        INT             NOT NULL,
         id_soal     INT             NOT NULL
         );''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS simulasi_paket
         (id           INT AUTO_INCREMENT PRIMARY KEY,
         id_paket      INT    NOT NULL,
         id_simulasi   INT    NOT NULL
         );''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS riwayat_simulasi
         (id                    INT AUTO_INCREMENT PRIMARY KEY,
         id_user                INT             NOT NULL,
         id_simulasi_paket      INT             NOT NULL,
         id_paket               INT             NOT NULL,
         nilai                  INT             NULL,
         nama_paket             VARCHAR(255)    NULL,
         mulai                  VARCHAR(50)     NULL,
         selesai                VARCHAR(50)     NULL
         );''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS jawaban_riwayat_simulasi
         (id                    INT AUTO_INCREMENT PRIMARY KEY,
         id_user                INT             NOT NULL,
         id_riwayat             INT             NOT NULL,
         id_simulasi_paket      INT             NOT NULL,
         id_tipe                INT             NULL,
         id_soal                INT             NOT NULL,
         id_opsi_jawab          INT             NOT NULL,
         poin                   INT             NULL
         );''')

    cursor.close()

    # Cek apakah user dengan email tersebut sudah ada
    cursor = connection.cursor()
    default_admin_email = 'admin@gmail.com'
    cursor.execute(
        "SELECT count(email) as total FROM users WHERE email=%s", [default_admin_email])
    user = cursor.fetchone()
    cursor.close()

    if int(user['total']) == 0:
        # Buat User default untuk admin
        cursor = connection.cursor()
        password = 'admin'
        password_encode = password.encode('utf-8')
        hash_password = bcrypt.hashpw(password_encode, bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO users (name,email,password,role) VALUES ('Admin',%s,%s,'admin')", [default_admin_email, hash_password])
        connection.commit()
        cursor.close()

    return redirect(url_for('home'))

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        # Cek apakah user dengan email tersebut sudah ada
        cursor = connection.cursor()
        cursor.execute(
            "SELECT count(email) as total FROM users WHERE email=%s", [email])
        user = cursor.fetchone()
        cursor.close()

        if int(user['total']) > 0:

            # Dapatkan user sesuai dengan email yang terdaftar
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()
            cursor.close()

            # cek password menggunakan bcrypt
            if bcrypt.hashpw(password, user["password"].encode('utf-8')) == user["password"].encode('utf-8'):
                session['id_user'] = user['id']
                session['name'] = user['name']
                session['role'] = user['role']
                session['email'] = user['email']
                
                return render_template("home.html")
            else:
                return "Error password and email not match"
        else:
            return "Error user not found"
    else:
        return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        # Cek apakah user dengan email tersebut sudah ada
        cursor = connection.cursor()
        cursor.execute("SELECT count(email) as total FROM users WHERE email=%s", [email])
        user = cursor.fetchone()
        cursor.close()

        if int(user['total']) > 0:
            return "Gagal ditambahkan. User sudah ada"
        else:

            # Tambahkan user ke database
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (name, email, password, role) VALUES (%s,%s,%s,%s)",
                        [name, email, hash_password, 'student'])
            connection.commit()
            cursor.close()

            # Dapatkan pengguna dari email
            cursor = connection.cursor()
            cursor.execute(
                "SELECT count(email) as total FROM users WHERE email=%s", [email])
            user = cursor.fetchone()
            cursor.close()

            session['id_user'] = user['id']
            session['name'] = user['name']
            session['role'] = user['role']
            session['email'] = user['email']

            return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return render_template("home.html")

# --------------------------------------- UNTUK ADMIN -------------------------------------
@app.route('/data-tipe')
def dataTipe():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tipe_soal")
    tipe = cursor.fetchall()
    cursor.close()
    return render_template('data-tipe.html', tipe=tipe)

@app.route('/data-tipe/add', methods=["POST"])
def addTipe():
    nama_tipe = request.form['nama_tipe']

    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO tipe_soal (nama_tipe) VALUES (%s)", [nama_tipe])
    connection.commit()
    cursor.close()
    return redirect(url_for('dataTipe'))

@app.route('/data-tipe/update', methods=["POST"])
def updateTipe():
    nama_tipe = request.form['nama_tipe']
    id = request.form['id']
    
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE tipe_soal SET nama_tipe=%s WHERE id=%s", [nama_tipe, int(id)])
    connection.commit()
    cursor.close()
    return redirect(url_for('dataTipe'))

@app.route('/data-tipe/delete/<string:id>')
def deleteTipe(id):
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM tipe_soal WHERE id=%s", [id])
    connection.commit()

    cursor.execute(
        "DELETE FROM soal WHERE id_tipe=%s", [id])
    connection.commit()

    cursor.close()
    return redirect(url_for('dataTipe'))

@app.route('/data-paket')
def dataPaket():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM paket")
    pakets = cursor.fetchall()
    cursor.close()
    return render_template('paket/data-paket.html', pakets=pakets)

@app.route('/data-paket/add', methods=["POST"])
def addPaket():
    nama_paket = request.form['nama_paket']
    
    cursor = connection.cursor()
    cursor.execute(
            "INSERT INTO paket (nama_paket) VALUES (%s)", [nama_paket])
    connection.commit()
    cursor.close()
    return redirect(url_for('dataPaket'))

@app.route('/data-paket/update', methods=["POST"])
def updatePaket():
    nama_paket = request.form['nama_paket']
    id = request.form['id']
    
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE paket SET nama_paket=%s WHERE id=%s", [nama_paket,id])
    connection.commit()
    cursor.close()
    return redirect(url_for('dataPaket'))

@app.route('/data-paket/delete/<string:id>')
def deletePaket(id):
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM paket WHERE id=%s", [id])
    connection.commit()

    cursor.execute(
        "DELETE FROM soal WHERE id_paket=%s", [id])
    connection.commit()

    cursor.close()
    return redirect(url_for('dataPaket'))

@app.route('/data-paket/soal/add', methods=["POST"])
def addSoal():
    id_paket = request.form['id_paket']
    id_tipe = request.form['id_tipe']
    nomor_soal = request.form['nomor_soal']
    pertanyaan_text = request.form['pertanyaan_text']
    opsi_text1 = request.form['opsi_text1']
    poin1 = request.form['poin1']
    opsi_text2 = request.form['opsi_text2']
    poin2 = request.form['poin2']
    opsi_text3 = request.form['opsi_text3']
    poin3 = request.form['poin3']
    opsi_text4 = request.form['opsi_text4']
    poin4 = request.form['poin4']
    opsi_text5 = request.form['opsi_text5']
    poin5 = request.form['poin5']
    
    cursor = connection.cursor()
    insertSoal = cursor.execute(
        "INSERT INTO soal(pertanyaan_text,id_paket,id_tipe,nomor_soal) VALUES(%s,%s,%s,%s)", [pertanyaan_text, id_paket, id_tipe, nomor_soal])
    connection.commit()
    id_soal = cursor.lastrowid
    print("id soal: "+str(id_soal))
    
    insertOpsi = cursor.execute(
        "INSERT INTO soal_opsi(opsi_text,poin,id_soal) VALUES(%s,%s,%s),(%s,%s,%s),(%s,%s,%s),(%s,%s,%s),(%s,%s,%s)", [opsi_text1, poin1, id_soal, opsi_text2, poin2, id_soal, opsi_text3, poin3, id_soal, opsi_text4, poin4, id_soal, opsi_text5, poin5, id_soal])
    connection.commit()

    cursor.close()
    return redirect(url_for('detailPaket',id=id_paket))

@app.route('/data-paket/soal/update', methods=["POST"])
def updateSoal():
    id_paket = request.form['id_paket']
    id_soal = request.form['id_soal']
    id_tipe = request.form['id_tipe']
    nomor_soal = request.form['nomor_soal']
    pertanyaan_text = request.form['pertanyaan_text']
    opsi_text1 = request.form['opsi_text1']
    id_opsi1 = request.form['id_opsi1']
    poin1 = request.form['poin1']

    opsi_text2 = request.form['opsi_text2']
    poin2 = request.form['poin2']
    id_opsi2 = request.form['id_opsi2']

    opsi_text3 = request.form['opsi_text3']
    poin3 = request.form['poin3']
    id_opsi3 = request.form['id_opsi3']

    opsi_text4 = request.form['opsi_text4']
    poin4 = request.form['poin4']
    id_opsi4 = request.form['id_opsi4']

    opsi_text5 = request.form['opsi_text5']
    poin5 = request.form['poin5']
    id_opsi5 = request.form['id_opsi5']
    
    cursor = connection.cursor()
    insertSoal = cursor.execute(
        "UPDATE soal SET pertanyaan_text=%s, id_paket=%s, id_tipe=%s, nomor_soal=%s WHERE id=%s", [pertanyaan_text, id_paket, id_tipe, nomor_soal,id_soal])
    connection.commit()

    updateOpsi = cursor.execute(
        "UPDATE soal_opsi SET opsi_text=%s, poin=%s, id_soal=%s WHERE id=%s", [opsi_text1, poin1, id_soal, id_opsi1])
    connection.commit()

    updateOpsi = cursor.execute(
        "UPDATE soal_opsi SET opsi_text=%s, poin=%s, id_soal=%s WHERE id=%s", [opsi_text2, poin2, id_soal, id_opsi2])
    connection.commit()

    updateOpsi = cursor.execute(
        "UPDATE soal_opsi SET opsi_text=%s, poin=%s, id_soal=%s WHERE id=%s", [opsi_text3, poin3, id_soal, id_opsi3])
    connection.commit()

    updateOpsi = cursor.execute(
        "UPDATE soal_opsi SET opsi_text=%s, poin=%s, id_soal=%s WHERE id=%s", [opsi_text4, poin4, id_soal, id_opsi4])
    connection.commit()

    updateOpsi = cursor.execute(
        "UPDATE soal_opsi SET opsi_text=%s, poin=%s, id_soal=%s WHERE id=%s", [opsi_text5, poin5, id_soal, id_opsi5])
    connection.commit()

    cursor.close()
    return redirect(url_for('detailPaket', id=id_paket))

@app.route('/data-paket/soal/del/<string:idPaket>/<string:idSoal>')
def delSoal(idPaket,idSoal):
    cursor = connection.cursor()
    delSoal = cursor.execute(
        "DELETE FROM soal WHERE id=%s", [idSoal])
    connection.commit()
    delOpsi = cursor.execute(
        "DELETE FROM soal_opsi WHERE id_soal=%s", [idSoal])
    connection.commit()
    cursor.close()
    return redirect(url_for('detailPaket', id=idPaket))

@app.route('/data-paket/<string:id>')
def detailPaket(id):
    cursor = connection.cursor()

    resultTipe = cursor.execute("SELECT * FROM tipe_soal")
    tipe = cursor.fetchall()

    resultPaket = cursor.execute("SELECT * FROM paket WHERE id="+id)
    paket = cursor.fetchone()

    resultSoal = cursor.execute(
        "SELECT sl.id,sl.pertanyaan_text,sl.id_paket,sl.id_tipe,sl.nomor_soal,ts.nama_tipe FROM soal as sl INNER JOIN tipe_soal as ts WHERE sl.id_tipe=ts.id AND id_paket=%s ORDER BY nomor_soal ASC", (id))
    soals = cursor.fetchall()

    cursor.close()
    total = len(soals)
    # print(json.dumps(soals))
    return render_template('paket/detail-paket.html', paket=paket, soals=soals, tipe=tipe, total=total)

@app.route('/ajax/soal/opsi/<string:id>')
def ajaxSoalOpsi(id):
    cursor = connection.cursor()
    result = cursor.execute(
        "SELECT * FROM soal_opsi WHERE id_soal=%s",[id])
    opsi = cursor.fetchall()
    cursor.close()
    return json.dumps(opsi)

@app.route('/ajax/paket/search/<string:keyword>')
def ajaxPaketSearch(keyword):
    cursor = connection.cursor()
    result = cursor.execute(
        "SELECT * FROM paket WHERE nama_paket LIKE '%"+keyword+"%'")
    simulasis = cursor.fetchall()
    cursor.close()
    return json.dumps(simulasis)

@app.route('/ajax/paket-simulasi/add', methods=["POST"])
def ajaxPaketAddToSimulasi():
    id_simulasi = request.form['id_simulasi']
    id_paket = request.form['id_paket']
    print("Id Paket : ",id_paket)
    print("Id Simulasi : ",id_simulasi)
    
    cursor = connection.cursor()
    cek = cursor.execute(
        "SELECT * FROM simulasi_paket WHERE id_simulasi=%s AND id_paket=%s", (id_simulasi, id_paket,))
    resultCek = cursor.fetchone()
    print(json.dumps(resultCek))

    if(json.dumps(resultCek) == "null"):
        cursor.execute(
            "INSERT INTO simulasi_paket (id_simulasi,id_paket) VALUES (%s,%s)",(id_simulasi,id_paket,))
        connection.commit()

    cursor.close()
    return json.dumps({"status":"success"})

@app.route('/data-simulasi')
def dataSimulasi():
    cursor = connection.cursor()
    result = cursor.execute("SELECT * FROM simulasi")
    simulasis = cursor.fetchall()
    cursor.close()
    return render_template('simulasi/data-simulasi.html', simulasis=simulasis)

@app.route('/data-simulasi/add', methods=["POST"])
def addSimulasi():
    nama_simulasi = request.form['nama_simulasi']
    panduan = request.form['panduan']
    durasi = request.form['durasi']
    
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO simulasi (nama_simulasi,panduan,durasi,sampul) VALUES (%s,%s,%s,'')", [nama_simulasi, panduan,int(durasi)])
    connection.commit()
    cursor.close()
    return redirect(url_for('dataSimulasi'))

@app.route('/data-simulasi/update', methods=["POST"])
def updateSimulasi():
    nama_simulasi = request.form['nama_simulasi']
    panduan = request.form['panduan']
    durasi = request.form['durasi']
    id = request.form['id']
    
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE simulasi SET nama_simulasi=%s,panduan=%s,durasi=%s WHERE id=%s", [nama_simulasi,panduan,int(durasi), id])
    connection.commit()
    cursor.close()
    return redirect(url_for('dataSimulasi'))

@app.route('/data-simulasi/delete/<string:id>')
def deleteSimulasi(id):
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM simulasi WHERE id=%s", [id])
    connection.commit()

    cursor.execute(
        "DELETE FROM simulasi_paket WHERE id_simulasi=%s", [id])
    connection.commit()

    cursor.close()
    return redirect(url_for('dataSimulasi'))

@app.route('/data-simulasi/<string:id>')
def detailSimulasi(id):
    cursor = connection.cursor()
    result = cursor.execute("SELECT * FROM simulasi WHERE id="+id)
    simulasi = cursor.fetchone()

    resultPaket = cursor.execute(
        "select pk.nama_paket, sp.id, sp.id_paket,sp.id_simulasi from simulasi_paket as sp inner join paket as pk where id_paket=pk.id AND id_simulasi="+id)
    paketSimulasi = cursor.fetchall()

    cursor.close()
    return render_template('simulasi/detail-simulasi.html', simulasi=simulasi, paket=paketSimulasi)

@app.route('/data-simulasi/paket/del/<string:idSim>/<string:idSimPkt>')
def delSimulasiPaket(idSim,idSimPkt):
    cursor = connection.cursor()
    delSimPaket = cursor.execute(
        "DELETE FROM simulasi_paket WHERE id=%s", [idSimPkt])
    connection.commit()
    cursor.close()
    return redirect(url_for('detailSimulasi', id=idSim))

# --------------------------------- END UNTUK ADMIN ------------------------------


# --------------------------------- UNTUK STUDENT ----------------------------------
@app.route('/student/simulasi')
def simulasiStudent():
    cursor = connection.cursor()
    result = cursor.execute("SELECT * FROM simulasi")
    simulasis = cursor.fetchall()
    cursor.close()
    return render_template('student/data-simulasi.html', simulasis=simulasis)

@app.route('/student/simulasi/pilih-paket/<string:idSim>')
def pilihSimulasiPaket(idSim):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM simulasi WHERE id=%s", [idSim])
    simulasi = cursor.fetchone()
    cursor.execute(
        "SELECT p.id as id_paket, p.nama_paket, sp.id as id_sim_paket FROM simulasi_paket as sp INNER JOIN paket as p ON sp.id_paket=p.id WHERE id_simulasi=%s", [idSim])
    paket = cursor.fetchall()
    cursor.close()
    return render_template('student/data-paket.html', simulasi=simulasi, paket=paket)


@app.route('/student/mulai-simulasi', methods=["POST"])
def mulaiSimulasi():
    id_simulasi_paket = request.form['id_simulasi_paket']
    id_paket = request.form['id_paket']
    nama_paket = request.form['nama_paket']
    id_user = session['id_user']

    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO riwayat_simulasi (id_paket,nama_paket,id_simulasi_paket,id_user) VALUES (%s,%s,%s,%s)", [id_paket, nama_paket, id_simulasi_paket, id_user])
    connection.commit()
    id_riwayat = cursor.lastrowid
    cursor.close()

    return redirect(url_for('mulaiJawabSoal', idRiwayat=id_riwayat, idSimPaket=id_simulasi_paket, idPaket=id_paket, nomor=1))


@app.route('/student/mulai-simulasi/<string:idRiwayat>/<string:idSimPaket>/paket/<string:idPaket>/pertanyaan/<string:nomor>')
def mulaiJawabSoal(idRiwayat, idSimPaket, idPaket, nomor):
    id_user = session['id_user']
    limit = 1
    nomor = int(nomor)
    offset = int(nomor) - 1

    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM riwayat_simulasi WHERE id=%s", [idRiwayat])
    riwayat = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM paket WHERE id=%s", [idPaket])
    paket = cursor.fetchone()

    cursor.execute(
        "SELECT s.nama_simulasi, s.durasi, s.id FROM simulasi as s INNER JOIN simulasi_paket as sp ON s.id=sp.id_simulasi WHERE sp.id=%s", [idSimPaket])
    simulasi = cursor.fetchone()

    cursor.execute(
        "SELECT sl.id,sl.pertanyaan_text,sl.id_paket,sl.id_tipe,sl.nomor_soal,ts.nama_tipe FROM soal as sl INNER JOIN tipe_soal as ts WHERE sl.id_tipe=ts.id AND id_paket=%s ORDER BY nomor_soal ASC LIMIT %s OFFSET %s", [idPaket, limit, offset])
    soal = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM jawaban_riwayat_simulasi WHERE id_riwayat=%s AND id_soal=%s", [idRiwayat,soal['id']])
    cek_jawaban = cursor.fetchone()

    cursor.execute(
        "SELECT count(sl.id) as total FROM soal as sl INNER JOIN tipe_soal as ts WHERE sl.id_tipe=ts.id AND id_paket=%s ORDER BY nomor_soal ASC", [idPaket])
    totalSoal = cursor.fetchone()

    cursor.close()

    return render_template('student/jawab-soal.html', cek_jawaban=cek_jawaban, riwayat=riwayat, simulasi=simulasi, idSimPaket=idSimPaket, paket=paket, totalSoal=totalSoal, soal=soal, nomor=nomor)


@app.route('/student/mulai-simulasi/simpan-jawaban', methods=["POST"])
def simpanJawaban():
    id_simulasi_paket = request.form['id_simulasi_paket']
    id_paket = request.form['id_paket']
    id_riwayat = request.form['id_riwayat']
    id_tipe = request.form['id_tipe']
    id_soal = request.form['id_soal']
    id_opsi_jawab = request.form['jawaban']
    nomor = int(request.form['nomor'])
    total = int(request.form['total'])

    if total == nomor:
        next_nomor = nomor
    else:
        next_nomor = int(nomor) + 1

    id_user = session['id_user']

    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM soal_opsi WHERE id=%s", [id_opsi_jawab])
    opsi = cursor.fetchone()
    poin = opsi['poin']

    cursor.execute(
        "SELECT * FROM jawaban_riwayat_simulasi WHERE id_riwayat=%s AND id_soal=%s", [id_riwayat, id_soal])
    cek_jawaban = cursor.fetchone()

    if cek_jawaban :
        cursor.execute(
            "UPDATE jawaban_riwayat_simulasi SET poin=%s, id_opsi_jawab=%s WHERE id=%s", [poin, id_opsi_jawab, cek_jawaban['id']])
        connection.commit()
        cursor.close()
    else:
        cursor.execute(
            "INSERT INTO jawaban_riwayat_simulasi (id_user,id_riwayat,id_simulasi_paket,id_tipe,id_soal,id_opsi_jawab,poin) VALUES ( %s, %s, %s, %s, %s, %s, %s)", [id_user, id_riwayat, id_simulasi_paket, id_tipe, id_soal, id_opsi_jawab, poin])
        connection.commit()
        cursor.close()

    return redirect(url_for('mulaiJawabSoal', idRiwayat=id_riwayat, idSimPaket=id_simulasi_paket, idPaket=id_paket, nomor=next_nomor))


@app.route('/student/selesai-simulasi/<string:idRiwayat>')
def selesaiSimulasi(idRiwayat):
    nilai = 0

    cursor = connection.cursor()
    cursor.execute(
        "SELECT SUM(poin) as total_nilai FROM jawaban_riwayat_simulasi WHERE id_riwayat=%s", [idRiwayat])
    cek_nilai = cursor.fetchone()
    nilai = int(cek_nilai['total_nilai'])

    cursor.execute(
        "UPDATE riwayat_simulasi SET nilai=%s WHERE id=%s", [nilai, idRiwayat])
    connection.commit()

    cursor.close()
    return redirect(url_for('hasilSimulasi', idRiwayat=idRiwayat))


@app.route('/student/hasil-simulasi/<string:idRiwayat>')
def hasilSimulasi(idRiwayat):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT rs.nilai, rs.nama_paket, sm.nama_simulasi FROM riwayat_simulasi as rs INNER JOIN simulasi_paket as sp ON rs.id_simulasi_paket=sp.id"+
        " INNER JOIN simulasi as sm ON sp.id_simulasi=sm.id WHERE rs.id=%s", [idRiwayat])
    hasil = cursor.fetchone()

    cursor.execute(
        "SELECT ts.nama_tipe, (SELECT SUM(poin) FROM jawaban_riwayat_simulasi WHERE id_tipe=ts.id AND id_riwayat=jrs.id_riwayat) as tspoin"+
        " FROM jawaban_riwayat_simulasi as jrs INNER JOIN tipe_soal as ts ON jrs.id_tipe=ts.id" +
        " WHERE id_riwayat=%s GROUP BY id_tipe", [idRiwayat])
    tipesoal = cursor.fetchall()

    connection.commit()

    cursor.close()
    return render_template('student/hasil-simulasi.html',hasil=hasil, tipesoal=tipesoal)
# ------------------------------- END UNTUK STUDENT --------------------------------

@app.route('/contact-us')
def contactUs():
    return render_template('contact-us.html')

if __name__ == '__main__':
    app.run('127.0.0.1', '5000', debug=True)

