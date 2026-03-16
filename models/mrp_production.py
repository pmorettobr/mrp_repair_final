from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # Vínculo com a Ordem de Reparo
    repair_id = fields.Many2one('repair.order', string='Ordem de Reparo (OS)')

    # Campos de Detalhamento do Processo (Rastreio)
    parent_product = fields.Char(string='Produto Principal / NS')
    sub_product = fields.Char(string='Componente / Sub-produto')
    operation_name = fields.Char(string='Operação Realizada')
    workcenter_name = fields.Char(string='Centro de Trabalho')

    # Status Personalizado (Independente do status nativo do MRP para controle de chão de fábrica)
    status_custom = fields.Selection([
        ('waiting', 'Aguardando'),
        ('in_progress', 'Em Andamento'),
        ('done', 'Concluído'),
        ('rejected', 'Reprovado'),
    ], string='Status Chão de Fábrica', default='waiting', tracking=True)

    # Controle de Tempo
    start_time = fields.Datetime(string='Início Real')
    end_time = fields.Datetime(string='Fim Real')

    # Observações
    deviation_note = fields.Text(string='Observações de Desvio')

    @api.onchange('workcenter_id')
    def _onchange_workcenter_id(self):
        """Preenche automaticamente o nome do centro de trabalho se selecionado."""
        if self.workcenter_id:
            self.workcenter_name = self.workcenter_id.name

    def action_start_custom(self):
        """Ação rápida para marcar como Em Andamento e registrar hora início."""
        self.write({
            'status_custom': 'in_progress',
            'start_time': fields.Datetime.now()
        })

    def action_finish_custom(self):
        """Ação rápida para marcar como Concluído e registrar hora fim."""
        self.write({
            'status_custom': 'done',
            'end_time': fields.Datetime.now()
        })
