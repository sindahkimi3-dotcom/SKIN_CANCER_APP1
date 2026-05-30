 #  SkinDiag — Plateforme de Diagnostic Dermatologique par IA

> Plateforme web médicale d'assistance au diagnostic dermatologique basée sur un modèle de deep learning **VGG16**, permettant aux médecins de classifier automatiquement des lésions cutanées en **bénignes ou malignes** à partir d'une simple image.

---

##  Fonctionnalités

-  **Authentification sécurisée** — Accès réservé aux médecins avec gestion de session
-  **Analyse IA en temps réel** — Classification bénin/malin via VGG16 avec score de confiance
-  **Dossiers patients** — Historique complet des diagnostics avec images et résultats
-  **Tableau de bord analytique** — Statistiques, graphiques et tendances d'activité
-  **Notes médecin** — Système de commentaires cliniques avec tags (Urgent, Suivi, Info, OK)
-  **Mode sombre** — Interface adaptable, préférences persistées
-  **Design responsive** — Compatible desktop, tablette et mobile

---

##  Stack Technique

| Couche | Technologie |
|--------|-------------|
| Backend | Python 3.8+, Flask 2.x |
| IA / Deep Learning | TensorFlow 2.x, Keras, VGG16 |
| Base de données | MySQL 8.0 (via XAMPP) |
| Frontend | HTML5, CSS3 |
| Connecteur DB | mysql-connector-python |

---

##  Structure du Projet

```
skindiag/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
│
├── model/
│   └── vgg16_malignant_vs_benign.h5
│
├── static/
│   ├── style.css
│   └── uploads/
│
└── templates/
    ├── login.html
    ├── dashboard.html
    ├── predict.html
    ├── result.html
    ├── patients.html
    ├── analytics.html
    └── notes.html
```

---

##  Installation

### Prérequis

- Python 3.8+
- XAMPP (MySQL + Apache)
- Git

### 1. Cloner le dépôt

```bash
git clone https://github.com/VOTRE_USERNAME/skindiag.git
cd skindiag
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer la base de données

Démarrez XAMPP et exécutez ce SQL dans phpMyAdmin :

```sql
CREATE DATABASE skin_cancer_db;

USE skin_cancer_db;

CREATE TABLE users (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE patients (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100),
    age         INT,
    result      VARCHAR(50),
    probability FLOAT,
    image_path  VARCHAR(255),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username, password) VALUES ('admin', 'admin');
```

> La table `doctor_notes` est créée automatiquement au premier accès à `/notes`.

### 5. Ajouter le modèle IA

Placez le fichier `vgg16_malignant_vs_benign.h5` dans le dossier `model/`.

### 6. Configurer les variables d'environnement

Créez un fichier `.env` à la racine :

```
SECRET_KEY=votre_cle_secrete_ici
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=skin_cancer_db
```

### 7. Lancer l'application

```bash
python app.py
```

Ouvrez votre navigateur sur `http://localhost:5001`

---

##  Identifiants par défaut

| Champ | Valeur |
|-------|--------|
| Utilisateur | `admin` |
| Mot de passe | `admin` |

>  Modifiez ces identifiants avant tout déploiement en production.

---

##  Modèle IA

Le modèle est un réseau de neurones convolutif **VGG16** pré-entraîné sur ImageNet et fine-tuné sur un dataset de lésions cutanées dermoscopiques.

| Paramètre | Valeur |
|-----------|--------|
| Architecture | VGG16 (Transfer Learning) |
| Input | Image 224×224 px, RGB |
| Output | Probabilité [0, 1] |
| Seuil | 0.5 |
| Précision | ~98.4% |
| Classes | Benign / Malignant |

---

##  Dépendances

```
flask
tensorflow
numpy
mysql-connector-python
python-dotenv
Pillow
```

Générez le fichier avec :

```bash
pip freeze > requirements.txt
```

---

##  Sécurité

- Sessions Flask avec clé secrète
- Accès aux routes protégé par vérification de session
- Fichier `.env` exclu du versioning
- Modèle `.h5` et images patients exclus du dépôt GitHub

---
