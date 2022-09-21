from odoo import models, fields,api
from odoo.exceptions import ValidationError,UserError
from datetime import datetime,date
class AccountMove(models.Model):
    _inherit = "account.move"
    installment_id = fields.Many2one('installment.installment')