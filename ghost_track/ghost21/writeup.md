```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x15 · "secrets in history"
 ========================================================================

   target ..: ghost-21  "Secrets in History"
   class ...: git forensics · secret in tag history
   tools ...: git log · git tag · git show
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> `main` è pulito, e questo è il trucco. una release candidate taggata ha
> ancora la deploy key hardcoded che qualcuno ha tolto "in superficie". la
> history di git non dimentica.

## ----[ 0x00 · intel ]----

Il livello consegna un repo git già clonato, branch `main` pulito. Ma il
brief avverte: una release candidate taggata contiene ancora una deploy
key hardcoded, poi rimossa da main. Obiettivo: recuperare quel secret
dalla history.

## ----[ 0x01 · recon ]----

Nella home una cartella `repo/` con un repo git funzionante. `git log` su
`main` mostra solo due commit puliti, nessun segreto. `git tag` rivela
però un tag di release candidate, non raggiungibile dalla history lineare
che `git log` mostra di default.

## ----[ 0x02 · il difetto ]----

Ispezione della history oltre il branch corrente. `git log` mostra solo i
commit raggiungibili da `HEAD`, ma tag e repo possono conservare commit
"orfani" rispetto a main — es. una rc taggata e mai mergiata, o il cui
commit incriminato è stato tolto da main ma resta raggiungibile dal tag.
`git show <tag>` ne mostra il diff completo. Qui il commit taggato
introduce un `.env` con una deploy key in chiaro: secret hardcoded rimosso
in superficie ma ancora nella history immutabile. Esattamente ciò che i
secret-scanner di GitHub cercano di intercettare.

## ----[ 0x03 · exploit ]----

1. Enumerazione e repo:

```bash
ll
```

```text
drwxr-xr-x 1 ghost21 ghost21 4096 Jun 25 14:16 repo/
```

2. History sul branch corrente:

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

Nessun secret: main è pulito davvero.

3. Tag presenti, spesso ignorati in un audit superficiale:

```bash
git tag
```

```text
v1.4.0-rc1
```

4. Ispezione del commit puntato dal tag, messaggio e diff:

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

Il diff del tag mostra `.env` con la deploy key in chiaro, mai rimossa
dalla history nonostante non sia più su main.

## ----[ 0x04 · loot ]----

La deploy key dal tag della release candidate è la password per proseguire
(valore fuori dal writeup). Lezione: in un audit, tag e history vanno
guardati sempre insieme al branch principale — cancellare da main non
cancella dalla storia.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
