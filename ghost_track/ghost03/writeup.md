```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x03 · "access denied"
 ========================================================================

   target ..: ghost-03  "Access Denied"
   class ...: recon / unix group permissions
   tools ...: whoami · groups · ls
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> "access denied" è un bluff. non serve scalare niente: sei già nel
> gruppo giusto, devi solo accorgertene. il kernel ti farebbe entrare da
> subito.

## ----[ 0x00 · intel ]----

Nessun banner "Goal/Connect": l'obiettivo emerge dalla home. Recuperare
le credenziali riservate lasciate da un operatore precedente in una
directory ad accesso ristretto, aperta solo a chi appartiene a un certo
gruppo Unix.

## ----[ 0x01 · recon ]----

Nella home c'è una nota di un operatore precedente che descrive una
gerarchia di directory sensibili:

- una leggibile da tutti
- una ad accesso ristretto
- una solo per root

La nota è esplicita: l'accesso segue lo schema dei gruppi Unix, e
suggerisce di verificare la propria identità con gli strumenti standard
della shell.

## ----[ 0x02 · il difetto ]----

Enumerazione dei permessi Unix basata sui gruppi. Controllando
l'appartenenza dell'utente corrente si scopre che sta non solo nel
gruppo primario ma anche in un gruppo aggiuntivo. E la directory
ristretta è leggibile/eseguibile proprio da quel gruppo aggiuntivo:
nessuna escalation, il kernel concede l'accesso già così com'è. Il
"denied" era solo scenografia.

## ----[ 0x03 · exploit ]----

1. Enumerazione della home e lettura della nota:

```bash
ll
cat map.txt
```

Rivela la struttura delle directory riservate e la dipendenza dal gruppo.

2. Verifica di identità e gruppi:

```bash
whoami
groups
```

L'utente appartiene anche a un gruppo secondario oltre al primario.

3. Ispezione dei permessi delle sottodirectory riservate:

```bash
ll /var/intel
```

Una sottodirectory è leggibile/eseguibile proprio dal gruppo secondario
— quindi accessibile senza altri privilegi.

4. Accesso diretto e lettura dei file:

```bash
ll
cat access_codes.dat operative_list.txt
```

## ----[ 0x04 · loot ]----

Le credenziali "Analyst Only" recuperate con la sola enumerazione dei
permessi di gruppo, zero privilege escalation (valore omesso). La
lezione: prima di pensare all'escalation, guarda a quali gruppi
appartieni già — spesso la porta è aperta.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
