from odoo import models, fields, api
import base64
import io
import xlsxwriter

class RepairOrder(models.Model):
    _inherit = 'repair.order'

    os_number = fields.Char(string="Número da OS", required=True)
    equipment_description = fields.Text(string="Descrição do Equipamento")
    deadline = fields.Date(string="Prazo")
    production_ids = fields.One2many('mrp.production', 'repair_id', string="Ordens de Produção")
    progress_percent = fields.Float(string="Progresso (%)", compute="_compute_progress", store=True)

    @api.depends('production_ids.status')
    def _compute_progress(self):
        for record in self:
            total = len(record.production_ids)
            if total == 0:
                record.progress_percent = 0
            else:
                done = len(record.production_ids.filtered(lambda p: p.status == 'concluido'))
                record.progress_percent = (done / total) * 100

    def action_export_report(self):
        """Exporta relatório Excel das OPs vinculadas à OS"""
        for record in self:
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            sheet = workbook.add_worksheet("Relatório OS")

            # Cabeçalho
            headers = [
                'Número da OS', 'Cliente', 'Equipamento', 'Prazo', 'Progresso (%)',
                'Produto Principal', 'Subproduto', 'Operação', 'Centro de Trabalho',
                'Status', 'Início', 'Fim', 'Observação'
            ]
            for col, header in enumerate(headers):
                sheet.write(0, col, header)

            # Dados
            row = 1
            for prod in record.production_ids:
                sheet.write(row, 0, record.os_number or '')
                sheet.write(row, 1, record.partner_id.name or '')
                sheet.write(row, 2, record.equipment_description or '')
                sheet.write(row, 3, str(record.deadline or ''))
                sheet.write(row, 4, record.progress_percent)
                sheet.write(row, 5, prod.parent_product or '')
                sheet.write(row, 6, prod.sub_product or '')
                sheet.write(row, 7, prod.operation_name or '')
                sheet.write(row, 8, prod.workcenter_name or '')
                sheet.write(row, 9, prod.status or '')
                sheet.write(row, 10, str(prod.start_time or ''))
                sheet.write(row, 11, str(prod.end_time or ''))
                sheet.write(row, 12, prod.deviation_note or '')
                row += 1

            workbook.close()
            file_content = base64.b64encode(output.getvalue())
            output.close()

            return {
                'type': 'ir.actions.act_url',
                'url': 'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,' + file_content.decode(),
                'target': 'new',
            }
