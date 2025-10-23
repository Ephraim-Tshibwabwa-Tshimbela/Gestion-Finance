import sqlite3
import hashlib
from datetime import datetime
import os

def init_db():
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    # Table des utilisateurs
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            default_currency TEXT DEFAULT 'USD',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des transactions
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            category TEXT,
            description TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Table des taux de change
    c.execute('''
        CREATE TABLE IF NOT EXISTS exchange_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            base_currency TEXT NOT NULL,
            target_currency TEXT NOT NULL,
            rate REAL NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Vérifier et ajouter la colonne default_currency si elle n'existe pas
    try:
        c.execute("ALTER TABLE users ADD COLUMN default_currency TEXT DEFAULT 'USD'")
    except sqlite3.OperationalError:
        pass  # La colonne existe déjà
    
    # Vérifier et ajouter la colonne currency si elle n'existe pas
    try:
        c.execute("ALTER TABLE transactions ADD COLUMN currency TEXT DEFAULT 'USD'")
    except sqlite3.OperationalError:
        pass  # La colonne existe déjà
    
    # Créer un utilisateur de test (mot de passe: test123)
    try:
        hashed_password = hashlib.sha256("test123".encode('utf-8')).hexdigest()
        c.execute("INSERT INTO users (username, password, default_currency) VALUES (?, ?, ?)", 
                 ("test", hashed_password, 'USD'))
        print("Utilisateur test créé - username: test, password: test123")
    except sqlite3.IntegrityError:
        print("Utilisateur test existe déjà")
    
    # Insérer les taux de change s'ils n'existent pas
    try:
        c.execute("SELECT COUNT(*) FROM exchange_rates")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO exchange_rates (base_currency, target_currency, rate) VALUES (?, ?, ?)",
                     ("USD", "CDF", 2300.0))
            c.execute("INSERT INTO exchange_rates (base_currency, target_currency, rate) VALUES (?, ?, ?)",
                     ("CDF", "USD", 1/2300.0))
            print("Taux de change insérés")
    except:
        print("Erreur lors de l'insertion des taux de change")
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('finance.db')
    conn.row_factory = sqlite3.Row
    return conn