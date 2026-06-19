import json
from pathlib import Path

# Lecture des données
with open("matches.json", "r", encoding="utf-8") as f:
    matches = json.load(f)
flags = {
    "Canada": "https://flagcdn.com/w40/ca.png",
    "États-Unis": "https://flagcdn.com/w40/us.png",
    "Mexique": "https://flagcdn.com/w40/mx.png",

    "Arabie saoudite": "https://flagcdn.com/w40/sa.png",
    "Australie": "https://flagcdn.com/w40/au.png",
    "Irak": "https://flagcdn.com/w40/iq.png",
    "Japon": "https://flagcdn.com/w40/jp.png",
    "Jordanie": "https://flagcdn.com/w40/jo.png",
    "Ouzbékistan": "https://flagcdn.com/w40/uz.png",
    "Qatar": "https://flagcdn.com/w40/qa.png",
    "République de Corée": "https://flagcdn.com/w40/kr.png",
    "RI Iran": "https://flagcdn.com/w40/ir.png",

    "Afrique du Sud": "https://flagcdn.com/w40/za.png",
    "Algérie": "https://flagcdn.com/w40/dz.png",
    "Cap-Vert": "https://flagcdn.com/w40/cv.png",
    "Côte d'Ivoire": "https://flagcdn.com/w40/ci.png",
    "Égypte": "https://flagcdn.com/w40/eg.png",
    "Ghana": "https://flagcdn.com/w40/gh.png",
    "Maroc": "https://flagcdn.com/w40/ma.png",
    "RD Congo": "https://flagcdn.com/w40/cd.png",
    "Sénégal": "https://flagcdn.com/w40/sn.png",
    "Tunisie": "https://flagcdn.com/w40/tn.png",

    "Curaçao": "https://flagcdn.com/w40/cw.png",
    "Haïti": "https://flagcdn.com/w40/ht.png",
    "Panama": "https://flagcdn.com/w40/pa.png",
    "Panamá": "https://flagcdn.com/w40/pa.png",

    "Argentine": "https://flagcdn.com/w40/ar.png",
    "Brésil": "https://flagcdn.com/w40/br.png",
    "Colombie": "https://flagcdn.com/w40/co.png",
    "Équateur": "https://flagcdn.com/w40/ec.png",
    "Paraguay": "https://flagcdn.com/w40/py.png",
    "Uruguay": "https://flagcdn.com/w40/uy.png",

    "Nouvelle-Zélande": "https://flagcdn.com/w40/nz.png",

    "Allemagne": "https://flagcdn.com/w40/de.png",
    "Angleterre": "https://flagcdn.com/w40/gb.png",
    "Autriche": "https://flagcdn.com/w40/at.png",
    "Belgique": "https://flagcdn.com/w40/be.png",
    "Bosnie-et-Herzégovine": "https://flagcdn.com/w40/ba.png",
    "Bosnia and Herzegovina": "https://flagcdn.com/w40/ba.png",
    "Croatie": "https://flagcdn.com/w40/hr.png",
    "Écosse": "https://flagcdn.com/w40/gb-sct.png",
    "Espagne": "https://flagcdn.com/w40/es.png",
    "France": "https://flagcdn.com/w40/fr.png",
    "Norvège": "https://flagcdn.com/w40/no.png",
    "Pays-Bas": "https://flagcdn.com/w40/nl.png",
    "Portugal": "https://flagcdn.com/w40/pt.png",
    "Suède": "https://flagcdn.com/w40/se.png",
    "Suisse": "https://flagcdn.com/w40/ch.png",
    "Tchéquie": "https://flagcdn.com/w40/cz.png",
    "Turquie": "https://flagcdn.com/w40/tr.png",
    "Bosnie-Herzégovine": "https://flagcdn.com/w40/ba.png",
    "Iran": "https://flagcdn.com/w40/ir.png",
    "Corée du Sud": "https://flagcdn.com/w40/kr.png"
}
def build_phase(matches, phase):
    html = ""
    phase_matches = [m for m in matches if m["groupe"] == phase]

    for m in phase_matches:
        eq1 = m.get("equipe1", "TBD")
        eq2 = m.get("equipe2", "TBD")

        if m["termine"]:
            status = '<div class="score">Match terminé</div>'
        else:
            status = '<div class="future">Match à venir</div>'

        html += f"""
        <div class="match">
            <div class="connector"></div>
            <div class="teams">
                {eq1} - {eq2}
            </div>

            {status}

            <div class="date">
                {m.get("date", "")} - {m.get("heure", "")}
            </div>
        </div>
        """

    return html

