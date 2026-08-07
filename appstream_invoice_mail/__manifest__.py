{
    'name': 'AppStream: Rechnungs-E-Mail (SEPA / Überweisung)',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'E-Mail-Vorlage für den Rechnungsversand mit getrennten Zahlungstexten '
               'für SEPA-Lastschrift und Überweisung',
    'description': """
Rechnungs-E-Mail mit automatischer Fallunterscheidung
=====================================================

Stellt eine E-Mail-Vorlage für ``account.move`` bereit, die den Zahlungstext
abhängig davon formuliert, ob der Betrag per SEPA-Lastschrift eingezogen oder
vom Kunden überwiesen wird.

Die Erkennung läuft über ein gültiges SEPA-Mandat (``sdd.mandate`` aus dem
Enterprise-Modul *SEPA Direct Debit*). Pro Rechnung lässt sich das Ergebnis
über das Feld *Zahlungshinweis in E-Mail* manuell übersteuern.
""",
    'author': 'app-stream',
    'website': 'https://www.app-stream.eu',
    'license': 'LGPL-3',
    'depends': ['account'],
    'data': [
        'data/mail_template_invoice.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
}
