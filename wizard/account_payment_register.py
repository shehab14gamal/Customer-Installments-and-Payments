# -*- coding: utf-8 -*-
from collections import defaultdict
from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, frozendict


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        payments = self._create_payments()

        if self._context.get('dont_redirect_to_payments'):
            return True

        action = {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'context': {'create': False},
        }
        if len(payments) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': payments.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', payments.ids)],
            })
        remaining_amount = 0
        for line in self.line_ids:
            if line.move_id.installment_id:
                remaining_amount += line.move_id.amount_residual
                for payment in payments:
                    payment.installment_id = line.move_id.installment_id.id
            line.move_id.installment_id.payment_ids = self.env['account.payment'].search(
                [('installment_id', '=', line.move_id.installment_id.id)])

        if remaining_amount == 0:
            for line in self.line_ids:
                line.move_id.installment_id.state = 'paid'

        return action