def build_match_card(match):
    eq1 = match.get("equipe1", "TBD")
    eq2 = match.get("equipe2", "TBD")
    status = '<div class="score">Match terminé</div>' if match.get("termine") else '<div class="future">Match à venir</div>'
    return f"""
    <div class="match">
        <div class="connector"></div>
        <div class="teams">{eq1} - {eq2}</div>
        {status}
        <div class="date">{match.get("date", "")} - {match.get("heure", "")}</div>
    </div>
    """

def build_quarter_branches(matches):
    huit = [m for m in matches if m["groupe"] == "Huitièmes de finale"]
    quarts = [m for m in matches if m["groupe"] == "Quarts de finale"]
    html = ""

    for i in range(len(quarts)):
        left = huit[i * 2]
        right = huit[i * 2 + 1]
        html += f"""
        <div class="branch branch-quarter">
            <div class="branch-side">{build_match_card(left)}</div>
            <div class="branch-connector">
                <span class="line"></span>
                <span class="arrow">➜</span>
            </div>
            <div class="branch-center">{build_match_card(quarts[i])}</div>
            <div class="branch-connector">
                <span class="line"></span>
                <span class="arrow">➜</span>
            </div>
            <div class="branch-side">{build_match_card(right)}</div>
        </div>
        """

    return html

def build_demi_branches(matches):
    quarts = [m for m in matches if m["groupe"] == "Quarts de finale"]
    demis = [m for m in matches if m["groupe"] == "Demi-finales"]
    html = ""

    for i in range(len(demis)):
        left = quarts[i * 2]
        right = quarts[i * 2 + 1]
        html += f"""
        <div class="branch branch-demi">
            <div class="branch-side">{build_match_card(left)}</div>
            <div class="branch-connector">
                <span class="line"></span>
                <span class="arrow">➜</span>
            </div>
            <div class="branch-center">{build_match_card(demis[i])}</div>
            <div class="branch-connector">
                <span class="line"></span>
                <span class="arrow">➜</span>
            </div>
            <div class="branch-side">{build_match_card(right)}</div>
        </div>
        """

    return html

def build_final_branch(matches):
    demis = [m for m in matches if m["groupe"] == "Demi-finales"]
    finale = [m for m in matches if m["groupe"] == "Finale"]
    html = ""

    if finale:
        left = demis[0]
        right = demis[1]
        html += f"""
        <div class="branch branch-final">
            <div class="branch-side">{build_match_card(left)}</div>
            <div class="branch-connector">
                <span class="line"></span>
                <span class="arrow">➜</span>
            </div>
            <div class="branch-center">{build_match_card(finale[0])}</div>
            <div class="branch-connector">
                <span class="line"></span>
                <span class="arrow">➜</span>
            </div>
            <div class="branch-side">{build_match_card(right)}</div>
        </div>
        """

    return html

def flag(team):
    url = flags.get(team)
    if url:
        return f'<img src="{url}" class="flag">'
    return ""
