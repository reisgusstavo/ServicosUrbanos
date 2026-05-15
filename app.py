from flask import Flask, render_template, request, redirect, session
import pyodbc
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '123456'

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def conectar():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=GUSTAVO;"
        "DATABASE=ServicosUrbanos;"
        "Trusted_Connection=yes;"
    )

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    senha = request.form['senha']

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT email, senha, tipo
        FROM Usuarios
        WHERE email = ? AND senha = ?
    """, email, senha)

    usuario = cursor.fetchone()
    conn.close()

    if usuario:
        session['usuario'] = usuario[0]
        session['tipo'] = usuario[2]
        if usuario[2] == 'admin':
            return redirect('/admin')
        else:
            return redirect('/usuario')

    return "Login inválido"

@app.route('/usuario')
def usuario():
    if 'usuario' not in session:
        return redirect('/')

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nome, endereco, telefone, tipo, descricao, status
        FROM Solicitacoes
        WHERE usuario_email = ?
    """, session['usuario'])

    solicitacoes = cursor.fetchall()
    conn.close()

    return render_template('usuario.html', solicitacoes=solicitacoes)

@app.route('/admin')
def admin():
    if 'usuario' not in session:
        return redirect('/')
    if session['tipo'] != 'admin':
        return 'Acesso negado'

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Solicitacoes")
    solicitacoes = cursor.fetchall()
    conn.close()

    return render_template('admin.html', solicitacoes=solicitacoes)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/criar-solicitacao', methods=['POST'])
def criar_solicitacao():
    if 'usuario' not in session:
        return redirect('/')

    imagem_nome = None

    if 'imagem' in request.files:
        arquivo = request.files['imagem']
        if arquivo and arquivo.filename != '' and allowed_file(arquivo.filename):
            imagem_nome = secure_filename(arquivo.filename)
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], imagem_nome)
            conteudo = arquivo.read()
            with open(caminho, 'wb') as f:
                f.write(conteudo)

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Solicitacoes
        (usuario_email, nome, endereco, telefone, tipo, descricao, status, imagem)
        VALUES (?, ?, ?, ?, ?, ?, 'Aberto', ?)
    """,
    session['usuario'],
    request.form['nome'],
    request.form['endereco'],
    request.form['telefone'],
    request.form['tipo'],
    request.form['descricao'],
    imagem_nome)

    conn.commit()
    conn.close()

    return redirect('/usuario')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/criar-usuario', methods=['POST'])
def criar_usuario():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Usuarios (email, senha, tipo)
        VALUES (?, ?, 'usuario')
    """,
    request.form['email'],
    request.form['senha'])

    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/concluir/<int:id>', methods=['POST'])
def concluir_solicitacao(id):
    if 'usuario' not in session:
        return redirect('/')

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE Solicitacoes SET status = 'Concluído' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/excluir/<int:id>', methods=['POST'])
def excluir_solicitacao(id):
    if 'usuario' not in session:
        return redirect('/')
    if session['tipo'] != 'admin':
        return 'Acesso negado'

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Solicitacoes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)