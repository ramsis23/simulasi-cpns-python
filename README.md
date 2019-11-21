<h1 class="code-line" data-line-start=0 data-line-end=1 ><a id="MEMBUAT_APLIKASI_SIMULASI_CPNS_SEDERHANA_MENGGUNAKAN_PYTHON_FLASK__MySQL_0"></a>MEMBUAT APLIKASI SIMULASI CPNS SEDERHANA MENGGUNAKAN PYTHON, FLASK &amp; MySQL</h1>
<h1 class="code-line" data-line-start=2 data-line-end=3 ><a id="Tahap_Persiapan_2"></a>Tahap Persiapan</h1>
<ul>
<li class="has-line-data" data-line-start="3" data-line-end="4">install python</li>
<li class="has-line-data" data-line-start="4" data-line-end="5">install text editor (<a href="https://notepad-plus-plus.org/downloads/v7.8.1/">Notepad++</a> atau <a href="https://code.visualstudio.com/download">Visual Studio Code</a> atau text editor lainnya)</li>
<li class="has-line-data" data-line-start="5" data-line-end="7">install <a href="https://www.apachefriends.org/index.html">XAMPP</a> / WAMP</li>
</ul>
<h1 class="code-line" data-line-start=7 data-line-end=8 ><a id="Konfigurasi_7"></a>Konfigurasi</h1>
<ul>
<li class="has-line-data" data-line-start="8" data-line-end="9">install flask, flask_cors, pymysql, bcrypt menggunakan pip</li>
<li class="has-line-data" data-line-start="9" data-line-end="11">buat database dengan nama simulasi_cpns</li>
</ul>
<h1 class="code-line" data-line-start=11 data-line-end=12 ><a id="Desain_Database_11"></a>Desain Database</h1>
<p class="has-line-data" data-line-start="12" data-line-end="14"><img src="https://i.postimg.cc/DZrmbL6q/relasi-tabel-simulasi-tes-cpns.png" alt="N|Solid"><br>
Contoh kode program untuk megenerate tabel:</p>
<pre><code class="has-line-data" data-line-start="15" data-line-end="90" class="language-python">cursor = connection.cursor()
cursor.execute(<span class="hljs-string">'''CREATE TABLE IF NOT EXISTS users
     (id            INT AUTO_INCREMENT PRIMARY KEY,
     name           VARCHAR(255)             NOT NULL,
     email          VARCHAR(255)   UNIQUE    NOT NULL,
     password       VARCHAR(255)             NOT NULL,
     role           VARCHAR(255)             NOT NULL
     );'''</span>)

cursor.execute(<span class="hljs-string">'''CREATE TABLE IF NOT EXISTS simulasi
     (id              INT AUTO_INCREMENT PRIMARY KEY,
     nama_simulasi    VARCHAR(255)    NOT NULL,
     sampul           VARCHAR(255)    NULL,
     bgHome           VARCHAR(255)    NULL,
     durasi           INT             NOT NULL,
     panduan          TEXT            NULL,
     bgPanduan        VARCHAR(255)    NULL,
     bgPertanyaan     VARCHAR(255)    NULL
     );'''</span>)

cursor.execute(<span class="hljs-string">'''CREATE TABLE IF NOT EXISTS paket
     (id           INT AUTO_INCREMENT PRIMARY KEY,
     nama_paket    VARCHAR(255)    NOT NULL);'''</span>)

cursor.execute(<span class="hljs-string">'''CREATE TABLE IF NOT EXISTS tipe_soal
     (id           INT AUTO_INCREMENT PRIMARY KEY,
     nama_tipe     VARCHAR(255)    NOT NULL);'''</span>)

cursor.execute(<span class="hljs-string">'''CREATE TABLE IF NOT EXISTS soal
     (id               INT AUTO_INCREMENT PRIMARY KEY,
     pertanyaan_text   VARCHAR(255)    NULL,
     pertanyaan_img    VARCHAR(255)    NULL,
     id_paket          INT             NOT NULL,
     id_tipe           INT             NOT NULL,
     nomor_soal        INT             NOT NULL
     );'''</span>)

