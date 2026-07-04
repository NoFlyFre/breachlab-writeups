# Ghost Track - Ghost 21

## Sommario

- Track: Ghost Track
- Livello: Ghost 21
- Fonte appunti: `ghost_track/ghost21/notes.md`

## Obiettivo

Il livello ("Secrets in History") consegna un repository git già clonato, il cui branch `main` è pulito. Il brief avverte però che una release candidate taggata contiene ancora una deploy key hardcoded che a suo tempo è stata rimossa dal branch principale. L'obiettivo è recuperare quel secret dalla history del repository.

## Ricognizione

Nella home dell'utente è presente una cartella `repo/` con un repository git funzionante. Il `git log` sul branch `main` mostra solo due commit puliti, nessuno dei quali espone segreti. `git tag` rivela però l'esistenza di un tag di release candidate, non presente come commit raggiungibile dalla history lineare mostrata da `git log` di default.

## Tecnica

La tecnica sfruttata è l'ispezione della history git al di là del branch corrente: `git log` mostra solo i commit raggiungibili da `HEAD`, ma repository e tag possono conservare commit "orfani" rispetto al branch principale — ad esempio una release candidate che è stata taggata e poi mai mergiata, o il cui commit incriminato è stato rimosso da `main` ma resta comunque raggiungibile tramite il tag. `git show <tag>` permette di ispezionare il commit puntato dal tag, incluso il suo diff completo. In questo caso il commit taggato introduce un file `.env` con una variabile d'ambiente che contiene una deploy key in chiaro — un classico caso di secret hardcoded rimosso "in superficie" (nel branch main successivo) ma ancora recuperabile dalla history immutabile di git. Questo è esattamente il rischio che gli strumenti di secret-scanning su GitHub sono pensati per intercettare.

## Sfruttamento

1. Enumerazione della home e individuazione del repository:

```bash
ll
```

```text
drwxr-xr-x 1 ghost21 ghost21 4096 Jun 25 14:16 repo/
```

2. Dentro `repo/`, controllo della history sul branch corrente:

```bash
git log
```

```text
commit 2b796476c228c3d9aefd8c8d88814c2ae350dfc1 (HEAD -> main)
Author: KAEL <kael@ghost>
    docs: deploy + release notes

commit 580f36d13e257458299c7a569a9d8702bd6fbb66
Author: KAEL <kael@ghost>
    chore: deploy config template + ignore .env
```

Nessun secret visibile: main è effettivamente pulito.

3. Verifica dei tag presenti nel repository, spesso trascurati durante un audit superficiale:

```bash
git tag
```

```text
v1.4.0-rc1
```

4. Ispezione del commit puntato dal tag, incluso messaggio e diff:

```bash
git show v1.4.0-rc1
```

```text
tag v1.4.0-rc1
release candidate 1.4.0-rc1 (do not ship)

commit 3e1c99f798f87e9d860eecbd474b72bd079f7a4d (tag: v1.4.0-rc1)
    rc: hardcode deploy key so CI can ship 1.4.0

diff --git a/.env b/.env
new file mode 100644
index 0000000..773f8dd
--- /dev/null
+++ b/.env
@@ -0,0 +1,3 @@
+GHOST_DEPLOY_KEY=<REDACTED>
+REGION=eu-1
+DEBUG=true
```

Il diff del commit taggato mostra il file `.env` con la deploy key in chiaro, mai rimosso dalla history nonostante non sia più presente su `main`.

## Risultato

La deploy key recuperata dalla history del tag di release candidate è la password necessaria per proseguire nel track. Il valore letterale non è riportato qui secondo la dottrina BreachLab; il punto didattico è che i tag e la history git vanno sempre controllati insieme al branch principale durante un audit.

## Nota di pubblicazione

Questa è la versione pensata per la pubblicazione su GitHub secondo la dottrina BreachLab (Writeups · Creators): il metodo è spiegato per intero, ma la deploy key è stata sostituita con `<REDACTED>` per non fornire scorciatoie a chi non ha ancora risolto il livello.

## Crediti

Livello risolto su BreachLab (https://breachlab.org), Ghost Track. Credito al progetto BreachLab per la piattaforma di training.