def calculer_classement(matches, groupe):
    classement = {}

    # 1) AJOUTER TOUTES LES ÉQUIPES DU GROUPE (même sans match joué)
    for m in matches:
        if m["groupe"] != groupe:
            continue

        classement.setdefault(m["equipe1"], {
            "pts": 0,
            "vic": 0,
            "nul": 0,
            "def": 0
        })

        classement.setdefault(m["equipe2"], {
            "pts": 0,
            "vic": 0,
            "nul": 0,
            "def": 0
        })

    # 2) ensuite seulement tu calcules les matchs joués
    for m in matches:
        if m["groupe"] != groupe:
            continue
        if not m["termine"]:
            continue

        eq1 = m["equipe1"]
        eq2 = m["equipe2"]

        s1, s2 = map(int, m["score"].replace(" ", "").split("-"))

        if s1 > s2:
            classement[eq1]["pts"] += 3
            classement[eq1]["vic"] += 1
            classement[eq2]["def"] += 1

        elif s2 > s1:
            classement[eq2]["pts"] += 3
            classement[eq2]["vic"] += 1
            classement[eq1]["def"] += 1

        else:
            classement[eq1]["pts"] += 1
            classement[eq2]["pts"] += 1
            classement[eq1]["nul"] += 1
            classement[eq2]["nul"] += 1

    return sorted(
        classement.items(),
        key=lambda x: (x[1]["pts"], x[1]["vic"], -x[1]["def"]),
        reverse=True
    )

classements_par_groupe = {}

for m in matches:
    g = m["groupe"]
    if g not in classements_par_groupe:
        classements_par_groupe[g] = calculer_classement(matches, g)
classement_html = ""

for groupe, classement in classements_par_groupe.items():
    classement_html += f'<div class="classement-groupe" data-groupe="{groupe}" style="display:none;">'
    classement_html += f"<h3>Classement Groupe {groupe}</h3>"

    classement_html += """
    <table style="
        width:100%;
        border-collapse:collapse;
        background:white;
        border-radius:10px;
        overflow:hidden;
        box-shadow:0 2px 8px rgba(0,0,0,0.1);
    ">
    <tr style="background:#0066cc; color:white;">
        <th>#</th>
        <th>Équipe</th>
        <th>Pts</th>
        <th>V</th>
        <th>N</th>
        <th>D</th>
    </tr>
    """

    position = 1

    for equipe, stats in classement:
        if position == 1:
            medal = "🥇"
        elif position == 2:
            medal = "🥈"
        elif position == 3:
            medal = "🥉"
        else:
            medal = str(position)

        classement_html += f"""
        <tr style="border-bottom:1px solid #eee;">
    
            <td style="width:50px; text-align:center; font-size:18px;">
                {medal}
            </td>

            <td style="text-align:left; display:flex; align-items:center; gap:8px;">
                {flag(equipe)} <span>{equipe}</span>
            </td>

            <td><b>{stats['pts']}</b></td>
            <td>{stats['vic']}</td>
            <td>{stats['nul']}</td>
            <td>{stats['def']}</td>

        </tr>
        """
        position += 1

    classement_html += "</table></div>"
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
.flag{
    width:22px;
    height:16px;
    vertical-align:middle;
    margin:0 6px;
    border-radius:3px;
    box-shadow:0 1px 3px rgba(0,0,0,0.2);
}
.dropdown {
    position: relative;
    display: flex;
    align-items: center;
}

.dropbtn {
    background-color: #0066cc;
    color: white;
    padding: 10px 16px;
    font-size: 16px;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    height: 40px;
    display: flex;
    align-items: center;
}

.dropbtn:hover {
    background-color: #004999;
}

.dropdown-content {
    display: none;
    position: absolute;
    background-color: white;
    min-width: 220px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    border-radius: 10px;
    z-index: 1000;
    padding: 10px;
}

.dropdown-content button {
    width: 100%;
    padding: 8px;
    border: none;
    background: none;
    text-align: left;
    cursor: pointer;
    border-radius: 6px;
}

.dropdown-content button:hover {
    background-color: #f0f0f0;
}

.dropdown:hover .dropdown-content {
    display: block;
}
table {
    border-collapse: collapse;
    width: 100%;
    table-layout: fixed;
}

th, td {
    text-align: center;
    padding: 10px;
}

td:nth-child(2) {
    text-align: left;
}
td {
    font-variant-numeric: tabular-nums;
}
#classement {
    margin-bottom: 30px;
}

.classement-groupe {
    margin-bottom: 30px;
}
.toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between; /* clé */
    gap: 12px;
    margin-bottom: 20px;
}

