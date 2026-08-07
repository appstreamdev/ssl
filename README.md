# ssl

Odoo-Anpassungen für app-stream.

## `appstream_invoice_mail`

E-Mail-Vorlage für den Rechnungsversand (Odoo Enterprise 19), die den
Zahlungsabsatz automatisch danach unterscheidet, ob der Rechnungsbetrag

* per **SEPA-Lastschrift** eingezogen wird, oder
* vom Kunden per **Überweisung** gezahlt werden soll.

### Wie die Unterscheidung funktioniert

Die Vorlage liest das Feld `is_sepa_dd_communication` auf `account.move`.
Dieses wird so berechnet:

| Feld *Zahlungshinweis in E-Mail* | Ergebnis |
| --- | --- |
| `Automatisch` (Standard) | SEPA, wenn für den Kunden ein gültiges Mandat (`sdd.mandate`) existiert |
| `SEPA-Lastschrift` | immer SEPA-Text |
| `Überweisung` | immer Überweisungstext |

Für die automatische Erkennung wird `sdd.mandate._get_usable_mandate(company, partner, datum)`
aus dem Enterprise-Modul *SEPA Direct Debit* (`account_sepa_direct_debit`) verwendet — also
exakt dieselbe Logik, die Odoo beim Anlegen einer Lastschriftzahlung nutzt. Steht die Methode
in einer Version nicht zur Verfügung, wird auf eine Suche nach einem aktiven Mandat des
kaufmännischen Partners zurückgefallen. Ist das Modul gar nicht installiert, gilt jede
Rechnung als Überweisung.

Das Modul hängt bewusst nur von `account` ab: alle Zugriffe auf SEPA-spezifische Felder
passieren abgesichert in Python, nicht im QWeb-Body. Dadurch kann die Vorlage nicht durch
ein fehlendes Feld beim Versand abbrechen.

### Textbausteine

Zusätzlich zum reinen Wechsel des Absatzes:

* **SEPA:** nennt optional Mandatsreferenz, Gläubiger-Identifikationsnummer und das
  belastete Kundenkonto.
* **Überweisung:** nennt Fälligkeitsdatum, Kontoinhaber, IBAN/BIC und den Verwendungszweck.
  Das Konto kommt aus `partner_bank_id` der Rechnung, ersatzweise aus dem ersten Bankkonto
  des Unternehmens (`mail_bank_account_id`).
* **Bereits bezahlt:** ist die Rechnung beim Versand schon ausgeglichen
  (`payment_state in ('paid', 'in_payment')`), erscheint stattdessen ein Hinweis darauf —
  so wird kein Einzug angekündigt, der nicht mehr stattfindet.

### Installation

1. Verzeichnis `appstream_invoice_mail` in den Addons-Pfad legen.
2. Apps-Liste aktualisieren, Modul *AppStream: Rechnungs-E-Mail (SEPA / Überweisung)* installieren.

### Als Standardvorlage verwenden

Die Vorlage heißt **„Rechnung: Versand (SEPA-Lastschrift / Überweisung)"** und ist im
Dialog *Senden & Drucken* über die Vorlagenauswahl erreichbar. Sie ersetzt die
Odoo-Standardvorlage `account.email_template_edi_invoice` nicht, damit ein Upgrade des
`account`-Moduls die Anpassung nicht überschreibt.

Der PDF-Anhang wird wie gewohnt vom Versand-Assistenten erzeugt; die Vorlage definiert
deshalb bewusst keinen eigenen Report.

### Manuelles Übersteuern

Auf der Rechnung (Reiter *Weitere Informationen*, neben der Zahlungsbedingung) steht das
Feld *Zahlungshinweis in E-Mail*. Damit lässt sich für Einzelfälle — Kunde mit Mandat zahlt
diese eine Rechnung selbst — der Text vor dem Versand umstellen. Daneben zeigt das
schreibgeschützte Feld *E-Mail-Text: SEPA-Lastschrift*, welche Variante gerade greifen würde.
