from flask import Flask, request, redirect, jsonify
import sqlite3
import string
import random
import os

app = Flask(__name__)

# Configuração do banco de dados SQLite
def init_db():
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls
                 (short_code TEXT PRIMARY KEY, long_url TEXT)''')
    conn.commit()
    conn.close()

# Gerar um código curto aleatório
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Inicializar o banco de dados
init_db()

# Rota para encurtar URLs
@app.route('/shorten', methods=['POST'])
def shorten_url():
    long_url = request.json.get('url')
    if not long_url:
        return jsonify({"error": "URL não fornecida"}), 400

    # Verificar se a URL já existe
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute("SELECT short_code FROM urls WHERE long_url = ?", (long_url,))
    result = c.fetchone()

    if result:
        conn.close()
        return jsonify({"short_url": f"{request.host_url}{result[0]}"})

    # Gerar um código curto único
    while True:
        short_code = generate_short_code()
        c.execute("SELECT short_code FROM urls WHERE short_code = ?", (short_code,))
        if not c.fetchone():
            break

    # Salvar no banco de dados
    c.execute("INSERT INTO urls (short_code, long_url) VALUES (?, ?)", (short_code, long_url))
    conn.commit()
    conn.close()

    return jsonify({"short_url": f"{request.host_url}{short_code}"})

# Rota para redirecionar
@app.route('/<short_code>')
def redirect_url(short_code):
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute("SELECT long_url FROM urls WHERE short_code = ?", (short_code,))
    result = c.fetchone()
    conn.close()

    if result:
        return redirect(result[0])
    return jsonify({"error": "Link não encontrado"}), 404

if __name__ == '__main__':
    app.run(debug=True)