/* bloc gauche = filtre */
.toolbar-left {
    display: flex;
    align-items: center;
    gap: 10px;
    position: relative;
}

/* dropdown corrigé */
.dropdown {
    position: relative;
    display: flex;
    align-items: center;
}

/* menu corrigé (évite de sortir écran) */
.dropdown-content {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    background-color: white;
    min-width: 220px;
    max-height: 300px;
    overflow-y: auto; /* IMPORTANT */
    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    border-radius: 10px;
    z-index: 1000;
    padding: 10px;
}

/* bouton phase finale à droite */
.toolbar-right {
    display: flex;
    align-items: center;
}
.bracket-btn {
    background: gold;
    border: none;
    padding: 10px 16px;
    border-radius: 10px;
    cursor: pointer;
    font-weight: bold;
    height: 40px;
    display: flex;
    align-items: center;
}

.bracket-btn:hover {
    background: #e6c200;
}
</style>
</head>
<body>
<div id="classement"></div>
</div>

<h1>🏆 Coupe du Monde 2026</h1>

<div class="toolbar-left">

    <div class="dropdown">
        <button class="dropbtn">🎛️ Filtrer</button>

        <div class="dropdown-content">
            <button onclick="filtrer('A')">Groupe A</button>
            <button onclick="filtrer('B')">Groupe B</button>
            <button onclick="filtrer('C')">Groupe C</button>
            <button onclick="filtrer('D')">Groupe D</button>
            <button onclick="filtrer('E')">Groupe E</button>
            <button onclick="filtrer('F')">Groupe F</button>
            <button onclick="filtrer('G')">Groupe G</button>
            <button onclick="filtrer('H')">Groupe H</button>
            <button onclick="filtrer('I')">Groupe I</button>
            <button onclick="filtrer('J')">Groupe J</button>
            <button onclick="filtrer('K')">Groupe K</button>
            <button onclick="filtrer('L')">Groupe L</button>
            
            <hr>
            
            <button onclick="filtrer('Seizièmes de finale')">Seizièmes</button>
            <button onclick="filtrer('Huitièmes de finale')">Huitièmes</button>
            <button onclick="filtrer('Quarts de finale')">Quarts</button>
            <button onclick="filtrer('Demi-finales')">Demi-finales</button>
            <button onclick="filtrer('Match pour la 3e place')">3e place</button>
            <button onclick="filtrer('Finale')">Finale</button>

            <hr>

            <button onclick="filtrer('all')">Tous</button>
        </div>
    </div>

</div>

<div class="toolbar-right">
    <button class="bracket-btn"
            onclick="window.location.href='bracket.html'">
        🏆 Phase finale
    </button>
</div>

</div>

<div id="classement">
    """ + classement_html + """
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
            {flag(match["equipe1"])} {match["equipe1"]} {match["score"]}  {match["equipe2"]} {flag(match["equipe2"])}
        </div>
        <div class="score">Match terminé</div>
        <div class="date">{match["date"]}</div>
        """
    else:
        html += f"""
        <div class="teams">
            {flag(match["equipe1"])} {match["equipe1"]} -  {match["equipe2"]} {flag(match["equipe2"])}
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

window.onload = function() {
    filtrer('all');
};

