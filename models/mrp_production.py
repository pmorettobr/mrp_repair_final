from odoo import models, fields

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    repair_id = fields.Many2one('repair.order', string="Ordem de Reparação")
    parent_product = fields.Char(string="Produto Principal")   # Ex: NS01
    sub_product = fields.Char(string="Subproduto")             # Ex: Haste, Camisa
    operation_name = fields.Char(string="Operação")            # Ex: Brunimento, Solda
    workcenter_name = fields.Char(string="Centro de Trabalho") # Ex: Torno 01, Solda 01
    status = fields.Selection([
        ('aguardando', 'Aguardando'),
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
        ('reprovado', 'Reprovado')
    ], string="Status", default='aguardando')
    start_time = fields.Datetime(string="Início")
    end_time = fields.Datetime(string="Fim")
    deviation_note = fields.Text(string="Desvio / Observação")