cursor.execute(<span class="hljs-string">'''CREATE TABLE IF NOT EXISTS soal_opsi
     (id         INT AUTO_INCREMENT PRIMARY KEY,
     opsi_text   VARCHAR(255)    NULL,
     opsi_img    VARCHAR(255)    NULL,
     poin        INT             NOT NULL,
     id_soal     INT             NOT NULL
     );'''</span>)

cursor.execute(<span class="hljs-string">'''CREATE TABLE IF NOT EXISTS simulasi_paket
     (id           INT AUTO_INCREMENT PRIMARY KEY,
     id_paket      INT    NOT NULL,
     id_simulasi   INT    NOT NULL
     );'''</span>)

cursor.execute(<span class="hljs-string">'''CREATE TABLE IF NOT EXISTS riwayat_simulasi
     (id                    INT AUTO_INCREMENT PRIMARY KEY,
     id_user                INT             NOT NULL,
     id_simulasi_paket      INT             NOT NULL,
     id_paket               INT             NOT NULL,
     nilai                  INT             NULL,
     nama_paket             VARCHAR(255)    NULL,
     mulai                  VARCHAR(50)     NULL,
     selesai                VARCHAR(50)     NULL
     );'''</span>)

cursor.execute(<span class="hljs-string">'''CREATE TABLE IF NOT EXISTS jawaban_riwayat_simulasi
     (id                    INT AUTO_INCREMENT PRIMARY KEY,
     id_user                INT             NOT NULL,
     id_riwayat             INT             NOT NULL,
     id_simulasi_paket      INT             NOT NULL,
     id_tipe                INT             NULL,
     id_soal                INT             NOT NULL,
     id_opsi_jawab          INT             NOT NULL,
     poin                   INT             NULL
     );'''</span>)

cursor.close()
</code></pre>
<p class="has-line-data" data-line-start="90" data-line-end="91"><img src="https://i.postimg.cc/XYRc9Mdd/onion-ring-struktur-simulasi-cpns.png" alt="N|Solid"></p>
<h1 class="code-line" data-line-start=92 data-line-end=93 ><a id="Membuat_Default_Admin_92"></a>Membuat Default Admin</h1>
<p class="has-line-data" data-line-start="94" data-line-end="95">Aplikasi sederhana ini memungkinkan pengguna untuk menambah simulasi, tipe, paket dan soal layaknya admin dan melakukan simulasi layaknya siswa.</p>
<p class="has-line-data" data-line-start="96" data-line-end="97">Sebelum membuat akun, lakukan pengecekan terlebih dahulu untuk mengetahui apakah email yang akan digunakan oleh pengguna tersedia (belum pernah digunakan). Jika belum digunakan maka lakukan penambahan pengguna baru dengan role sebagai admin</p>
<p class="has-line-data" data-line-start="98" data-line-end="99">Contoh kode program:)</p>
<pre><code class="has-line-data" data-line-start="100" data-line-end="121" class="language-python">
    <span class="hljs-comment"># Cek apakah user dengan email tersebut sudah ada</span>
    cursor = connection.cursor()
    default_admin_email = <span class="hljs-string">'admin@gmail.com'</span>
    cursor.execute(
        <span class="hljs-string">"SELECT count(email) as total FROM users WHERE email=%s"</span>, [default_admin_email])
    user = cursor.fetchone()
    cursor.close()

    <span class="hljs-keyword">if</span> int(user[<span class="hljs-string">'total'</span>]) == <span class="hljs-number">0</span>:
        <span class="hljs-comment"># Buat User default untuk admin</span>
        cursor = connection.cursor()
        password = <span class="hljs-string">'admin'</span>
        password_encode = password.encode(<span class="hljs-string">'utf-8'</span>)
        hash_password = bcrypt.hashpw(password_encode, bcrypt.gensalt())
        cursor.execute(
            <span class="hljs-string">"INSERT INTO users (name,email,password,role) VALUES ('Admin',%s,%s,'admin')"</span>, [default_admin_email, hash_password])
        connection.commit()
        cursor.close()

