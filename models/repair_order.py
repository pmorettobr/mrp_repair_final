import io
import base64
from odoo import models, fields, api
from odoo.exceptions import UserError

# Tentativa segura de importar xlsxwriter
try:
    import xlsxwriter
    HAS_XLSXWRITER = True
except ImportError:
    HAS_XLSXWRITER = False

class RepairOrder(models.Model):
    _inherit = 'repair.order'

    os_number = fields.Char(string='Número OS', required=True, copy=False, readonly=True, default='New')
    equipment_description = fields.Text(string='Descrição Detalhada do Equipamento')
    deadline = fields.Date(string='Prazo Limite')
    
    production_ids = fields.One2many('mrp.production', 'repair_id', string='Ordens de Produção Vinculadas')
    progress_percent = fields.Float(string='Progresso (%)', compute='_compute_progress', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('os_number', 'New') == 'New':
                seq = self.env['ir.sequence'].next_by_code('repair.order.seq')
                vals['os_number'] = seq or 'OS/NEW'
        return super(RepairOrder, self).create(vals_list)

    @api.depends('production_ids', 'production_ids.status_custom')
    def _compute_progress(self):
        for order in self:
            if not order.production_ids:
                order.progress_percent = 0.0
                continue
            total = len(order.production_ids)
            completed = len(order.production_ids.filtered(lambda p: p.status_custom == 'done'))
            order.progress_percent = round((completed / total) * 100, 2) if total > 0 else 0.0

    def action_export_report(self):
        self.ensure_one()
        
        if not HAS_XLSXWRITER:
            raise UserError("A biblioteca Python 'xlsxwriter' não está instalada neste servidor. Por favor, instale-a com: pip install xlsxwriter")

        try:
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet('Relatório')

            # Formatos básicos
            header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border': 1})
            cell_fmt = workbook.add_format({'border': 1})
            title_fmt = workbook.add_format({'bold': True, 'font_size': 14})
            
            row = 0
            worksheet.merge_range(row, 0, row, 5, f"OS: {self.os_number}", title_fmt)
            row += 1
            
            worksheet.write(row, 0, "Cliente:", header_fmt)
            worksheet.write(row, 1, self.partner_id.name or '-', cell_fmt)
            worksheet.write(row, 2, "Produto:", header_fmt)
            worksheet.write(row, 3, self.product_id.name or '-', cell_fmt)
            row += 1
            
            worksheet.write(row, 0, "Progresso:", header_fmt)
            worksheet.write(row, 1, f"{self.progress_percent}%", cell_fmt)
            row += 2

            # Cabeçalho da Tabela
            headers = ['MO', 'Componente', 'Operação', 'Status', 'Início', 'Fim']
            for col, h in enumerate(headers):
                worksheet.write(row, col, h, header_fmt)
            row += 1

            for mo in self.production_ids:
                data = [
                    mo.name,
                    mo.sub_product or mo.product_id.name,
                    mo.operation_name or '-',
                    dict(mo._fields['status_custom'].selection).get(mo.status_custom, ''),
                    str(mo.start_time)[:10] if mo.start_time else '-',
                    str(mo.end_time)[:10] if mo.end_time else '-'
                ]
                for col, val in enumerate(data):
                    worksheet.write(row, col, val, cell_fmt)
                row += 1

            workbook.close()
            output.seek(0)
            
            attachment = self.env['ir.attachment'].create({
                'name': f"Relatorio_{self.os_number}.xlsx",
                'type': 'binary',
                'datas': base64.b64encode(output.getvalue()).decode('utf-8'),
                'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            })

            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'self',
            }
        except Exception as e:
            raise UserError(f"Erro ao gerar relatório: {str(e)}")
