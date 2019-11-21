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
Contoh kode program untuk megenerate tabel:
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

Contoh kode program:)
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

