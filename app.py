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
.boutons{
    text-align:center;
    margin-bottom:20px;
}
.boutons button{
    padding:10px 15px;
    margin:5px;
    border:none;
    border-radius:8px;
    cursor:pointer;
    background:#0066cc;
    color:white;
    font-weight:bold;
}

.boutons button:hover{
    background:#004999;
}
</style>
</head>
<body>

<h1>🏆 Coupe du Monde 2026</h1>
<div class="boutons">

<button onclick="filtrer('A')">A</button>
<button onclick="filtrer('B')">B</button>
<button onclick="filtrer('C')">C</button>
<button onclick="filtrer('D')">D</button>

<button onclick="filtrer('E')">E</button>
<button onclick="filtrer('F')">F</button>
<button onclick="filtrer('G')">G</button>
<button onclick="filtrer('H')">H</button>

<button onclick="filtrer('I')">I</button>
<button onclick="filtrer('J')">J</button>
<button onclick="filtrer('K')">K</button>
<button onclick="filtrer('L')">L</button>

<br><br>

<button onclick="filtrer('Round of 32')">32e</button>
<button onclick="filtrer('Round of 16')">16e</button>
<button onclick="filtrer('Quarter-finals')">Quarts</button>
<button onclick="filtrer('Semi-finals')">Demi</button>
<button onclick="filtrer('Third place play-off')">3e place</button>
<button onclick="filtrer('Final')">Finale</button>

<button onclick="filtrer('all')">Tous</button>

</div>
"""

# Ajout des matchs
for match in matches:

    html += f"""
        <div class="match" data-groupe="{match.get('groupe', '')}">
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
<script>

function filtrer(groupe){

    let matchs =
    document.querySelectorAll('.match');

    matchs.forEach(match => {

        if(groupe === 'all'){
            match.style.display='block';
        }

        else if(
            match.dataset.groupe === groupe
        ){
            match.style.display='block';
        }

        else{
            match.style.display='none';
        }

    });

}

</script>

</body>
</html>
"""

# Création du dossier site
Path("site").mkdir(exist_ok=True)

# Écriture du fichier
with open("site/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Site généré : site/index.html")