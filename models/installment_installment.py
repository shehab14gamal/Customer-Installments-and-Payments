from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date


class InstallmentInstallment(models.Model):
    _name = "installment.installment"

    name = fields.Char(string='Number', readonly=1)
    reference = fields.Char()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid')], default='draft')
    date = fields.Date(default=date.today())
    customer_id = fields.Many2one('res.partner', domain=[('customer_rank', '>', 0)], string='Customer')
    customer_image = fields.Image(related='customer_id.image_1920')
    journal_id = fields.Many2one('account.journal', string='Journal')
    account_id = fields.Many2one('account.account', string='Account')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    amount = fields.Float()
    notes = fields.Text()
    payment_ids = fields.One2many('account.payment', 'installment_id')
    move_ids = fields.One2many('account.move', 'installment_id')
    move_count = fields.Integer(compute="_compute_move_count")

    def _compute_move_count(self):
        for rec in self:
            rec.move_count = self.env['account.move'].search_count([('installment_id', '=', self.id)])

    @api.constrains('amount')
    def check_positive_amount(self):
        for rec in self:
            if rec.amount < 0:
                raise ValidationError('The installment amount cannot be negative.')

    def open_action(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'open'
                rec.env['account.move'].create({
                    'partner_id': rec.customer_id.id,
                    'move_type': 'out_invoice',
                    'payment_reference': rec.reference,
                    'invoice_date': date.today(),
                    'installment_id': self.id,
                    'invoice_line_ids': [(0, 0, {
                        'name': "installment",
                        'account_id': rec.account_id.id,
                        'analytic_account_id': rec.analytic_account_id.id,
                        'analytic_tag_ids': rec.analytic_tag_ids.ids,
                        'quantity': 1,
                        'price_unit': rec.amount
                    })]
                })
                rec.name = self.env['ir.sequence'].next_by_code('installment.installment')

    def payment_action(self):

        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {

                'active_model': 'account.move',
                'active_ids': self.move_ids.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def settlement_action(self):
        if self.payment_ids:
            paid_amount = 0
            for pay in self.payment_ids:
                paid_amount += pay.amount
            self.amount -= paid_amount
            self.state = 'paid'
        else:

            self.state = 'paid'

    def set_draft_action(self):
        if self.state != 'draft':
            self.state = 'draft'

    def button_open_journal_items(self):
        return {
            'name': "Journal Items",
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False},
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.customer_id.id), ('move_type', '=', 'out_invoice'),
                       ('installment_id', '=', self.id)]
        }

    def unlink(self):
        if self.state != 'draft':
            raise ValidationError('Can not delete ' + self.state + ' installment')
        super(InstallmentInstallment, self).unlink()
