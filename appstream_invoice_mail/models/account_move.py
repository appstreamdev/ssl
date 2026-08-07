from odoo import api, fields, models

OUT_TYPES = ('out_invoice', 'out_refund')


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_mail_payment_mode = fields.Selection(
        selection=[
            ('auto', 'Automatisch'),
            ('sepa', 'SEPA-Lastschrift'),
            ('transfer', 'Überweisung'),
        ],
        string='Zahlungshinweis in E-Mail',
        default='auto',
        copy=False,
        help="Bestimmt, welcher Zahlungstext in der Rechnungs-E-Mail erscheint.\n"
             "'Automatisch' wertet aus, ob für den Kunden ein gültiges "
             "SEPA-Lastschriftmandat hinterlegt ist.",
    )

    is_sepa_dd_communication = fields.Boolean(
        string='E-Mail-Text: SEPA-Lastschrift',
        compute='_compute_sdd_mail_info',
        help="Technisches Feld: steuert den Zahlungsabsatz der E-Mail-Vorlage.",
    )
    sdd_mail_mandate_ref = fields.Char(
        string='Mandatsreferenz (E-Mail)',
        compute='_compute_sdd_mail_info',
    )
    sdd_mail_debtor_iban = fields.Char(
        string='Kunden-IBAN (E-Mail)',
        compute='_compute_sdd_mail_info',
    )
    sdd_mail_creditor_id = fields.Char(
        string='Gläubiger-ID (E-Mail)',
        compute='_compute_sdd_mail_info',
    )
    mail_bank_account_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string='Bankkonto für Überweisungshinweis',
        compute='_compute_mail_bank_account_id',
        help="Konto, das in der E-Mail bei Zahlung per Überweisung genannt wird.",
    )

    # ------------------------------------------------------------------
    # SEPA-Lastschrift
    # ------------------------------------------------------------------

    def _get_sdd_mail_mandate(self):
        """Gültiges SEPA-Lastschriftmandat für diese Rechnung, sonst ``None``.

        Das Modell ``sdd.mandate`` stammt aus dem Enterprise-Modul
        ``account_sepa_direct_debit``. Ist es nicht installiert, gilt jede
        Rechnung als Überweisung.
        """
        self.ensure_one()
        if 'sdd.mandate' not in self.env or self.move_type not in OUT_TYPES or not self.partner_id:
            return None

        mandate_model = self.env['sdd.mandate'].sudo()
        partner = self.partner_id.commercial_partner_id
        date = self.invoice_date_due or self.invoice_date or fields.Date.context_today(self)

        get_usable_mandate = getattr(mandate_model, '_get_usable_mandate', None)
        if get_usable_mandate:
            try:
                return get_usable_mandate(self.company_id.id, partner.id, date) or None
            except TypeError:
                # Signatur weicht in dieser Version ab -> Suche unten
                pass

        return mandate_model.search([
            ('partner_id', '=', partner.id),
            ('state', '=', 'active'),
            ('company_id', 'in', (self.company_id.id, False)),
        ], limit=1) or None

    @api.depends('move_type', 'partner_id', 'company_id',
                 'invoice_date', 'invoice_date_due', 'invoice_mail_payment_mode')
    def _compute_sdd_mail_info(self):
        for move in self:
            mandate = move._get_sdd_mail_mandate()
            mode = move.invoice_mail_payment_mode or 'auto'
            if mode == 'transfer':
                is_sepa = False
            elif mode == 'sepa':
                is_sepa = True
            else:
                is_sepa = bool(mandate)

            move.is_sepa_dd_communication = is_sepa
            move.sdd_mail_mandate_ref = mandate.display_name if mandate else False
            move.sdd_mail_debtor_iban = (
                mandate.partner_bank_id.acc_number
                if mandate and 'partner_bank_id' in mandate._fields
                else False
            )
            company = move.company_id.sudo()
            move.sdd_mail_creditor_id = (
                company.sdd_creditor_identifier
                if is_sepa and 'sdd_creditor_identifier' in company._fields
                else False
            )

    # ------------------------------------------------------------------
    # Überweisung
    # ------------------------------------------------------------------

    @api.depends('partner_bank_id', 'company_id')
    def _compute_mail_bank_account_id(self):
        for move in self:
            bank = move.partner_bank_id
            if not bank:
                bank = move.company_id.partner_id.bank_ids.filtered(
                    lambda b: not b.company_id or b.company_id == move.company_id
                )[:1]
            move.mail_bank_account_id = bank