</code></pre>
<p class="has-line-data" data-line-start="121" data-line-end="122">Aplikasi ini menggunakan bcrypt untuk mengenkripsi password pengguna. Bcrypt memerlukan secret key untuk meng-encode dan men-decode password. Secret key ini bersifat rahasia dan diusahakan untuk dibuat serumit mungkin untuk keamanan (kodenya terserah dari pengembang aplikasi).</p>
<pre><code class="has-line-data" data-line-start="124" data-line-end="126" class="language-python">app.secret_key = <span class="hljs-string">"^A%DJAJU^JJ123"</span>
</code></pre>
<h1 class="code-line" data-line-start=127 data-line-end=128 ><a id="Login_127"></a>Login</h1>
<p class="has-line-data" data-line-start="129" data-line-end="130">Pengguna memasukkan email dan password yang telah dibuat selanjutnya form login tersebut akan diarahkan ke route login dengan fungsi login()</p>
<p class="has-line-data" data-line-start="131" data-line-end="132">Pada fungsi login() dilakukan pengecekan method request yang digunakan, jika method adalah GET maka diarahkan ke form login.html jika tidak maka diarahkan untuk pengecekan email dan password</p>
<pre><code class="has-line-data" data-line-start="134" data-line-end="170" class="language-python"><span class="hljs-decorator">@app.route('/login', methods=["GET", "POST"])</span>
<span class="hljs-function"><span class="hljs-keyword">def</span> <span class="hljs-title">login</span><span class="hljs-params">()</span>:</span>
    <span class="hljs-keyword">if</span> request.method == <span class="hljs-string">'POST'</span>:
        email = request.form[<span class="hljs-string">'email'</span>]
        password = request.form[<span class="hljs-string">'password'</span>].encode(<span class="hljs-string">'utf-8'</span>)

        <span class="hljs-comment"># Cek apakah user dengan email tersebut sudah ada</span>
        cursor = connection.cursor()
        cursor.execute(
            <span class="hljs-string">"SELECT count(email) as total FROM users WHERE email=%s"</span>, [email])
        user = cursor.fetchone()
        cursor.close()

        <span class="hljs-keyword">if</span> int(user[<span class="hljs-string">'total'</span>]) &gt; <span class="hljs-number">0</span>:

            <span class="hljs-comment"># Dapatkan user sesuai dengan email yang terdaftar</span>
            cursor = connection.cursor()
            cursor.execute(<span class="hljs-string">"SELECT * FROM users WHERE email=%s"</span>, (email,))
            user = cursor.fetchone()
            cursor.close()

            <span class="hljs-comment"># cek password menggunakan bcrypt</span>
            <span class="hljs-keyword">if</span> bcrypt.hashpw(password, user[<span class="hljs-string">"password"</span>].encode(<span class="hljs-string">'utf-8'</span>)) == user[<span class="hljs-string">"password"</span>].encode(<span class="hljs-string">'utf-8'</span>):
                session[<span class="hljs-string">'id_user'</span>] = user[<span class="hljs-string">'id'</span>]
                session[<span class="hljs-string">'name'</span>] = user[<span class="hljs-string">'name'</span>]
                session[<span class="hljs-string">'role'</span>] = user[<span class="hljs-string">'role'</span>]
                session[<span class="hljs-string">'email'</span>] = user[<span class="hljs-string">'email'</span>]
                
                <span class="hljs-keyword">return</span> render_template(<span class="hljs-string">"home.html"</span>)
            <span class="hljs-keyword">else</span>:
                <span class="hljs-keyword">return</span> <span class="hljs-string">"Error password and email not match"</span>
        <span class="hljs-keyword">else</span>:
            <span class="hljs-keyword">return</span> <span class="hljs-string">"Error user not found"</span>
    <span class="hljs-keyword">else</span>:
        <span class="hljs-keyword">return</span> render_template(<span class="hljs-string">"login.html"</span>)
</code></pre>