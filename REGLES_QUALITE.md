# Règles de qualité du code : exemples de violations

Ce document illustre, avec des exemples simples, ce que les outils configurés dans [pyproject.toml](pyproject.toml) détectent.

| Outil | Rôle | Commande |
|-------|------|----------|
| Ruff | Style et erreurs courantes | `ruff check .` |
| Mypy | Cohérence des types | `mypy .` |
| Pytest | Exécution des tests | `pytest` |

---

## 1. Ruff : règles `E` (style PEP 8)

Elles vérifient la mise en forme du code.

### E501 : ligne trop longue

```python
# ❌ Violation
message = "Ceci est un message vraiment très très long qui dépasse largement la limite de caractères autorisée par ligne"

# ✅ Correct
message = (
    "Ceci est un message vraiment très très long "
    "qui est découpé sur plusieurs lignes"
)
```

### E711 / E712 : comparaison incorrecte avec `None` ou `True`/`False`

```python
# ❌ Violation
if valeur == None:
    ...
if est_actif == True:
    ...

# ✅ Correct
if valeur is None:
    ...
if est_actif:
    ...
```

### E701 : plusieurs instructions sur une seule ligne

```python
# ❌ Violation
if x > 0: print("positif")

# ✅ Correct
if x > 0:
    print("positif")
```

### E741 : nom de variable ambigu

```python
# ❌ Violation (« l » ressemble à « 1 » ou « I »)
l = [1, 2, 3]

# ✅ Correct
nombres = [1, 2, 3]
```

### E402 : import qui n'est pas en haut du fichier

```python
# ❌ Violation
print("démarrage")
import os

# ✅ Correct
import os

print("démarrage")
```

---

## 2. Ruff : règles `F` (erreurs logiques, pyflakes)

Elles détectent du code qui est probablement faux ou inutile.

### F401 : import inutilisé

```python
# ❌ Violation
import os
import sys

print(sys.version)   # « os » n'est jamais utilisé

# ✅ Correct
import sys

print(sys.version)
```

### F821 : nom non défini

```python
# ❌ Violation
def afficher():
    print(prenom)    # « prenom » n'existe nulle part

# ✅ Correct
def afficher(prenom: str) -> None:
    print(prenom)
```

### F841 : variable locale assignée mais jamais utilisée

```python
# ❌ Violation
def calculer() -> int:
    resultat = 42    # jamais utilisée
    return 0

# ✅ Correct
def calculer() -> int:
    return 42
```

### F811 : redéfinition d'un nom non utilisé

```python
# ❌ Violation
def saluer() -> str:
    return "bonjour"

def saluer() -> str:   # écrase la première définition
    return "salut"
```

---

## 3. Ruff : règles `I` (tri des imports)

Les imports doivent être regroupés et triés : bibliothèque standard, puis tiers, puis code local, avec une ligne vide entre chaque groupe.

### I001 : imports non triés

```python
# ❌ Violation
import requests
import os
from fair_share import calcul
import sys

# ✅ Correct
import os
import sys

import requests

from fair_share import calcul
```

---

## 4. Ruff : règles `B` (bugbear : bugs probables)

Elles repèrent des pièges classiques de Python.

### B006 : argument par défaut mutable

Le piège : la liste est créée **une seule fois** et partagée entre tous les appels.

```python
# ❌ Violation
def ajouter(element: int, liste: list[int] = []) -> list[int]:
    liste.append(element)
    return liste

ajouter(1)   # [1]
ajouter(2)   # [1, 2]  ← surprise !

# ✅ Correct
def ajouter(element: int, liste: list[int] | None = None) -> list[int]:
    if liste is None:
        liste = []
    liste.append(element)
    return liste
```

### B007 : variable de boucle non utilisée

```python
# ❌ Violation
for i in range(3):
    print("coucou")

# ✅ Correct
for _ in range(3):
    print("coucou")
```

### B904 : `raise` dans un `except` sans `from`

Sans `from`, on perd l'information sur l'erreur d'origine.

```python
# ❌ Violation
try:
    int("abc")
except ValueError:
    raise RuntimeError("valeur invalide")

# ✅ Correct
try:
    int("abc")
except ValueError as erreur:
    raise RuntimeError("valeur invalide") from erreur
```

### B011 : `assert False`

`assert False` est supprimé quand Python tourne avec l'option `-O`.

```python
# ❌ Violation
assert False, "ne devrait jamais arriver"

# ✅ Correct
raise AssertionError("ne devrait jamais arriver")
```

---

## 5. Mypy en mode `strict = true`

Mypy vérifie les **types**. Le mode strict active toutes les vérifications, notamment l'obligation d'annoter les fonctions.

### no-untyped-def : fonction sans annotations

```python
# ❌ Violation
def additionner(a, b):
    return a + b

# ✅ Correct
def additionner(a: int, b: int) -> int:
    return a + b
```

### assignment / arg-type : type incompatible

```python
# ❌ Violation
age: int = "vingt"           # une chaîne n'est pas un entier

def doubler(n: int) -> int:
    return n * 2

doubler("5")                 # attend un int, reçoit un str

# ✅ Correct
age: int = 20
doubler(5)
```

### union-attr : oubli du cas `None`

```python
# ❌ Violation
def longueur(texte: str | None) -> int:
    return len(texte)        # texte peut être None

# ✅ Correct
def longueur(texte: str | None) -> int:
    if texte is None:
        return 0
    return len(texte)
```

### type-arg : générique sans paramètre de type

```python
# ❌ Violation
def premier(elements: list) -> int:   # list de quoi ?
    return elements[0]

# ✅ Correct
def premier(elements: list[int]) -> int:
    return elements[0]
```

### no-any-return : retour de `Any` dans une fonction typée

```python
# ❌ Violation
import json

def lire(contenu: str) -> int:
    return json.loads(contenu)   # json.loads renvoie Any

# ✅ Correct
def lire(contenu: str) -> int:
    valeur = json.loads(contenu)
    return int(valeur)
```

### return-value / missing return : retour incohérent

```python
# ❌ Violation
def nom() -> str:
    return None              # promet un str, renvoie None

# ✅ Correct
def nom() -> str | None:
    return None
```

---

## 6. Pytest

Cette section ne contient pas de règles à violer : elle configure le comportement de pytest.

| Option | Effet |
|--------|-------|
| `pythonpath = ["."]` | Ajoute la racine du projet au chemin d'import, pour que les tests puissent faire `from fair_share import ...`. |
| `testpaths = ["tests"]` | `pytest` cherche les tests uniquement dans le dossier `tests/`. |

**Ce qui se passe sans `pythonpath`** :

```
ModuleNotFoundError: No module named 'fair_share'
```

**Convention de nommage** : pour être découvert, un fichier de test s'appelle `test_*.py` et ses fonctions `test_*`.

```python
# tests/test_calcul.py
def test_addition() -> None:
    assert 1 + 1 == 2
```

---

## Corriger automatiquement

```bash
ruff check . --fix     # corrige ce qui peut l'être (imports inutilisés, tri des imports...)
ruff check .           # liste ce qui reste à corriger à la main
mypy .                 # vérifie les types
pytest                 # lance les tests
```

> Les violations de type `E`, `B` et `mypy` demandent le plus souvent une correction manuelle. Ruff ne corrige automatiquement que les cas sans ambiguïté.
