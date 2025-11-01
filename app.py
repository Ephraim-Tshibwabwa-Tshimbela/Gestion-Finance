import os

# Correction automatique des dossiers
if os.path.exists('emplates') and not os.path.exists('templates'):
    os.rename('emplates', 'templates')
    print("✅ Dossier templates corrigé", file=sys.stderr)
import os
import sys
import traceback

# DEBUG - Affiche tout au démarrage
print("🚀 DÉMARRAGE APPLICATION", file=sys.stderr)
print(f"📁 Répertoire: {os.getcwd()}", file=sys.stderr)
print(f"📁 Fichiers: {os.listdir('.')}", file=sys.stderr)

try:
    from flask import Flask, render_template, request, redirect, session, flash, jsonify
    import database
    import hashlib
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import io
    import base64
    from datetime import datetime
    import sqlite3
    import numpy as np
    
    print("✅ TOUS LES IMPORTS RÉUSSIS", file=sys.stderr)
    
except Exception as e:
    print(f"❌ ERREUR IMPORT: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-key-123')
# ... reste de votre code existant ...

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🎯 PORT: {port}", file=sys.stderr)
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
        print("✅ APPLICATION DÉMARRÉE", file=sys.stderr)
    except Exception as e:
        print(f"💥 ERREUR DÉMARRAGE: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

app = Flask(__name__)
# Clé secrète sécurisée pour la production
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['DATABASE'] = 'finance.db'

# Taux de change fixe
EXCHANGE_RATES = {
    'USD': {'CDF': 2300.0},
    'CDF': {'USD': 1/2300.0}
}

def convert_currency(amount, from_currency, to_currency):
    """Convertit un montant d'une devise à une autre"""
    if from_currency == to_currency:
        return amount
    if from_currency in EXCHANGE_RATES and to_currency in EXCHANGE_RATES[from_currency]:
        return amount * EXCHANGE_RATES[from_currency][to_currency]
    return amount

def get_user_currency(user_id):
    """Récupère la devise préférée de l'utilisateur"""
    conn = database.get_db_connection()
    try:
        user = conn.execute('SELECT default_currency FROM users WHERE id = ?', (user_id,)).fetchone()
        return user['default_currency'] if user and user['default_currency'] else 'USD'
    except sqlite3.OperationalError:
        return 'USD'
    finally:
        conn.close()

# Initialiser la base de données
with app.app_context():
    database.init_db()
    
    
@app.route('/test')
def test():
    return "✅ L'application fonctionne !"

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})    

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')
    return redirect('/dashboard')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        
        conn = database.get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password)
        ).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Connexion réussie!', 'success')
            return redirect('/dashboard')
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation des données
        if not username or not password:
            flash('Tous les champs sont obligatoires', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères', 'error')
            return render_template('register.html')
        
        # Vérifier si l'utilisateur existe déjà
        conn = database.get_db_connection()
        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ?', (username,)
        ).fetchone()
        
        if existing_user:
            flash('Ce nom d\'utilisateur est déjà pris', 'error')
            conn.close()
            return render_template('register.html')
        
        # Créer le nouvel utilisateur
        try:
            hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            conn.execute(
                'INSERT INTO users (username, password, default_currency) VALUES (?, ?, ?)',
                (username, hashed_password, 'USD')
            )
            conn.commit()
            flash('Compte créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
            return redirect('/login')
        
        except Exception as e:
            flash('Erreur lors de la création du compte', 'error')
            print(f"Erreur: {e}")
        
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté', 'info')
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    user_currency = get_user_currency(user_id)
    conn = database.get_db_connection()
    
    # Calculer le solde
    transactions = conn.execute('SELECT amount, currency, type FROM transactions WHERE user_id = ?', (user_id,)).fetchall()
    
    total_income = 0
    total_expenses = 0
    
    for trans in transactions:
        amount_in_user_currency = convert_currency(trans['amount'], trans['currency'], user_currency)
        if trans['type'] == 'income':
            total_income += amount_in_user_currency
        else:
            total_expenses += amount_in_user_currency
    
    balance = total_income - total_expenses
    
    # Transactions récentes
    transactions = conn.execute('''
        SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC LIMIT 10
    ''', (user_id,)).fetchall()
    
    conn.close()

    # Générer les graphiques MOBILE
    graph_evolution = generate_mobile_balance_chart(user_id, user_currency)
    graph_categories = generate_mobile_expense_chart(user_id, user_currency)
    
    return render_template('dashboard.html', 
                         balance=balance,
                         total_income=total_income,
                         total_expenses=total_expenses,
                         transactions=transactions,
                         user_currency=user_currency,
                         graph_evolution=graph_evolution,
                         graph_categories=graph_categories)

@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_currency = get_user_currency(session['user_id'])
    
    if request.method == 'POST':
        amount = float(request.form['amount'])
        currency = request.form['currency']
        trans_type = request.form['type']
        category = request.form.get('category', '')
        description = request.form.get('description', '')
        
        # La date et l'heure sont automatiquement ajoutées par la base de données
        # grâce à DEFAULT CURRENT_TIMESTAMP
        conn = database.get_db_connection()
        conn.execute('''
            INSERT INTO transactions (user_id, amount, currency, type, category, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], amount, currency, trans_type, category, description))
        conn.commit()
        conn.close()
        
        flash('Transaction ajoutée avec succès!', 'success')
        return redirect('/dashboard')
    
    return render_template('add_transaction.html', user_currency=user_currency)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect('/login')
    
    conn = database.get_db_connection()
    
    if request.method == 'POST':
        default_currency = request.form['default_currency']
        
        conn.execute('UPDATE users SET default_currency = ? WHERE id = ?', 
                    (default_currency, session['user_id']))
        conn.commit()
        conn.close()
        
        flash('Paramètres mis à jour avec succès!', 'success')
        return redirect('/dashboard')
    
    user = conn.execute('SELECT default_currency FROM users WHERE id = ?', 
                       (session['user_id'],)).fetchone()
    user_currency = user['default_currency'] if user and user['default_currency'] else 'USD'
    conn.close()
    
    return render_template('settings.html', user_currency=user_currency)

def generate_mobile_balance_chart(user_id, user_currency):
    """Graphique ultra-simplifié pour mobile"""
    try:
        conn = database.get_db_connection()
        
        transactions = conn.execute('''
            SELECT date, amount, type, currency
            FROM transactions 
            WHERE user_id = ? 
            ORDER BY date
        ''', (user_id,)).fetchall()
        
        conn.close()
        
        if not transactions:
            return None
        
        # Calcul simple du solde cumulé
        dates = []
        balances = []
        current_balance = 0
        
        for trans in transactions:
            try:
                trans_date = datetime.strptime(trans['date'], '%Y-%m-%d %H:%M:%S').date()
            except:
                trans_date = datetime.strptime(trans['date'], '%Y-%m-%d').date()
            
            amount_in_user_currency = convert_currency(trans['amount'], trans['currency'], user_currency)
            
            if trans['type'] == 'income':
                current_balance += amount_in_user_currency
            else:
                current_balance -= amount_in_user_currency
            
            dates.append(trans_date.strftime('%m-%d'))
            balances.append(current_balance)
        
        # Graphique très simple
        plt.figure(figsize=(6, 3))  # Très petit pour mobile
        plt.plot(dates, balances, 'b-', linewidth=2)
        plt.fill_between(dates, balances, alpha=0.3, color='blue')
        plt.title('Solde', fontsize=10)
        plt.xticks(rotation=45, fontsize=8)
        plt.yticks(fontsize=8)
        plt.grid(True, alpha=0.3)
        plt.tight_layout(pad=0.5)
        
        # Conversion en base64 avec compression
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=60, bbox_inches='tight')
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()
        plt.close()
        
        return graph_url
        
    except Exception as e:
        print(f"Erreur graphique mobile: {e}")
        return None

def generate_mobile_expense_chart(user_id, user_currency):
    """Graphique de dépenses ultra-simplifié pour mobile"""
    try:
        conn = database.get_db_connection()
        
        expenses = conn.execute('''
            SELECT category, amount, currency
            FROM transactions 
            WHERE user_id = ? AND type = 'expense' AND amount > 0
        ''', (user_id,)).fetchall()
        
        conn.close()
        
        if not expenses:
            return None
        
        # Regroupement simple
        categories = {}
        for expense in expenses:
            category = expense['category'] or 'Divers'
            amount_in_user_currency = convert_currency(expense['amount'], expense['currency'], user_currency)
            categories[category] = categories.get(category, 0) + amount_in_user_currency
        
        if not categories:
            return None
        
        # Graphique simple en barres horizontales
        categories_names = list(categories.keys())[:5]  # Max 5 catégories
        amounts = [categories[name] for name in categories_names]
        
        plt.figure(figsize=(5, 3))
        plt.barh(categories_names, amounts, color='skyblue')
        plt.title('Dépenses', fontsize=10)
        plt.tight_layout(pad=0.5)
        
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=60, bbox_inches='tight')
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()
        plt.close()
        
        return graph_url
        
    except Exception as e:
        print(f"Erreur graphique dépenses mobile: {e}")
        return None

if __name__ == '__main__':
    # Récupérer le port de Railway ou utiliser 5000 en local
    port = int(os.environ.get("PORT", 5000))
    
    # Afficher l'URL d'accès
    print(f"🚀 Application démarrée sur le port: {port}", file=sys.stderr)
    print(f"🌐 URL d'accès: http://0.0.0.0:{port}", file=sys.stderr)
    
    # Démarrer l'application
    try:
        app.run(
            host='0.0.0.0', 
            port=port, 
            debug=False,
            # Important pour Railway
            use_reloader=False
        )
    except Exception as e:
        print(f"❌ Erreur: {e}", file=sys.stderr)
        raise