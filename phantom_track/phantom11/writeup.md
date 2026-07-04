```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   phantom track · phile 0x0b · "token hunter"
 ========================================================================

   target ..: phantom-11  "Token Hunter"
   class ...: git history archaeology · secret recovery
   tools ...: git log · git show
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> un repo con un revert a metà e un conflitto proprio sul file dei
> segreti. git non dimentica: il valore "rimosso" è ancora nel diff, sulla
> riga col `-`.

## ----[ 0x00 · intel ]----

La missione: cacciare token e credenziali moderne oltre alle password —
JWT, API key, credenziali cloud, service account token. La macchina si
collega a servizi cloud e API interne; uno di quei token è la flag.

## ----[ 0x01 · recon ]----

Nella home un repo git leggibile. Non è pulito: file di stato di un
merge/revert interrotto (`AUTO_MERGE`, `MERGE_MSG`, `REVERT_HEAD`,
`COMMIT_EDITMSG`), segno di operazioni git recenti. Ispezionandoli, è in
corso (o appena avvenuto) il revert di un commit di config iniziale, con
un conflitto proprio su un file di env var — forte indizio che quel file,
in una versione precedente, conteneva segreti.

## ----[ 0x02 · il difetto ]----

**Git history archaeology**: anche se un commit successivo rimuove o
oscura un segreto, il valore originale resta nella history, perché git
conserva ogni versione come oggetto immutabile finché non c'è un gc
aggressivo o una riscrittura. `git log` enumera i commit; `git show
<hash>` mostra il diff, inclusi quelli che *rimuovono* segreti — con il
valore vecchio (`-`) e quello nuovo (`+`). Qui il commit in testa (messaggio
sulla rimozione segreti) sostituisce valori reali con placeholder, ma la
riga `-` contiene ancora l'originale in chiaro.

## ----[ 0x03 · exploit ]----

1. Brief:

```bash
cat BRIEFING
```

2. `.git` e file di stato:

```bash
cd .git
ll
```

3. Lettura rapida dei file di stato:

```bash
cat *
```

Revert di un commit di config, conflitto su un file sensibile.

4. Cronologia:

```bash
git log
```

Due commit: config iniziale e rimozione segreti in testa.

5. Diff del commit più recente:

```bash
git show
```

I valori originali (righe `-`) prima dei placeholder (righe `+`):

```text
diff --git a/.env b/.env
index 1db2a85..c935363 100644
--- a/.env
+++ b/.env
@@ -1,2 +1,2 @@
-APP_SECRET=<REDACTED_FLAG>
-DB_URL=<REDACTED>
+APP_SECRET=REDACTED
+DB_URL=REDACTED
```

## ----[ 0x04 · loot ]----

La history rivela nel diff di "pulizia" il segreto applicativo (la flag) e
una connection string di db (valori omessi). Lezione concreta: committare
credenziali e "rimuoverle" dopo non serve a nulla — la history le tiene.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · phantom track
```
