# MEMBUAT APLIKASI SIMULASI CPNS SEDERHANA MENGGUNAKAN PYTHON, FLASK & MySQL

# Tahap Persiapan
- install python
- install text editor ([Notepad++](https://notepad-plus-plus.org/downloads/v7.8.1/) atau [Visual Studio Code](https://code.visualstudio.com/download) atau text editor lainnya)
- install [XAMPP](https://www.apachefriends.org/index.html) / WAMP

# Konfigurasi
- install flask, flask_cors, pymysql, bcrypt menggunakan pip
- buat database dengan nama simulasi_cpns

# Desain Database
![N|Solid](https://i.postimg.cc/DZrmbL6q/relasi-tabel-simulasi-tes-cpns.png)
Contoh kode program untuk men-generate tabel:
```python
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
```
![N|Solid](https://i.postimg.cc/XYRc9Mdd/onion-ring-struktur-simulasi-cpns.png)

# Membuat Default Admin

Aplikasi sederhana ini memungkinkan pengguna untuk menambah simulasi, tipe, paket dan soal layaknya admin dan melakukan simulasi layaknya siswa.

Sebelum membuat akun, lakukan pengecekan terlebih dahulu untuk mengetahui apakah email yang akan digunakan oleh pengguna tersedia (belum pernah digunakan). Jika belum digunakan maka lakukan penambahan pengguna baru dengan role sebagai admin

Contoh kode program
```python

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

```
Aplikasi ini menggunakan bcrypt untuk mengenkripsi password pengguna. Bcrypt memerlukan secret key untuk meng-encode dan men-decode password. Secret key ini bersifat rahasia dan diusahakan untuk dibuat serumit mungkin untuk keamanan (kodenya terserah dari pengembang aplikasi).

```python
app.secret_key = "^A%DJAJU^JJ123"
```

# Login

Pengguna memasukkan email dan password yang telah dibuat selanjutnya form login tersebut akan diarahkan ke route login dengan fungsi login()

Pada fungsi login() dilakukan pengecekan method request yang digunakan, jika method adalah GET maka diarahkan ke form login.html jika tidak maka diarahkan untuk pengecekan email dan password

```python
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
```

# Register

Pengguna dapat mendaftarkan diri melalu menu register kemudian mengisi biodata sesuai form tersebut
![N|Solid](https://i.postimg.cc/kGjpxxr2/html-register.png)

Lakukan pengecekan email sebelum membuat pengguna baru, jika email belum digunakan maka lakukan aksi INSERT INTO

Contoh kode program:

```python
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
```

# Menampilkan data dari database

Untuk menampilkan data dari database ada 2 yaitu menampilkan seluruh data sesuai dengan query yang diberikan atau menampilkan satu data suai dengan query yang diberikan

Contoh kode program untuk menampilkan seluruh data:
```python
cursor = connection.cursor()
cursor.execute("SELECT * FROM tipe_soal")
tipe = cursor.fetchall()
cursor.close()
```

Contoh kode program untuk menampilkan seluruh data:
```python
cursor = connection.cursor()
cursor.execute("SELECT * FROM tipe_soal WHERE id=1")
tipe = cursor.fetchone()
cursor.close()
```

Jika menggunakan fetchall() maka data akan dilooping satu per satu menggunakan for
```html
<table class="table table-striped">
    <thead>
        <tr>
            <td>ID</td>
            <td>Nama Tipe Soal</td>
        </tr>
    </thead>
    <tbody>
        {% for row in tipe %}
        <tr>
            <td>{{ row.id }}</td>
            <td>{{ row.nama_tipe }}</td>
        </tr>
        {% endfor %}
    <tbody>
</table>
```

# Menambahkan data berdasarkan form yang diimput
Contoh pada form penambahan Tipe Soal hanya terdapat satu field input yaitu nama tipe soal

```html
<form method="POST" action="/data-tipe/add">
    <div class="form-group">
        <label for="usr">Nama Tipe Soal:</label>
        <input type="text" class="form-control" name="nama_tipe">
    </div>
    <p>
        <button type="submit" class="btn btn-primary">Simpan</button>
    </p>
</form>
```

Maka dibuat route dengan tipe POST

```python
@app.route('/data-tipe/add', methods=["POST"])
def addTipe():
    nama_tipe = request.form['nama_tipe']

    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO tipe_soal (nama_tipe) VALUES (%s)", [nama_tipe])
    connection.commit()
    cursor.close()
    return redirect(url_for('dataTipe'))
```

connection.commit() untuk melakukan konfirmasi perubahan terhadap database baik itu INSERT, UPDATE dan DELETE

# Melakukan Update Data
Contoh route untuk mengubah nama paket soal

```python
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
```

# Menghapus Data
Mengapus data adalah aksi yang beresiko tinggi karena data yang telah dihapus tidak dapat dikembalikan oleh karena itu diperlukan konfirmasi ulang apakah benar pengguna ingin menhapus data tersebut. Untuk melakukan konfirmasi ke user cukup mudah menggunakan salah satu fungsi dari javascript yaitu fungsi confirm(). Fungsi confirm() diletakkan pada link hapus.

Contoh penggunakan fungsi confirm()
```html
<a href="/data-paket/delete/{{ row.id }}" class="btn btn-xs btn-danger" onclick="return confirm('Yakin ingin hapus?')">Hapus</a>
```

Contoh route untuk menghapus data paket soal
```python
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
```

Semua soal yang masuk dalam kategori paket tersebut juga akan dihapus

# Menajawab Soal
Pada saat pengguna melakukan simulasi dan menyimpan jawaban dari soal maka terlebih dahulu dicek berapa poin pertanyaan tersebut, kemudian mengecek apakah pertanyaan tersebut sudah pernah diwab sebelumnya

Jika pertanyaan belum pernah dijawab maka jalankan query INSERT jika sudah ernah dijawab maka jalankan query UPDATE

```python
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
```

# Selesai Simulasi
Setelah selesai simulasi maka dihitung berapa total poin yang berhasil didapatkan dan berapa poin setiap tipe soal

```python
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
```