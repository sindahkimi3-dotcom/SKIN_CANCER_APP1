import os
import numpy as np
import mysql.connector
from flask import Flask, render_template, request, redirect, session, flash
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image


app = Flask(__name__)
app.secret_key = "secret"
 
UPLOAD_FOLDER = "static/uploads/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 
model = load_model("model/vgg16_malignant_vs_benign.h5")
 
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="skin_cancer_db"
)
cursor = db.cursor(dictionary=True)
 
 

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd  = request.form["password"]
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (user, pwd))
        result = cursor.fetchone()
        if result:
            session["user"] = user
            flash("Login réussi ✓", "success")
            return redirect("/dashboard")
        else:
            flash("Identifiants incorrects ✗", "danger")
    return render_template("login.html")
 
 

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
 
    cursor.execute("SELECT COUNT(*) AS total FROM patients")
    total_patients = cursor.fetchone()["total"]
 
    cursor.execute("""
        SELECT COUNT(*) AS cnt FROM patients
        WHERE MONTH(created_at) = MONTH(CURDATE())
          AND YEAR(created_at)  = YEAR(CURDATE())
    """)
    monthly_analyses = cursor.fetchone()["cnt"]
 
    return render_template("dashboard.html",
                           total_patients=total_patients,
                           monthly_analyses=monthly_analyses)
 


@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "user" not in session:
        return redirect("/")
 
    if request.method == "POST":
        try:
            name = request.form["name"]
            age  = request.form["age"]
            file = request.files["image"]
 
            if file.filename == "":
                flash("Veuillez choisir une image", "warning")
                return redirect("/predict")
 
            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(path)
 
            img = image.load_img(path, target_size=(224, 224))
            img = image.img_to_array(img)
            img = img / 255.0
            img = np.expand_dims(img, axis=0)
 
            pred   = model.predict(img)[0][0]
            result = "Malignant" if pred > 0.5 else "Benign"
 
            cursor.execute(
                "INSERT INTO patients (name, age, result, probability, image_path) VALUES (%s, %s, %s, %s, %s)",
                (name, age, result, float(pred), path)
            )
            db.commit()
 
            flash("Analyse réussie ✓", "success")
            return render_template("result.html", result=result, prob=round(pred * 100, 2), img=path)
 
        except Exception as e:
            print(f"Erreur système : {e}")
            flash("Erreur système ✗", "danger")
            return redirect("/predict")
 
    return render_template("predict.html")
 
 

@app.route("/patients")
def patients():
    if "user" not in session:
        return redirect("/")
    cursor.execute("SELECT * FROM patients ORDER BY created_at DESC")
    data = cursor.fetchall()
    return render_template("patients.html", patients=data)
 
 

@app.route("/analytics")
def analytics():
    if "user" not in session:
        return redirect("/")
 

    cursor.execute("SELECT COUNT(*) AS total FROM patients")
    total_patients = cursor.fetchone()["total"]
 
    cursor.execute("""
        SELECT COUNT(*) AS cnt FROM patients
        WHERE MONTH(created_at) = MONTH(CURDATE())
          AND YEAR(created_at)  = YEAR(CURDATE())
    """)
    monthly_analyses = cursor.fetchone()["cnt"]
 
    cursor.execute("SELECT AVG(probability) AS avg_conf FROM patients")
    row = cursor.fetchone()
    avg_confidence = round((row["avg_conf"] or 0) * 100, 1)
 
  
    cursor.execute("SELECT COUNT(*) AS cnt FROM patients WHERE result = 'Benign'")
    benign = cursor.fetchone()["cnt"]
 
    cursor.execute("SELECT COUNT(*) AS cnt FROM patients WHERE result = 'Malignant'")
    malignant = cursor.fetchone()["cnt"]
 
    unknown = total_patients - benign - malignant
 

    cursor.execute("SELECT * FROM patients ORDER BY created_at DESC LIMIT 10")
    recent_patients = cursor.fetchall()
 
    stats = {
        "total_patients":   total_patients,
        "monthly_analyses": monthly_analyses,
        "avg_confidence":   avg_confidence,
        "benign":           benign,
        "malignant":        malignant,
        "unknown":          unknown,
    }
 
    return render_template("analytics.html", stats=stats, recent_patients=recent_patients)
 
 

@app.route("/notes")
def notes():
    if "user" not in session:
        return redirect("/")
 

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctor_notes (
            id           INT AUTO_INCREMENT PRIMARY KEY,
            author       VARCHAR(100),
            patient_name VARCHAR(100),
            tag          VARCHAR(20) DEFAULT 'info',
            text         TEXT,
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
 
    cursor.execute("SELECT * FROM doctor_notes ORDER BY created_at DESC")
    all_notes = cursor.fetchall()
 
    return render_template("notes.html", notes=all_notes)
 
 
@app.route("/notes/add", methods=["POST"])
def notes_add():
    if "user" not in session:
        return redirect("/")
 
    patient_name = request.form.get("patient_name", "").strip()
    tag          = request.form.get("tag", "info")
    text         = request.form.get("text", "").strip()
    author       = session["user"]
 
    if not patient_name or not text:
        flash("Veuillez remplir tous les champs ✗", "danger")
        return redirect("/notes")
 
    cursor.execute(
        "INSERT INTO doctor_notes (author, patient_name, tag, text) VALUES (%s, %s, %s, %s)",
        (author, patient_name, tag, text)
    )
    db.commit()
    flash("Note ajoutée avec succès ✓", "success")
    return redirect("/notes")
 
 
@app.route("/notes/delete/<int:note_id>")
def notes_delete(note_id):
    if "user" not in session:
        return redirect("/")
    cursor.execute("DELETE FROM doctor_notes WHERE id = %s", (note_id,))
    db.commit()
    flash("Note supprimée ✓", "info")
    return redirect("/notes")
 

@app.route("/logout")
def logout():
    session.clear()
    flash("Déconnecté", "info")
    return redirect("/")
 
 
if __name__ == "__main__":
    app.run(debug=True, port=5001)
