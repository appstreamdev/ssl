# ssl

Odoo-Anpassungen für app-stream (Odoo Online / SaaS — keine eigenen Module möglich).

## `vorlagen/rechnung-sepa-oder-ueberweisung.html`

Body für die Rechnungs-E-Mail (`account.move`), der den Zahlungsabsatz automatisch
danach wechselt, ob per **SEPA-Lastschrift** eingezogen oder vom Kunden
**überwiesen** wird. Eine Vorlage, drei Fälle — kein Umschalten von Hand beim Versand.

### Einbauen

1. Entwicklermodus aktivieren (Einstellungen → ganz unten → *Entwicklerwerkzeuge aktivieren*).
2. Einstellungen → Technisch → E-Mail → **E-Mail-Vorlagen**.
3. Bestehende Rechnungsvorlage öffnen (oder per *Duplizieren* eine Kopie anlegen und
   diese im Dialog *Senden & Drucken* auswählen).
4. Reiter *Inhalt* → im Editor auf **`</>`** (Codeansicht) → gesamten Inhalt durch die
   Datei ersetzen. Den HTML-Kommentar am Dateianfang nicht mitkopieren.

### Die Bedingung

Genau eine Zeile entscheidet über den Text — die erste im Body:

```xml
<t t-set="ist_lastschrift" t-value="'lastschrift' in (object.invoice_payment_term_id.name or '').lower()"/>
```

Ausgewertet wird die **Zahlungsbedingung** der Rechnung: enthält ihr Name das Wort
*Lastschrift* (Groß-/Kleinschreibung egal), erscheint der Einzugstext, sonst der
Überweisungstext. Voraussetzung ist also je eine Zahlungsbedingung wie
`Lastschrift 10 Tage` und `14 Tage netto`, hinterlegt am Kunden unter
*Verkauf & Einkauf → Zahlungsbedingungen*. Von dort landet sie automatisch auf jeder
neuen Rechnung und lässt sich pro Rechnung übersteuern.

### Warum die Zahlungsbedingung und nicht das SEPA-Mandat

Ursprünglich war das aktive Mandat (`sdd.mandate`) als Kriterium geplant. Das trägt
auf Odoo Online nicht:

* In einem Modul lässt sich der Zugriff auf Enterprise-Felder in Python absichern.
  In einer reinen QWeb-Vorlage geht das nicht — `object.a or object.b` wertet `object.a`
  trotzdem aus und bricht bei einem nicht existierenden Feld beim Rendern ab.
* Die Feldnamen des Enterprise-Moduls `account_sepa_direct_debit` sind nicht öffentlich
  dokumentiert und zwischen Versionen nicht garantiert stabil. Ein falsch geratener Name
  führt entweder zum Abbruch beim Versand oder — schlimmer — still zum falschen
  Zahlungstext beim Kunden.

Die Vorlage nutzt deshalb ausschließlich Felder aus dem Standardmodul `account`
bzw. `base`. Sie kann durch ein fehlendes Feld nicht brechen.

### Alternative Kriterien

Nur die eine `t-set`-Zeile tauschen, der Rest bleibt:

**Kundenkennzeichen (Stichwort/Tag am Kunden), z. B. Tag `SEPA-Lastschrift`:**

```xml
<t t-set="ist_lastschrift" t-value="'SEPA-Lastschrift' in object.partner_id.commercial_partner_id.category_id.mapped('name')"/>
```

**Aktives SEPA-Mandat** — nur einsetzen, wenn der Feldname vorher geprüft wurde
(Einstellungen → Technisch → Datenbankstruktur → *Felder*, Modell `res.partner`,
nach `sdd` filtern). Vorher an einer Testrechnung versenden:

```xml
<t t-set="ist_lastschrift" t-value="object.partner_id.commercial_partner_id.sudo().mapped('sdd_mandate_ids').filtered(lambda m: m.state == 'active')"/>
```

### Was die Vorlage sonst noch macht

* **Bereits bezahlt:** ist die Rechnung beim Versand ausgeglichen
  (`payment_state in ('paid', 'in_payment')`), erscheint statt Einzugs- oder
  Überweisungstext ein Hinweis darauf. So wird kein Einzug angekündigt, der nicht
  mehr stattfindet.
* **Überweisungstext:** nennt Fälligkeitsdatum, Kontoinhaber, IBAN/BIC und den
  Verwendungszweck. Das Konto kommt aus dem Feld *Bankkonto* der Rechnung, ersatzweise
  aus dem ersten Bankkonto des Unternehmens.
* Rechnungsnummer, Auftrag, Projektnummer, Telefonnummer, Hilfebereich-Button und
  Signaturblock sind unverändert aus der bisherigen Vorlage übernommen und in allen
  Fällen gleich.
