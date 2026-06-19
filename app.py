import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

API_BASE = "http://worldcup26.ir:3050"
MATCHES_FILE = Path("matches.json")


def fetch_json(url):
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        },
    )
    with urlopen(req, timeout=60) as response:
        return json.load(response)


def parse_api_datetime(value):
    if not value:
        return "", ""

    if " " in value:
        date_part, time_part = value.split(" ", 1)
    else:
        date_part, time_part = value, ""

    if "/" in date_part:
        day, month, year = date_part.split("/")
        date_part = f"{year}-{int(month):02d}-{int(day):02d}"

    return date_part, time_part.strip()


def parse_scorer_entry(entry):
    text = (entry or "").strip()
    match = re.match(r"^(.*)\s+(\d+(?:\+\d+)?['’])$", text)
    if match:
        return {
            "name": match.group(1).strip(),
            "minute": match.group(2).strip()
        }
    return {"name": text, "minute": ""}


def parse_scorer_list(raw_value):
    if not raw_value or raw_value in ("null", "None", "[]", "{}"):
        return []

    text = str(raw_value).replace("“", '"').replace("”", '"')
    text = text.replace("{", "[").replace("}", "]")

    try:
        parsed = json.loads(text)
    except Exception:
        parsed = []

    if isinstance(parsed, str):
        parsed = [parsed]

    return [parse_scorer_entry(item) for item in parsed if item]


