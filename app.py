import json
from pathlib import Path

# Lecture des données
with open("matches.json", "r", encoding="utf-8") as f:
    matches = json.load(f)

# Début du HTML
html = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Coupe du Monde 2026</title>

<style>
body {
    font-family: Arial, sans-serif;
    background: #f4f4f4;
    max-width: 1000px;
    margin: auto;
    padding: 20px;
}

h1 {
    text-align: center;
}

.match {
    background: white;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

.groupe {
    font-size: 0.9rem;
    color: #666;
}

.teams {
    font-size: 1.2rem;
    font-weight: bold;
    margin: 8px 0;
}

.score {
    color: green;
    font-weight: bold;
}

.future {
    color: #0055cc;
}

.date {
    margin-top: 5px;
}
</style>
</head>
<body>

<h1>🏆 Coupe du Monde 2026</h1>
"""

# Ajout des matchs
for match in matches:

    html += f"""
    <div class="match">
        <div class="groupe">{match.get("groupe", "")}</div>
    """

    if match["termine"]:
        html += f"""
        <div class="teams">
            {match["equipe1"]} {match["score"]} {match["equipe2"]}
        </div>
        <div class="score">Match terminé</div>
        <div class="date">{match["date"]}</div>
        """
    else:
        html += f"""
        <div class="teams">
            {match["equipe1"]} - {match["equipe2"]}
        </div>
        <div class="future">
            Match à venir
        </div>
        <div class="date">
            {match["date"]} - {match.get("heure", "Heure non définie")}
        </div>
        """

    html += "</div>"

# Fin du HTML
html += """
</body>
</html>
"""

# Création du dossier site
Path("site").mkdir(exist_ok=True)

# Écriture du fichier
with open("site/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Site généré : site/index.html")