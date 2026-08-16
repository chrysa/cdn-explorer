# cdn-explorer — Deep-dive technique & teardown des sources de référence

**Repo local :** `/home/anthony/Documents/perso/projects/chrysa/cdn-explorer`
**But (1 phrase) :** Outil full-stack FastAPI + React qui crawle une URL de directory-listing public (autoindex nginx/Apache HTML + JSON nginx), reconstruit une arborescence de fichiers navigable et proxy-télécharge chaque fichier via un proxy borné (SSRF-guard, cap 50 MB, timeouts), le tout stateless (rien persisté).

**Modules-clés visés par les réfs :**
- `api/ssrf.py` — guard SSRF (résout l'hôte, bloque IP non routables : loopback, RFC1918, link-local `169.254.169.254`…).
- `api/crawler.py` — détection listing, parsing nginx-JSON, récursion same-host, bornes profondeur/nodes.
- `api/routers/explore.py` — endpoints `/api/explore` + `/api/download` (proxy streamé).
- `api/constants.py` — extensions d'assets, bornes de crawl, cap download.

Données GitHub **LIVE** relevées le 2026-08-15 (via `gh api`).

---

## 1. JordanMilne/Advocate — SSRF-safe HTTP wrapper (LE match direct de `api/ssrf.py`)

- **owner/repo :** JordanMilne/Advocate
- **stars :** 96
- **activité :** dernier push 2023-08-31 (mature, peu maintenu mais stable)
- **licence :** **Apache-2.0** (le fichier LICENSE est explicitement Apache 2.0 ; l'API GitHub renvoie `NOASSERTION` par erreur de détection). **→ PERMISSIVE, copiable avec attribution.**
- **langage :** Python
- **fichier/module précis :** `advocate/addrvalidator.py` (classe `AddrValidator`) + `advocate/connection.py`.
- **mécanisme réel :** Advocate wrappe `requests` et interpose la validation d'IP **au moment de la connexion socket**, pas seulement au moment de la résolution DNS. Le point important qu'il traite et que `ssrf.py` ne traite PAS aujourd'hui : le **TOCTOU / DNS-rebinding**. `ssrf.py` fait `getaddrinfo()` puis laisse `httpx` re-résoudre → un DNS malveillant peut renvoyer une IP publique à la validation et une IP privée à la connexion réelle. Advocate valide l'IP effectivement connectée. Il gère aussi le suivi de redirections (revalide chaque hop).
- **snippet portable (~15 lignes) — bloquer par plage, comme Advocate le fait, mais appliqué à l'IP connectée :**

```python
import ipaddress

# Plages à bloquer (superset de ce que fait AddrValidator d'Advocate)
_BLOCKED_NETS = [ipaddress.ip_network(n) for n in (
    "0.0.0.0/8", "10.0.0.0/8", "100.64.0.0/10", "127.0.0.0/8",
    "169.254.0.0/16", "172.16.0.0/12", "192.0.0.0/24", "192.168.0.0/16",
    "198.18.0.0/15", "::1/128", "fc00::/7", "fe80::/10",
)]

def is_blocked(ip_str: str) -> bool:
    ip = ipaddress.ip_address(ip_str)
    return (not ip.is_global) or any(ip in net for net in _BLOCKED_NETS)
```

- **intégration dans ce projet :**
  1. Garder `api/ssrf.py` pour la validation pré-vol (rapide, rejette 99% des cas).
  2. Fermer le trou DNS-rebinding : sur le client `httpx`, monter un transport qui **pin l'IP validée** — résoudre une fois, passer l'IP en `host` de la connexion et l'hostname d'origine seulement dans l'en-tête `Host` + SNI. Alternative plus simple : ré-appeler `validate_public_url` sur **chaque URL de redirection** dans `crawler.py` / `download` (Advocate revalide chaque hop).
  3. Ajouter `ip.is_global` comme garde primaire (plus robuste que l'énumération manuelle actuelle `is_private/is_loopback/...`).
- **gotchas :** Advocate cible `requests` (sync), pas `httpx` async → **réimplémentation du mécanisme**, pas un `pip install` drop-in. Ne pas copier son code verbatim dans le chemin async ; s'en inspirer. La plage `100.64.0.0/10` (CGNAT) et `198.18.0.0/15` (bench) manquent souvent des guards naïfs — Advocate les couvre.

---

## 2. KoalaBear84/OpenDirectoryDownloader — le crawler d'open-directories de référence

- **owner/repo :** KoalaBear84/OpenDirectoryDownloader
- **stars :** 1383
- **activité :** dernier push 2026-07-18 (**très actif**)
- **licence :** **GPL-3.0** → **COPYLEFT FORT. NE PAS COPIER DE CODE. Réimplémenter les idées uniquement.**
- **langage :** C#
- **fichier/module précis :** dossier `OpenDirectoryDownloader/Site/` — un parseur par famille de listing (`GoIndex`, `Bhadoo`, un parseur Apache/nginx générique `OpenDirectoryIndexer.cs`).
- **mécanisme réel :** il maintient un **registre de "reconnaisseurs" de listings** : chaque type de serveur d'index (nginx autoindex, Apache mod_autoindex, DirectoryLister, h5ai, GoIndex, ...) a une signature détectée dans le HTML/headers, puis un parseur dédié qui extrait `(nom, taille, date, is_dir)`. La détection est en cascade (essaie chaque reconnaisseur, s'arrête au premier match). Il déduplique par URL et borne la récursion.
- **snippet portable (~12 lignes, réécrit en Python — pattern, PAS son code) :**

```python
# Registre de détecteurs — extensible, remplace le simple DIRECTORY_LISTING_MARKERS actuel
_PARSERS = []  # list[tuple[detect_fn, parse_fn]]

def register(detect, parse):
    _PARSERS.append((detect, parse))

def parse_listing(html: str, headers: dict) -> list[dict] | None:
    for detect, parse in _PARSERS:
        if detect(html, headers):
            return parse(html)   # -> [{"name","size","href","is_dir"}]
    return None
```

- **intégration :** `api/crawler.py` détecte aujourd'hui via `DIRECTORY_LISTING_MARKERS` + un chemin nginx-JSON codé en dur. Adopter le **pattern registre** rend l'ajout de h5ai / DirectoryLister / Apache trivial sans toucher au cœur de récursion. Chaque parser reste une petite fonction pure testable.
- **gotchas :** GPL — se limiter à lire pour **comprendre les signatures** (ex. quel marqueur identifie h5ai), jamais transposer des blocs. Beaucoup de ses parseurs gèrent des CDN JS (GoIndex/Bhadoo) hors scope ici. Son cap mémoire est bien plus élevé — garder `MAX_NODES=500`.

---

## 3. filebrowser/filebrowser — arborescence + download streamé côté serveur

- **owner/repo :** filebrowser/filebrowser
- **stars :** 35 868
- **activité :** dernier push 2026-07-31 (**très actif**)
- **licence :** **Apache-2.0** → **PERMISSIVE.** (Go, donc réf conceptuelle plutôt que copie ligne à ligne.)
- **langage :** Go
- **fichier/module précis :** `http/raw.go` (endpoint de download) + `files/file.go` (modèle d'arbre).
- **mécanisme réel :** le download écrit en **streaming** via `http.ServeContent` (respecte `Range`, pose `Content-Disposition`, ne charge jamais le fichier entier en mémoire). Le modèle de fichier expose une struct récursive `{Name, Size, IsDir, Items[]}` quasi identique au `FileNode` de ce projet.
- **snippet portable (~10 lignes, équivalent Python/FastAPI streamé) :**

```python
from fastapi.responses import StreamingResponse

async def proxy_download(url: str, client: httpx.AsyncClient):
    req = client.build_request("GET", url)
    resp = await client.send(req, stream=True)          # pas de .read() global
    headers = {"Content-Disposition": f'attachment; filename="{name}"'}
    return StreamingResponse(resp.aiter_bytes(), media_type=resp.headers.get(
        "content-type", "application/octet-stream"), headers=headers)
```

- **intégration :** valider que `/api/download` **stream** bien (via `httpx` stream + `StreamingResponse`) plutôt que bufferiser avant l'envoi ; c'est déjà l'intention (cap 50 MB), s'assurer que le cap est appliqué **pendant** l'itération des chunks (compteur d'octets → abort), pas via `Content-Length` (spoofable/absent).
- **gotchas :** filebrowser sert du **disque local** (pas de proxy réseau) → pas de préoccupation SSRF chez lui ; ne pas transposer sa confiance dans les chemins. Le support `Range` est un bonus optionnel ici (les CDN publics le supportent souvent).

---

## 4. encode/httpx — streaming + timeouts (déjà une dépendance du projet)

- **owner/repo :** encode/httpx
- **stars :** 15 423
- **activité :** dernier push 2026-03-29 (actif)
- **licence :** **BSD-3-Clause** → **PERMISSIVE.**
- **langage :** Python
- **fichier/module précis :** `httpx/_client.py` (`AsyncClient.stream`), `httpx/_config.py` (`Timeout`).
- **mécanisme réel :** `client.stream("GET", url)` renvoie une réponse dont le corps n'est lu qu'à la demande (`aiter_bytes`, `aiter_raw`), et `Timeout(connect=, read=, write=, pool=)` sépare les 4 phases — crucial pour un proxy qui parle à des hôtes arbitraires (un `read` lent ne doit pas bloquer indéfiniment).
- **snippet portable (~8 lignes) — cap appliqué pendant le stream :**

```python
CAP = 50 * 1024 * 1024
async with client.stream("GET", url, timeout=httpx.Timeout(connect=5, read=30, write=5, pool=5)) as r:
    total = 0
    async for chunk in r.aiter_bytes():
        total += len(chunk)
        if total > CAP:
            raise ValueError("file exceeds 50 MB cap")
        yield chunk
```

- **intégration :** c'est le bon endroit pour appliquer le cap **réel** (octets streamés) et des timeouts granulaires par phase dans `explore.py`. Remplace tout `resp.content`/`resp.read()` global éventuel.
- **gotchas :** en mode stream il faut fermer la réponse (`async with`) sinon fuite de connexion ; `follow_redirects` — chaque redirection doit repasser par `validate_public_url` (cf. réf 1).

---

## 5. aquilax/opendirindexer — mini-indexeur d'open-directory (idée portable, MIT)

- **owner/repo :** aquilax/opendirindexer
- **stars :** 10
- **activité :** dernier push 2023-01-08 (dormant mais autonome)
- **licence :** **MIT** → **PERMISSIVE, copiable.**
- **langage :** Go
- **fichier/module précis :** `main.go` — walk récursif d'un open-directory HTTP en émettant un flux d'entrées.
- **mécanisme réel :** BFS borné sur les liens `<a href>` d'une page d'index, filtre les liens de navigation parent (`../`, `?C=…` de tri Apache) et n'émet que les feuilles-fichiers ; extrait les liens via un parseur HTML tolérant.
- **snippet portable (~9 lignes — garde anti-liens-de-tri Apache, souvent oubliée) :**

```python
# Apache mod_autoindex ajoute des liens de tri ?C=N;O=D — à ignorer sinon boucles/doublons
_SKIP_QUERY_SORT = ("?C=", "?N=", "?M=", "?S=", "?D=")

def is_nav_link(href: str) -> bool:
    return (href in {"/", "../", "./"}
            or href.startswith(("#", "mailto:"))
            or any(s in href for s in _SKIP_QUERY_SORT))
```

- **intégration :** `crawler.py` a déjà `_SKIPPABLE_HREF_EXACT`/`_SKIPPABLE_HREF_PREFIXES` mais **ne filtre pas les liens de tri Apache `?C=N;O=D`** — ils créent des faux nodes et des ré-explorations. Ajouter le filtre ci-dessus ferme ce trou.
- **gotchas :** Go, donc réimplémentation ; petit projet → à traiter comme snippet de référence, pas comme dépendance.

---

## Synthèse licences

| Source | Licence | Verdict |
| --- | --- | --- |
| JordanMilne/Advocate | Apache-2.0 | ✅ copiable (attribution) |
| filebrowser/filebrowser | Apache-2.0 | ✅ copiable (Go → conceptuel) |
| encode/httpx | BSD-3-Clause | ✅ déjà dépendance |
| aquilax/opendirindexer | MIT | ✅ copiable |
| **KoalaBear84/OpenDirectoryDownloader** | **GPL-3.0** | ⛔ **COPYLEFT — réimplémenter les idées, ne rien copier** |

## Top 3 takeaways actionnables

1. **Fermer le DNS-rebinding/TOCTOU** (réf Advocate) : `ssrf.py` valide au DNS mais `httpx` re-résout → pin l'IP validée OU revalider chaque redirection. Ajouter `ip.is_global` + plages CGNAT/bench manquantes.
2. **Registre de parseurs de listings** (réf OpenDirectoryDownloader, idée seule) : remplacer le couple `DIRECTORY_LISTING_MARKERS` + nginx-JSON codé en dur par un registre extensible (h5ai, DirectoryLister, Apache).
3. **Cap & timeouts au niveau du stream** (réf httpx/filebrowser) : appliquer le cap 50 MB sur les octets réellement streamés (pas `Content-Length`) + `Timeout` granulaire par phase ; ignorer les liens de tri Apache `?C=…` (réf opendirindexer).
