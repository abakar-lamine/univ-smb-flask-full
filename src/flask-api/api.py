import json
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

# Configuration des chemins pour le dossier 'data'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# --- FONCTIONS UTILITAIRES ---

def read_json(filename):
    """Lit un fichier JSON dans le dossier data."""
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_json(filename, data):
    """Écrit des données dans un fichier JSON dans le dossier data."""
    file_path = os.path.join(DATA_DIR, filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

# ==========================================
# ROUTE ACCUEIL
# ==========================================

@app.route("/")
def hello():
    return "Hello, API!"

# ==========================================
# PARTIE IDENTITÉ & AUTHENTIFICATION
# ==========================================

@app.route('/login', methods=['GET'])
def login():
    # Simulé pour le TP
    return jsonify({"status": "success", "message": "Connecté à l'API"}), 200

@app.route('/identity', methods=['GET'])
def get_identities():
    # Retourne une liste fictive d'utilisateurs pour les tests
    users = [{"username": "admin", "role": "root"}, {"username": "student", "role": "user"}]
    return jsonify(users), 200

@app.route('/identity/<username>', methods=['GET'])
def get_user(username):
    return jsonify({"username": username, "authorized": True}), 200

# ==========================================
# PARTIE LOAD BALANCER
# ==========================================

@app.route('/config/lb', methods=['GET'])
def get_all_lb():
    return jsonify(read_json('loadbalancer.json')), 200

@app.route('/config/lb/<int:lb_id>', methods=['GET'])
def get_lb(lb_id):
    data = read_json('loadbalancer.json')
    item = next((x for x in data if x.get('id') == lb_id), None)
    return jsonify(item) if item else (jsonify({"error": "Not found"}), 404)

@app.route('/config/lb', methods=['POST'])
def create_lb():
    new_item = request.get_json()
    data = read_json('loadbalancer.json')
    new_item['id'] = (max(x['id'] for x in data) + 1) if data else 1
    data.append(new_item)
    write_json('loadbalancer.json', data)
    return jsonify(new_item), 201

@app.route('/config/lb/<int:lb_id>', methods=['DELETE'])
def delete_lb(lb_id):
    data = read_json('loadbalancer.json')
    new_data = [x for x in data if x.get('id') != lb_id]
    write_json('loadbalancer.json', new_data)
    return jsonify({"message": "Deleted"}), 200

# ==========================================
# PARTIE REVERSE PROXY
# ==========================================

@app.route('/config/rp', methods=['GET'])
def get_all_rp():
    return jsonify(read_json('reverseproxy.json')), 200

@app.route('/config/rp/<int:rp_id>', methods=['GET'])
def get_rp(rp_id):
    data = read_json('reverseproxy.json')
    item = next((x for x in data if x.get('id') == rp_id), None)
    return jsonify(item) if item else (jsonify({"error": "Not found"}), 404)

@app.route('/config/rp', methods=['POST'])
def create_rp():
    new_item = request.get_json()
    data = read_json('reverseproxy.json')
    new_item['id'] = (max(x['id'] for x in data) + 1) if data else 1
    data.append(new_item)
    write_json('reverseproxy.json', data)
    return jsonify(new_item), 201

@app.route('/config/rp/<int:rp_id>', methods=['DELETE'])
def delete_rp(rp_id):
    data = read_json('reverseproxy.json')
    new_data = [x for x in data if x.get('id') != rp_id]
    write_json('reverseproxy.json', new_data)
    return jsonify({"message": "Deleted"}), 200

# ==========================================
# PARTIE WEB SERVER
# ==========================================

@app.route('/config/ws', methods=['GET'])
def get_all_ws():
    return jsonify(read_json('webserver.json')), 200

@app.route('/config/ws/<int:ws_id>', methods=['GET'])
def get_ws(ws_id):
    data = read_json('webserver.json')
    item = next((x for x in data if x.get('id') == ws_id), None)
    return jsonify(item) if item else (jsonify({"error": "Not found"}), 404)

@app.route('/config/ws', methods=['POST'])
def create_ws():
    new_item = request.get_json()
    data = read_json('webserver.json')
    new_item['id'] = (max(x['id'] for x in data) + 1) if data else 1
    data.append(new_item)
    write_json('webserver.json', data)
    return jsonify(new_item), 201

@app.route('/config/ws/<int:ws_id>', methods=['DELETE'])
def delete_ws(ws_id):
    data = read_json('webserver.json')
    new_data = [x for x in data if x.get('id') != ws_id]
    write_json('webserver.json', new_data)
    return jsonify({"message": "Deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)