def load_matches_from_api():
    stage_labels = {
        "r32": "Seizièmes de finale",
        "r16": "Huitièmes de finale",
        "qf": "Quarts de finale",
        "sf": "Demi-finales",
        "third": "Match pour la 3e place",
        "final": "Finale",
    }

    try:
        payload = fetch_json(f"{API_BASE}/get/games")
        raw_games = payload.get("games", [])
        matches = []

        for item in raw_games:
            match_type = item.get("type")
            finished = str(item.get("finished", "")).strip().upper() in {"TRUE", "1", "YES", "Y"}
            date_part, time_part = parse_api_datetime(item.get("local_date", ""))

            base_match = {
                "equipe1": item.get("home_team_name_en") or "TBD",
                "equipe2": item.get("away_team_name_en") or "TBD",
                "date": date_part,
                "heure": time_part,
                "termine": finished,
                "score": f"{item.get('home_score', 0)} - {item.get('away_score', 0)}" if finished else "Non défini",
            }

            if match_type == "group":
                base_match["groupe"] = item.get("group") or "A"
            elif match_type in stage_labels:
                base_match["groupe"] = stage_labels[match_type]
            else:
                continue

            base_match["scorers"] = {
                "home": parse_scorer_list(item.get("home_scorers")),
                "away": parse_scorer_list(item.get("away_scorers")),
            }
            matches.append(base_match)

        MATCHES_FILE.write_text(
            json.dumps(matches, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print("matches.json généré depuis l'API")
        return matches
    except Exception as e:
        print(f"Erreur d'accès à l'API: {e}")
        if MATCHES_FILE.exists():
            with MATCHES_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        raise


def load_team_flags():
    flags = {}
    try:
        teams_payload = fetch_json(f"{API_BASE}/get/teams")
        for team in teams_payload.get("teams", []):
            if team.get("flag"):
                if team.get("name_en"):
                    flags[team["name_en"]] = team["flag"]
                if team.get("name_fa"):
                    flags[team["name_fa"]] = team["flag"]
    except Exception:
        pass
    return flags


matches = load_matches_from_api()
flags = load_team_flags()


def build_scorers_leaderboard(matches):
    leaderboard = {}

    for match in matches:
        for side, team_name in (("home", match.get("equipe1")), ("away", match.get("equipe2"))):
            for scorer in match.get("scorers", {}).get(side, []):
                name = scorer.get("name", "")
                if not name:
                    continue
                entry = leaderboard.setdefault(
                    name,
                    {
                        "buts": 0,
                        "equipe": team_name,
                        "minutes": [],
                    },
                )
                entry["buts"] += 1
                if scorer.get("minute"):
                    entry["minutes"].append(scorer["minute"])
                entry["equipe"] = team_name

    return sorted(
        leaderboard.items(),
        key=lambda item: (-item[1]["buts"], item[0])
    )


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
        return f'<img src="{url}" class="flag" alt="{team}">'
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
    background:
        radial-gradient(circle at top, #e8f5ff 0%, #f7f9ff 32%, #eef8f3 100%);
    max-width: 1100px;
    margin: auto;
    padding: 28px 18px 48px;
    color: #16324f;
}

h1 {
    text-align: center;
    margin: 0 0 18px;
    color: #0b2342;
}

.match {
    background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 16px;
    box-shadow: 0 8px 18px rgba(15, 38, 75, 0.08);
    border: 1px solid #dde9f7;
}

.groupe {
    font-size: 0.82rem;
    color: #5f7b9a;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.teams {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    font-size: 1rem;
    font-weight: 700;
    margin: 12px 0;
}

.team-block {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1;
    min-width: 0;
}

.team-block.right {
    justify-content: flex-end;
}

.team-name {
    display: flex;
    align-items: center;
    gap: 8px;
}

.score-center {
    min-width: 84px;
    text-align: center;
    background: #eef7ff;
    border-radius: 999px;
    padding: 6px 10px;
    color: #0d5bb7;
    font-size: 0.92rem;
    font-weight: 800;
}

.score {
    color: #0a9157;
    font-weight: bold;
}

.future {
    color: #0d5bb7;
    font-weight: 700;
}

.date {
    margin-top: 6px;
    color: #517091;
    font-size: 0.92rem;
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
    width:26px;
    height:18px;
    vertical-align:middle;
    border-radius:4px;
    box-shadow:0 2px 6px rgba(0,0,0,0.15);
    object-fit: cover;
    flex: 0 0 auto;
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
    background: white;
    border-radius: 12px;
    overflow: hidden;
}

th, td {
    text-align: center;
    padding: 12px 10px;
}

th {
    background: linear-gradient(90deg, #0d5bb7, #0a8bcb);
    color: white;
}

tr:nth-child(even) td {
    background: #f9fbff;
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
    background: white;
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 6px 16px rgba(15, 38, 75, 0.06);
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
    gap: 10px;
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
.scorers-btn {
    background: #1f8f53;
    border: none;
    padding: 10px 16px;
    border-radius: 10px;
    cursor: pointer;
    font-weight: bold;
    height: 40px;
    display: flex;
    align-items: center;
    color: white;
}
.scorers-btn:hover {
    background: #176d3e;
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
    <button class="scorers-btn"
            onclick="window.location.href='scorers.html'">
        ⚽ Buteurs
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
            <div class="team-block">
                <span class="team-name">{flag(match['equipe1'])} <span>{match['equipe1']}</span></span>
            </div>
            <div class="score-center">{match['score']}</div>
            <div class="team-block right">
                <span class="team-name">{flag(match['equipe2'])} <span>{match['equipe2']}</span></span>
            </div>
        </div>
        <div class="score">Match terminé</div>
        <div class="date">{match['date']}</div>
        """
    else:
        html += f"""
        <div class="teams">
            <div class="team-block">
                <span class="team-name">{flag(match['equipe1'])} <span>{match['equipe1']}</span></span>
            </div>
            <div class="score-center">VS</div>
            <div class="team-block right">
                <span class="team-name">{flag(match['equipe2'])} <span>{match['equipe2']}</span></span>
            </div>
        </div>
        <div class="future">Match à venir</div>
        <div class="date">{match['date']} - {match.get('heure', 'Heure non définie')}</div>
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

scorers_rows = build_scorers_leaderboard(matches)
scorers_html = ""
for name, stats in scorers_rows:
    minutes = ", ".join(stats["minutes"][:3])
    if len(stats["minutes"]) > 3:
        minutes += ", ..."
    scorers_html += f"""
    <tr>
        <td>{name}</td>
        <td>{stats['equipe']}</td>
        <td>{stats['buts']}</td>
        <td>{minutes}</td>
    </tr>
    """

scorers_page = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Classement des buteurs</title>
<style>
body {{
    font-family: Arial, sans-serif;
    background: #f4f4f4;
    margin: 0;
    padding: 24px;
}}
.container {{
    max-width: 1100px;
    margin: 0 auto;
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}}
h1 {{
    text-align: center;
    margin-top: 0;
}}
button {{
    margin-bottom: 16px;
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
table {{
    width: 100%;
    border-collapse: collapse;
}}
th, td {{
    text-align: left;
    padding: 12px;
    border-bottom: 1px solid #e5e7eb;
}}
th {{
    background: #f8fafc;
}}
.score {{
    font-weight: bold;
    color: #0b8a46;
}}
</style>
</head>
<body>
<div class="container">
    <button onclick="window.location.href='index.html'">← Retour au calendrier</button>
    <h1>⚽ Classement des buteurs</h1>
    <table>
        <thead>
            <tr>
                <th>Joueur</th>
                <th>Équipe</th>
                <th>Buts</th>
                <th>Minutes</th>
            </tr>
        </thead>
        <tbody>
            {scorers_html}
        </tbody>
    </table>
</div>
</body>
</html>
"""

Path("site").mkdir(exist_ok=True)
with open("site/scorers.html", "w", encoding="utf-8") as f:
    f.write(scorers_page)

print("scorers généré : site/scorers.html")

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
        <div class="match-teams">
            <div class="team-row">{flag(equipe1)} <span>{equipe1}</span></div>
            <div class="team-row">{flag(equipe2)} <span>{equipe2}</span></div>
        </div>
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
    background:
        radial-gradient(circle at top, #e9f6ff 0%, #f9fafc 35%, #eefbf5 100%);
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
    background: linear-gradient(180deg, #ffffff 0%, #f6faff 100%);
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 6px 18px rgba(19, 34, 56, 0.08);
    border: 1px solid #dce8f7;
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
    background: linear-gradient(180deg, #f9fbff 0%, #eef7ff 100%);
    border: 1px solid #dfe7f2;
    border-radius: 14px;
    padding: 12px;
    min-height: 100px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 8px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.6);
}}

.match-teams {{
    font-weight: 700;
    font-size: 0.92rem;
    line-height: 1.3;
    display: flex;
    flex-direction: column;
    gap: 6px;
}}

.team-row {{
    display: flex;
    align-items: center;
    gap: 8px;
}}

.team-row span {{
    color: #223652;
    font-weight: 700;
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
<button onclick="window.location.href='scorers.html'">⚽ Buteurs</button>
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