function filtrer(groupe){

    let matchs = document.querySelectorAll('.match');
    let classements = document.querySelectorAll('.classement-groupe');

    matchs.forEach(match => {

        if(groupe === 'all' || match.dataset.groupe === groupe){
            match.style.display = 'block';
        } else {
            match.style.display = 'none';
        }

    });

classements.forEach(c => {

    if(
        groupe === 'all' ||
        groupe === 'Seizièmes de finale' ||
        groupe === 'Huitièmes de finale' ||
        groupe === 'Quarts de finale' ||
        groupe === 'Demi-finales' ||
        groupe === 'Match pour la 3e place' ||
        groupe === 'Finale'
    ){
        c.style.display = 'none';
    }
    else if(c.dataset.groupe === groupe){
        c.style.display = 'block';
    }
    else{
        c.style.display = 'none';
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

def render_match_card(match):
    equipe1 = match.get("equipe1", "TBD")
    equipe2 = match.get("equipe2", "TBD")
    date = match.get("date", "")
    heure = match.get("heure", "")

    if match.get("termine") and match.get("score") not in (None, "", " "):
        status = f'<div class="match-status result">{match.get("score", "")}</div>'
    else:
        status = '<div class="match-status upcoming">Match à venir</div>'

    if heure:
        time = f'<div class="match-time">{date} · {heure}</div>'
    else:
        time = f'<div class="match-time">{date}</div>'

    return f"""
    <div class="match-card">
        <div class="match-teams">{equipe1} <span>vs</span> {equipe2}</div>
        {status}
        {time}
    </div>
    """


def render_stage_column(title, matches):
    cards = ''.join(render_match_card(match) for match in matches)
    return f"""
    <section class="landscape-column">
        <h2>{title}</h2>
        <div class="round-list">{cards}</div>
    </section>
    """


huitiemes = [m for m in matches if m["groupe"] == "Huitièmes de finale"]
quarts = [m for m in matches if m["groupe"] == "Quarts de finale"]
demis = [m for m in matches if m["groupe"] == "Demi-finales"]
finale = [m for m in matches if m["groupe"] == "Finale"]
troisieme = [m for m in matches if m["groupe"] == "Match pour la 3e place"]

bracket_html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Phase finale</title>
<style>
* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    padding: 24px;
    font-family: Arial, sans-serif;
    background: #eef3f9;
    color: #132238;
    min-width: 1400px;
}}

button {{
    margin: 0 0 16px;
    padding: 10px 14px;
    border: 0;
    border-radius: 10px;
    background: #0a66c2;
    color: white;
    font-weight: 700;
    cursor: pointer;
}}

button:hover {{
    background: #084f97;
}}

h1 {{
    margin: 0 0 18px;
    text-align: center;
    font-size: 2rem;
}}

.bracket-tree {{
    width: 100%;
    margin: 0 auto;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    gap: 16px;
    overflow-x: auto;
    align-items: flex-start;
    padding-bottom: 20px;
}}

.landscape-column {{
    min-width: 280px;
    flex: 1 1 0;
    background: white;
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 6px 18px rgba(19, 34, 56, 0.08);
}}

.landscape-column h2 {{
    margin: 0 0 12px;
    font-size: 0.95rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #4f617d;
}}

.round-list {{
    display: flex;
    flex-direction: column;
    gap: 12px;
}}

.match-card {{
    background: #f9fbff;
    border: 1px solid #dfe7f2;
    border-radius: 12px;
    padding: 12px;
    min-height: 90px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 6px;
}}

.match-teams {{
    font-weight: 700;
    font-size: 0.95rem;
    line-height: 1.3;
}}

.match-teams span {{
    color: #60758f;
    font-weight: 600;
}}

.match-status {{
    font-size: 0.82rem;
    font-weight: 700;
}}

.match-status.result {{
    color: #0b8a46;
}}

.match-status.upcoming {{
    color: #0a66c2;
}}

.match-time {{
    font-size: 0.78rem;
    color: #5b6d86;
}}
</style>
</head>
<body>
<button onclick="window.location.href='index.html'">← Retour aux matchs</button>
<h1>🏆 Phase finale</h1>

<div class="bracket-tree">
    {render_stage_column('Huitièmes de finale', huitiemes)}
    {render_stage_column('Quarts de finale', quarts)}
    {render_stage_column('Demi-finales', demis)}
    <section class="landscape-column finale-block">
        <h2>Finale</h2>
        <div class="round-list">{''.join(render_match_card(match) for match in finale)}</div>
    </section>
    <section class="landscape-column third-place-block">
        <h2>3e place</h2>
        <div class="round-list">{''.join(render_match_card(match) for match in troisieme)}</div>
    </section>
</div>
</body>
</html>
"""

Path("site").mkdir(exist_ok=True)

with open("site/bracket.html", "w", encoding="utf-8") as f:
    f.write(bracket_html)

print("bracket généré")