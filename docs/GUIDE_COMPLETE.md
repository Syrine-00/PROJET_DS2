# Guide Complet — Explication de Tout le Code

**Projet:** Orchestration Multi-Agent Sécurisée pour l'Économie Tunisienne  
**Cours:** Problem Solving — 2BIS  
**Semaine:** 2 (Core Implementation + Scenario 1)

---

## Table des Matières

1. [Vue d'ensemble du système](#1-vue-densemble-du-système)
2. [Architecture](#2-architecture)
3. [Couche de sécurité](#3-couche-de-sécurité)
4. [Schémas de validation](#4-schémas-de-validation)
5. [Outils (Tools)](#5-outils-tools)
6. [Orchestrateur](#6-orchestrateur)
7. [Tests](#7-tests)
8. [Interface graphique](#8-interface-graphique)
9. [Comment tout fonctionne ensemble](#9-comment-tout-fonctionne-ensemble)

---

## 1. Vue d'ensemble du système

### Qu'est-ce qu'on a construit ?

Un système d'orchestration multi-agent qui analyse des données touristiques en Tunisie de manière **sécurisée**, **fiable** et **observable**.

### Problème résolu

Les systèmes d'agents IA échouent souvent en production à cause de :
- Appels d'outils non validés (mauvais arguments)
- Failles de sécurité (traversée de chemin, hôtes non autorisés)
- Boucles infinies ou échecs non gérés
- État partagé entre exécutions parallèles

Notre système résout tout ça.

### Flux principal

```
Utilisateur → Tâche → Planner → Executor → Critic → Résultat
                         ↓          ↓         ↓
                      Backtracking Tools  Validation
```

---

## 2. Architecture

### Les 3 agents principaux

```
┌─────────────────────────────────────────────────────────┐
│                     RunManager                          │
│  (Orchestre tout le processus)                         │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   ┌─────────┐      ┌──────────┐      ┌─────────┐
   │ Planner │      │ Executor │      │ Critic  │
   └─────────┘      └──────────┘      └─────────┘
        │                 │                 │
        │                 │                 │
   Backtracking      Appelle les       Valide le
   pour trouver      outils avec       résultat
   un plan           validation        final
   faisable          stricte
```

### Fichiers créés

```
PROJET_DS2/
├── security/
│   └── allow_list.py          # Validation chemin + hôtes HTTP
├── tools/
│   ├── schemas.py             # Modèles Pydantic
│   ├── read_csv_tool.py       # Lecture CSV sécurisée
│   ├── compute_kpis.py        # Calcul des KPIs
│   ├── api_tool.py            # Appels HTTP avec allow-list
│   ├── report.py              # Construction du rapport
│   └── visualisation.py       # Génération de graphiques
├── orchestrator/
│   ├── planner.py             # Backtracking planner
│   ├── executor.py            # Exécuteur d'outils
│   ├── critic.py              # Validateur de sortie
│   └── run_manager.py         # Boucle principale
├── tests/
│   ├── test_security.py       # Tests de sécurité
│   ├── test_tools.py          # Tests des outils
│   ├── test_planner.py        # Tests du planner
│   └── test_failure_injection.py  # Tests d'injection d'erreurs
├── gui/
│   └── app.py                 # Interface Streamlit
└── workflow/
    ├── scenario1.py           # Analyse CSV
    └── scenario2.py           # Intégration API
```

---

## 3. Couche de sécurité

### Fichier: `security/allow_list.py`

**Rôle:** Protéger contre les attaques et fuites de données.

#### Fonction 1: `is_host_allowed(url)`

```python
ALLOWED_HOSTS = {
    "api.open-meteo.com",
    "api.worldbank.org",
    "localhost",
    "127.0.0.1",
}

def is_host_allowed(url: str) -> bool:
    from urllib.parse import urlparse
    host = urlparse(url).hostname or ""
    return host in ALLOWED_HOSTS
```

**Explication:**
- Extrait le nom d'hôte de l'URL (ex: `https://api.open-meteo.com/v1/forecast` → `api.open-meteo.com`)
- Vérifie si l'hôte est dans la liste blanche
- Bloque tous les autres hôtes (protection contre l'exfiltration de données)

**Exemple:**
```python
is_host_allowed("https://api.open-meteo.com/data")  # ✅ True
is_host_allowed("https://evil.com/steal")           # ❌ False
```

---

#### Fonction 2: `is_path_safe(file_path)`

```python
_SANDBOX_ROOT = Path(__file__).resolve().parent.parent / "data_synthetic"

def is_path_safe(file_path: str) -> bool:
    try:
        resolved = (Path.cwd() / file_path).resolve()
        resolved.relative_to(_SANDBOX_ROOT.resolve())
        return True
    except ValueError:
        return False
```

**Explication:**
- Résout le chemin complet du fichier (gère `..`, `.`, liens symboliques)
- Vérifie que le chemin final est à l'intérieur de `data_synthetic/`
- Bloque les attaques de traversée de chemin (`../../etc/passwd`)

**Exemple:**
```python
is_path_safe("PROJET_DS2/data_synthetic/tourism_big.csv")  # ✅ True
is_path_safe("../../etc/passwd")                           # ❌ False
```

---

#### Fonction 3: `redact_sensitive(data)`

```python
SENSITIVE_KEYS = {"token", "api_key", "password", "secret", "authorization"}

def redact_sensitive(data: dict) -> dict:
    result = {}
    for k, v in data.items():
        if k.lower() in SENSITIVE_KEYS:
            result[k] = "***REDACTED***"
        elif isinstance(v, dict):
            result[k] = redact_sensitive(v)  # Récursif
        else:
            result[k] = v
    return result
```

**Explication:**
- Parcourt un dictionnaire
- Masque les clés sensibles (token, api_key, password, etc.)
- Fonctionne récursivement pour les dictionnaires imbriqués

**Exemple:**
```python
data = {"user": "alice", "api_key": "secret123", "value": 42}
redact_sensitive(data)
# → {"user": "alice", "api_key": "***REDACTED***", "value": 42}
```

---

## 4. Schémas de validation

### Fichier: `tools/schemas.py`

**Rôle:** Définir la structure exacte des entrées/sorties de chaque outil avec Pydantic.

#### Pourquoi Pydantic ?

Pydantic valide automatiquement les types et les contraintes :

```python
from pydantic import BaseModel, Field

class ReadCsvInput(BaseModel):
    file: str = Field(..., description="Chemin relatif vers le CSV")
    required_columns: list[str] = Field(
        default=["region", "occupancy_rate", "revenue"]
    )
```

**Ce que ça fait:**
- `file: str` → doit être une chaîne de caractères
- `required_columns: list[str]` → doit être une liste de chaînes
- Si vous passez un entier au lieu d'une chaîne → **erreur automatique**

#### Exemple de validation

```python
# ✅ Valide
inp = ReadCsvInput(
    file="PROJET_DS2/data_synthetic/tourism_big.csv",
    required_columns=["region", "revenue"]
)

# ❌ Erreur — file doit être une chaîne
inp = ReadCsvInput(file=123)  # ValidationError
```

#### Tous les schémas définis

| Outil | Schéma d'entrée | Schéma de sortie |
|-------|----------------|------------------|
| `read_csv_tool` | `ReadCsvInput` | `ReadCsvOutput` |
| `compute_kpis` | `ComputeKpisInput` | `ComputeKpisOutput` |
| `fetch_api_data` | `FetchApiInput` | `FetchApiOutput` |
| `fetch_weather_data` | `FetchWeatherInput` | `FetchWeatherOutput` |
| `build_report` | `BuildReportInput` | `BuildReportOutput` |

---

## 5. Outils (Tools)

### Outil 1: `read_csv_tool.py`

**Rôle:** Charger un fichier CSV depuis le sandbox de manière sécurisée.

```python
def read_csv_file(file: str, required_columns: list[str] | None = None):
    # 1. Validation du schéma
    inp = ReadCsvInput(file=file, required_columns=required_columns)
    
    # 2. Vérification de sécurité
    if not is_path_safe(inp.file):
        raise ToolError("SAFETY_BLOCK: chemin hors sandbox")
    
    # 3. Vérification d'existence
    resolved = (Path.cwd() / inp.file).resolve()
    if not resolved.exists():
        raise ToolError("FILE_NOT_FOUND")
    
    # 4. Lecture du CSV
    df = pd.read_csv(resolved)
    
    # 5. Vérification des colonnes requises
    missing = [c for c in inp.required_columns if c not in df.columns]
    if missing:
        raise ToolError(f"SCHEMA_ERROR: colonnes manquantes: {missing}")
    
    return df
```

**Flux de validation:**
```
Entrée → Pydantic → Sécurité → Existence → Lecture → Schéma → Sortie
```

---

### Outil 2: `compute_kpis.py`

**Rôle:** Calculer les KPIs touristiques (taux d'occupation, revenus, top régions).

```python
def compute_kpis(df: pd.DataFrame) -> dict:
    # 1. Vérifier les colonnes requises
    required = ["occupancy_rate", "revenue", "region"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ToolError(f"SCHEMA_ERROR: colonnes manquantes: {missing}")
    
    # 2. Calculer les KPIs
    average_occupancy_rate = round(float(df["occupancy_rate"].mean()), 4)
    total_revenue = round(float(df["revenue"].sum()), 2)
    
    revenue_by_region = (
        df.groupby("region")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )
    
    # 3. Valider la sortie avec Pydantic
    output = ComputeKpisOutput(
        average_occupancy_rate=average_occupancy_rate,
        total_revenue=total_revenue,
        top_regions=revenue_by_region,
    )
    
    return output.model_dump()
```

**Exemple de sortie:**
```json
{
  "average_occupancy_rate": 0.8123,
  "total_revenue": 12458900.50,
  "top_regions": {
    "Hammamet": 3245600.00,
    "Djerba": 2987400.00,
    "Tunis": 2654300.00
  },
  "status": "ok"
}
```

---

### Outil 3: `api_tool.py`

**Rôle:** Appeler des APIs externes avec allow-list et retries bornées.

```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def _get_with_retry(url: str, timeout: int):
    resp = requests.get(url, timeout=timeout)
    if resp.status_code == 429:
        raise IOError("HTTP 429: rate limited")
    if resp.status_code != 200:
        raise IOError(f"HTTP {resp.status_code}")
    return resp

def fetch_weather_data(latitude=36.8, longitude=10.1, timeout=10):
    # 1. Validation Pydantic
    inp = FetchWeatherInput(latitude=latitude, longitude=longitude, timeout=timeout)
    
    # 2. Construction de l'URL
    url = f"https://api.open-meteo.com/v1/forecast?latitude={inp.latitude}&longitude={inp.longitude}&current_weather=true"
    
    # 3. Vérification allow-list
    if not is_host_allowed(url):
        raise ToolError(f"SAFETY_BLOCK: hôte non autorisé")
    
    # 4. Appel avec retry (max 3 tentatives, backoff exponentiel)
    try:
        resp = _get_with_retry(url, inp.timeout)
    except (RetryError, IOError) as e:
        raise ToolError(f"API_FAILURE: {e}")
    
    # 5. Extraction et validation de la sortie
    raw = resp.json()
    cw = raw.get("current_weather", {})
    
    output = FetchWeatherOutput(
        temperature=cw.get("temperature", 0.0),
        windspeed=cw.get("windspeed", 0.0),
        tourism_impact="high" if cw.get("temperature", 0) > 25 else "medium",
    )
    
    return output.model_dump()
```

**Stratégie de retry:**
- Tentative 1 → échec → attendre 1s
- Tentative 2 → échec → attendre 2s
- Tentative 3 → échec → lever ToolError

---

## 6. Orchestrateur

### 6.1 Planner (Backtracking)

**Fichier:** `orchestrator/planner.py`

**Rôle:** Trouver un plan faisable (séquence d'étapes) en utilisant le backtracking.

#### Algorithme de backtracking

```
État = (index_étape, objectifs_satisfaits, budget_restant)

fonction backtrack(étapes, index, satisfaits, requis, budget):
    # Cas de base: budget épuisé
    si budget <= 0:
        élaguer cette branche
        retourner None
    
    # Cas de base: toutes les étapes consommées
    si index >= len(étapes):
        si tous les objectifs requis sont satisfaits:
            retourner []  # succès
        sinon:
            élaguer cette branche
            retourner None
    
    étape = étapes[index]
    
    # Élagage: étape non faisable
    si étape non valide pour cette tâche:
        élaguer cette branche
        retourner None
    
    # Branche 1: inclure cette étape
    nouveaux_satisfaits = satisfaits ∪ objectifs_satisfaits_par(étape)
    reste = backtrack(étapes, index+1, nouveaux_satisfaits, requis, budget-1)
    si reste ≠ None:
        retourner [étape] + reste
    
    # Branche 2: sauter cette étape (si pas strictement requise)
    si étape pas strictement requise:
        reste = backtrack(étapes, index+1, satisfaits, requis, budget-1)
        si reste ≠ None:
            retourner reste
    
    retourner None
```

#### Exemple concret

**Tâche:** Analyse CSV

**Séquences candidates:**
1. `[read_csv, compute_kpis, report]`
2. `[read_csv, report]` (fallback sans KPIs)

**Objectifs requis:**
- `data_loaded`
- `kpis_computed`
- `report_ready`

**Exploration:**
```
Branche 1: [read_csv, compute_kpis, report]
  - read_csv satisfait: data_loaded ✅
  - compute_kpis satisfait: kpis_computed ✅
  - report satisfait: report_ready ✅
  - Tous les objectifs satisfaits → SUCCÈS
  
Résultat: [read_csv, compute_kpis, report]
```

**Stats:**
```json
{
  "branches_explored": 1,
  "branches_pruned": 0,
  "depth_reached": 3,
  "plan_found": true
}
```

---

### 6.2 Executor

**Fichier:** `orchestrator/executor.py`

**Rôle:** Exécuter chaque étape du plan avec validation stricte.

```python
class Executor:
    def __init__(self):
        # État isolé par exécution (pas de partage entre runs)
        self.df: pd.DataFrame | None = None
        self.kpis: dict | None = None
    
    def execute(self, step: str, task: dict):
        if step == "read_csv":
            self.df = read_csv_file(
                file=task["file"],
                required_columns=task.get("required_columns"),
            )
            return {"rows_loaded": len(self.df), "columns": list(self.df.columns)}
        
        elif step == "compute_kpis":
            if self.df is None:
                raise ToolError("PRECONDITION_FAILED: read_csv doit s'exécuter avant")
            self.kpis = compute_kpis(self.df)
            return self.kpis
        
        elif step == "report":
            data = self.kpis or {}
            return build_report(data)
        
        else:
            raise ToolError(f"UNKNOWN_STEP: '{step}'")
```

**Isolation de l'état:**
- Chaque `RunManager` crée un nouvel `Executor`
- Pas de variables globales
- Pas de partage d'état entre exécutions parallèles

---

### 6.3 Critic

**Fichier:** `orchestrator/critic.py`

**Rôle:** Valider le résultat final.

```python
class Critic:
    def validate(self, result) -> bool:
        # None → erreur
        if result is None:
            return False
        
        # Marqueur d'erreur explicite
        if isinstance(result, dict) and "error" in result:
            return False
        
        # Dictionnaire vide → invalide
        if isinstance(result, dict) and len(result) == 0:
            return False
        
        # Tous les checks passés
        return True
```

---

### 6.4 RunManager

**Fichier:** `orchestrator/run_manager.py`

**Rôle:** Orchestrer la boucle complète avec retries bornées.

```python
class RunManager:
    def __init__(self, max_steps=10, max_retries_per_step=2):
        self.run_id = f"RUN-{uuid.uuid4()}"
        self.logs = []
        self.max_steps = max_steps
        self.max_retries_per_step = max_retries_per_step
    
    def run(self, task: dict) -> dict:
        # 1. Planning
        planner = Planner(max_steps=self.max_steps)
        steps = planner.plan(task)
        
        # 2. Exécution avec retries
        executor = Executor()
        result = None
        
        for i, step in enumerate(steps):
            try:
                result = self._execute_with_retry(executor, step, task)
                self.log_step(f"STEP_{i+1:03}", step, "SUCCESS")
            except (ToolError, RetryError) as e:
                self.log_step(f"STEP_{i+1:03}", step, f"FAILED: {e}")
                self.save_logs()
                return {"error": str(e), "run_id": self.run_id}
        
        # 3. Validation
        critic = Critic()
        if not critic.validate(result):
            return {"error": "Validation failed", "run_id": self.run_id}
        
        self.save_logs()
        return result
    
    def _execute_with_retry(self, executor, step, task):
        @retry(stop=stop_after_attempt(self.max_retries_per_step + 1))
        def _attempt():
            return executor.execute(step, task)
        return _attempt()
```

**Flux complet:**
```
1. Créer run_id unique
2. Planner → trouver plan faisable
3. Pour chaque étape:
   a. Exécuter avec retry (max 2 retries)
   b. Logger le résultat
   c. Si échec → arrêt sûr
4. Critic → valider le résultat final
5. Sauvegarder les logs
6. Retourner le résultat
```

---

## 7. Tests

### 7.1 Tests de sécurité

**Fichier:** `tests/test_security.py`

```python
def test_allowed_host():
    assert is_host_allowed("https://api.open-meteo.com/v1/forecast")
    assert not is_host_allowed("https://evil.com/steal")

def test_path_traversal_blocked():
    assert not is_path_safe("../../etc/passwd")

def test_redaction():
    data = {"user": "alice", "api_key": "secret123"}
    redacted = redact_sensitive(data)
    assert redacted["api_key"] == "***REDACTED***"
```

---

### 7.2 Tests des outils

**Fichier:** `tests/test_tools.py`

```python
def test_valid_csv():
    df = read_csv_file("PROJET_DS2/data_synthetic/tourism_big.csv")
    assert len(df) > 0
    assert "region" in df.columns

def test_missing_file():
    with pytest.raises(ToolError, match="FILE_NOT_FOUND"):
        read_csv_file("PROJET_DS2/data_synthetic/nonexistent.csv")

def test_path_traversal_blocked():
    with pytest.raises(ToolError, match="SAFETY_BLOCK"):
        read_csv_file("../../etc/passwd")
```

---

### 7.3 Tests du planner

**Fichier:** `tests/test_planner.py`

```python
def test_csv_task_plan():
    planner = Planner(max_steps=10)
    task = {"type": "csv", "file": "PROJET_DS2/data_synthetic/tourism_big.csv"}
    steps = planner.plan(task)
    
    assert "read_csv" in steps
    assert "compute_kpis" in steps
    assert "report" in steps
    assert planner.stats.plan_found is True
```

---

### 7.4 Tests d'injection d'erreurs

**Fichier:** `tests/test_failure_injection.py`

```python
def test_missing_file_scenario1():
    task = {
        "type": "csv",
        "file": "PROJET_DS2/data_synthetic/MISSING_FILE.csv"
    }
    manager = RunManager()
    result = manager.run(task)
    
    assert "error" in result
    assert "FILE_NOT_FOUND" in result["error"]
    assert result["failed_step"] == "read_csv"
```

---

## 8. Interface graphique

**Fichier:** `gui/app.py`

**Technologie:** Streamlit

### Composants

1. **Sidebar: Task Launcher**
   - Sélecteur de scénario (1 ou 2)
   - Checkbox "Inject Failure"
   - Bouton "Run Task"

2. **Main: Run Overview**
   - Liste des 10 dernières exécutions
   - Colonnes: Run ID, Status, Duration

3. **Step Timeline**
   - Trace chronologique de chaque étape
   - Expandable metadata (JSON)

4. **Metrics Dashboard**
   - Total Runs
   - Success Rate (placeholder)
   - Avg Steps (placeholder)

### Lancer la GUI

```bash
streamlit run gui/app.py
```

---

## 9. Comment tout fonctionne ensemble

### Scénario 1: Analyse CSV normale

```
1. Utilisateur lance: python main.py → choisit 1

2. RunManager créé avec run_id unique

3. Planner.plan(task):
   - task = {"type": "csv", "file": "..."}
   - Explore: [read_csv, compute_kpis, report]
   - Vérifie faisabilité: ✅
   - Retourne: [read_csv, compute_kpis, report]

4. Executor.execute("read_csv", task):
   - Valide schéma avec Pydantic ✅
   - Vérifie sécurité (is_path_safe) ✅
   - Lit le CSV (465 lignes) ✅
   - Retourne: {"rows_loaded": 465, "columns": [...]}

5. Executor.execute("compute_kpis", task):
   - Vérifie colonnes requises ✅
   - Calcule moyenne taux d'occupation: 0.8123
   - Calcule revenu total: 12458900.50
   - Groupe par région et trie
   - Retourne: {"average_occupancy_rate": 0.8123, ...}

6. Executor.execute("report", task):
   - Génère graphique (sauvegardé sur disque)
   - Retourne: {"status": "success", "data": {...}}

7. Critic.validate(result):
   - result n'est pas None ✅
   - result n'a pas de clé "error" ✅
   - result n'est pas vide ✅
   - Retourne: True

8. RunManager.save_logs():
   - Sauvegarde logs/RUN-<uuid>.json

9. Affichage du résultat final
```

---

### Scénario 1: Fichier manquant (injection d'erreur)

```
1. task = {"type": "csv", "file": "MISSING_FILE.csv"}

2. Planner trouve le plan: [read_csv, compute_kpis, report]

3. Executor.execute("read_csv", task):
   - Valide schéma ✅
   - Vérifie sécurité ✅
   - Vérifie existence du fichier ❌
   - Lève: ToolError("FILE_NOT_FOUND: ...")

4. RunManager attrape l'erreur:
   - Log: "STEP_001: read_csv → FAILED: FILE_NOT_FOUND"
   - Sauvegarde les logs
   - Retourne: {"error": "FILE_NOT_FOUND", "run_id": "...", "failed_step": "read_csv"}

5. Pas d'exécution des étapes suivantes (arrêt sûr)

6. Pas d'appel au Critic (sortie anticipée)
```

---

### Scénario 1: Traversée de chemin (attaque)

```
1. task = {"type": "csv", "file": "../../etc/passwd"}

2. Planner trouve le plan: [read_csv, compute_kpis, report]

3. Executor.execute("read_csv", task):
   - Valide schéma ✅
   - Vérifie sécurité (is_path_safe):
     - Résout: /etc/passwd
     - Vérifie si dans sandbox: ❌
   - Lève: ToolError("SAFETY_BLOCK: chemin hors sandbox")

4. RunManager attrape l'erreur:
   - Log: "STEP_001: read_csv → FAILED: SAFETY_BLOCK"
   - Sauvegarde les logs
   - Retourne: {"error": "SAFETY_BLOCK", ...}

5. Aucun accès au système de fichiers (attaque bloquée)
```

---

## Résumé des garanties

### ✅ Sécurité
- Traversée de chemin bloquée
- Allow-list HTTP stricte
- Secrets masqués dans les logs

### ✅ Fiabilité
- Validation de schéma (Pydantic)
- Retries bornées (tenacity)
- Max-step policy (pas de boucles infinies)

### ✅ Observabilité
- Logs structurés (JSON)
- Run ID unique par exécution
- Trace complète de chaque étape

### ✅ Correction
- Backtracking pour plans faisables
- Élagage des branches infaisables
- Validation finale par Critic

### ✅ Isolation
- État séparé par exécution
- Pas de variables globales
- Sûr pour exécutions parallèles

---

## Prochaines étapes (Semaine 3)

- [ ] Implémenter couche DP/mémoization
- [ ] Comparer BT vs BT+DP empiriquement
- [ ] Implémenter Scénario 2 + injection d'erreurs
- [ ] Tests de stress concurrence
- [ ] Améliorer dashboard GUI

---

**Fin du guide complet — Semaine 2**
