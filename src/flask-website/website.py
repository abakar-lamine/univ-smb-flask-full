import requests
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, Response

app = Flask(__name__)

# Clé secrète pour chiffrer les cookies de session
app.secret_key = "cle_secrete_projet_usmb_l3"

# URL de l'API (flask-api) qui tourne sur le port 5000
API_URL = "http://127.0.0.1:5000"

# ==========================================
# SÉCURITÉ : DÉCORATEUR DE CONNEXION
# ==========================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# ROUTES D'ACCUEIL ET AUTHENTIFICATION
# ==========================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Appel à la "vraie" auth de l'API
        try:
            resp = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
            if resp.status_code == 200:
                user_data = resp.json()['user']
                session['username'] = user_data['username']
                session['role'] = user_data['role']
                return redirect(url_for('list_all'))
        except:
            pass
        return render_template("login.html", error="Nom d'utilisateur ou mot de passe incorrect")
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation simple côté serveur
        if password != confirm_password:
            return render_template("register.html", error="Les mots de passe ne correspondent pas")
            
        try:
            resp = requests.post(f"{API_URL}/register", json={
                "username": username, 
                "password": password
            })
            if resp.status_code == 201:
                return redirect(url_for('login')) # Redirection après succès
            else:
                error_msg = resp.json().get('message', 'Erreur lors de l\'inscription')
                return render_template("register.html", error=error_msg)
        except:
            return render_template("register.html", error="L'API est indisponible")
            
    return render_template("register.html")

@app.route('/logout')
def logout():
    """Ferme la session utilisateur."""
    session.pop('username', None)
    return redirect(url_for('index'))

# ==========================================
# PROFILS ET VUE GLOBALE
# ==========================================

@app.route('/list_profile')
@login_required
def list_profile():
    try:
        profiles = requests.get(f"{API_URL}/identity").json()
    except:
        profiles = []
    return render_template('list_profile.html', profiles=profiles)

@app.route('/profile/<username>')
@login_required
def profile(username):
    try:
        user_data = requests.get(f"{API_URL}/identity/{username}").json()
    except:
        user_data = {}
    return render_template('profile.html', user=user_data)

@app.route('/list_all')
@login_required
def list_all():
    """Affiche l'ensemble des équipements récupérés via l'API."""
    try:
        lbs = requests.get(f"{API_URL}/config/lb").json()
        rps = requests.get(f"{API_URL}/config/rp").json()
        wss = requests.get(f"{API_URL}/config/ws").json()
    except:
        lbs, rps, wss = [], [], []
    return render_template('list_all.html', lbs=lbs, rps=rps, wss=wss)

@app.route('/download/<type_cfg>/<int:id>')
@login_required
def download_config(type_cfg, id):
    # Récupération de l'objet via l'API
    item = requests.get(f"{API_URL}/config/{type_cfg}/{id}").json()
    
    # Génération du contenu (même logique que dans le template)
    content = f"server {{\n    listen {item.get('ip_bind', '80')}:80;\n    server_name {item['name']}.local;\n    # ... (code config) ...\n}}"
    
    return Response(
        content,
        mimetype="text/plain",
        headers={"Content-disposition": f"attachment; filename=nginx_{item['name']}.conf"}
    )

# ==========================================
# PARTIE LOAD BALANCER
# ==========================================

@app.route('/lb/list')
@login_required
def lb_list():
    try:
        data = requests.get(f"{API_URL}/config/lb").json()
    except:
        data = []
    return render_template('lb_list.html', loadbalancers=data)

@app.route('/lb/<int:id>')
@login_required
def lb_detail(id):
    """Affiche la configuration Nginx générée pour un LB."""
    try:
        lb = requests.get(f"{API_URL}/config/lb/{id}").json()
    except:
        lb = {}
    return render_template('lb_detail.html', lb=lb)

@app.route('/lb/create', methods=['GET', 'POST'])
@login_required
def lb_create():
    if request.method == 'POST':
        lb_data = {
            "name": request.form.get('name'),
            "ip_bind": request.form.get('ip_bind'),
            "pass": request.form.get('pass')
        }
        requests.post(f"{API_URL}/config/lb", json=lb_data)
        return redirect(url_for('lb_list'))
    return render_template('lb_create.html')

@app.route('/lb/<int:id>/delete', methods=['POST'])
@login_required
def lb_delete(id):
    requests.delete(f"{API_URL}/config/lb/{id}")
    return redirect(url_for('lb_list'))

# ==========================================
# PARTIE REVERSE PROXY
# ==========================================

@app.route('/rp/list')
@login_required
def rp_list():
    try:
        data = requests.get(f"{API_URL}/config/rp").json()
    except:
        data = []
    return render_template('rp_list.html', reverseproxies=data)

@app.route('/rp/<int:id>')
@login_required
def rp_detail(id):
    try:
        rp = requests.get(f"{API_URL}/config/rp/{id}").json()
    except:
        rp = {}
    return render_template('rp_detail.html', rp=rp)

@app.route('/rp/create', methods=['GET', 'POST'])
@login_required
def rp_create():
    if request.method == 'POST':
        rp_data = {
            "name": request.form.get('name'),
            "ip_bind": request.form.get('ip_bind'),
            "target": request.form.get('target')
        }
        requests.post(f"{API_URL}/config/rp", json=rp_data)
        return redirect(url_for('rp_list'))
    return render_template('rp_create.html')

@app.route('/rp/<int:id>/delete', methods=['POST'])
@login_required
def rp_delete(id):
    requests.delete(f"{API_URL}/config/rp/{id}")
    return redirect(url_for('rp_list'))

# ==========================================
# PARTIE WEB SERVER
# ==========================================

@app.route('/ws/list')
@login_required
def ws_list():
    try:
        data = requests.get(f"{API_URL}/config/ws").json()
    except:
        data = []
    return render_template('ws_list.html', webservers=data)

@app.route('/ws/<int:id>')
@login_required
def ws_detail(id):
    try:
        ws = requests.get(f"{API_URL}/config/ws/{id}").json()
    except:
        ws = {}
    return render_template('ws_detail.html', ws=ws)

@app.route('/ws/create', methods=['GET', 'POST'])
@login_required
def ws_create():
    if request.method == 'POST':
        ws_data = {
            "name": request.form.get('name'),
            "port": request.form.get('port'),
            "root_path": request.form.get('root_path')
        }
        requests.post(f"{API_URL}/config/ws", json=ws_data)
        return redirect(url_for('ws_list'))
    return render_template('ws_create.html')

@app.route('/ws/<int:id>/delete', methods=['POST'])
@login_required
def ws_delete(id):
    requests.delete(f"{API_URL}/config/ws/{id}")
    return redirect(url_for('ws_list'))

if __name__ == '__main__':
    # Le site WebGenerator tourne sur le port 8080
    app.run(debug=True, port=8080)