from odoo import api, fields, models, tools, _
from odoo.modules import get_module_resource


class AccountMove(models.Model):
    _inherit = 'account.move'

    liquidacion_id = fields.Many2one('account_gt.liquidacion','Liquidacion')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    conciliacion_bancaria = fields.Boolean("Conciliacion bancaria")
    fecha_conciliacion_bancaria = fields.Date("Fecha conciliacion")
