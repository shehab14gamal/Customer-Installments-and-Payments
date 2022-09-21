from odoo import models, fields,api
from odoo.exceptions import ValidationError,UserError
from datetime import datetime,date
class AccountPayment(models.Model):
    _inherit = "account.payment"
    installment_id = fields.Many2one('installment.installment')
