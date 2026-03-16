import io
import xlsxwriter
from odoo import models, fields, api
from odoo.exceptions import UserError

class RepairOrder(models.Model):
    _inherit = 'repair.order'

    os_number = fields.Char(string='Número OS', required=True, copy=False, readonly=True, default='New')
    equipment_description = fields.Text(string='Descrição Detalhada do Equipamento')
    deadline = fields.Date(string='Prazo Limite')
    
    # Relação com MOs
    production_ids = fields.One2many('mrp.production', 'repair_id', string='Ordens de Produção Vinculadas')

    # Campo Calculado
    progress_percent = fields.Float(string='Progresso (%)', compute='_compute_progress', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        """Gera número sequencial simples para a OS."""
        for vals in vals_list:
            if vals.get('os_number', 'New') == 'New':
                # Tenta usar sequência, se falhar usa um placeholder
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
            # Filtra apenas as que estão 'done'
            completed = len(order.production_ids.filtered(lambda p: p.status_custom == 'done'))
            
            order.progress_percent = round((completed / total) * 100, 2) if total > 0 else 0.0

    def action_export_report(self):
        """Gera relatório Excel detalhado."""
        self.ensure_one()
        
        try:
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet('Relatório de Reparo')

            # Formatos
            header_format = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border': 1, 'align': 'center'})
            cell_format = workbook.add_format({'border': 1, 'align': 'left'})
            title_format = workbook.add_format({'bold': True, 'font_size': 14})
            status_done_fmt = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100', 'border': 1, 'align': 'center'})
            status_pending_fmt = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006', 'border': 1, 'align': 'center'})

            # Cabeçalho da OS
            row = 0
            worksheet.merge_range(row, 0, row, 5, f"ORDEM DE REPARO: {self.os_number}", title_format)
            row += 1
            
            worksheet.write(row, 0, "Cliente:", header_format)
            worksheet.write(row, 1, self.partner_id.name or 'N/A', cell_format)
            worksheet.write(row, 2, "Produto:", header_format)
            worksheet.write(row, 3, self.product_id.name or 'N/A', cell_format)
            worksheet.write(row, 4, "Prazo:", header_format)
            worksheet.write(row, 5, str(self.deadline) if self.deadline else 'N/A', cell_format)
            row += 1
            
            worksheet.write(row, 0, "Equipamento:", header_format)
            worksheet.merge_range(row, 1, row, 5, self.equipment_description or 'Sem descrição', cell_format)
            row += 1
            
            worksheet.write(row, 0, "Progresso:", header_format)
            worksheet.write(row, 1, f"{self.progress_percent}%", cell_format)
            row += 2

            # Tabela de MOs
            headers = ['MO Ref', 'Prod. Principal', 'Componente', 'Operação', 'Centro Trabalho', 'Status', 'Início', 'Fim', 'Obs']
            for col_num, header in enumerate(headers):
                worksheet.write(row, col_num, header, header_format)
            row += 1

            for mo in self.production_ids:
                status_label = dict(mo._fields['status_custom'].selection).get(mo.status_custom, mo.status_custom)
                # Escolhe o formato baseado no status
                current_status_fmt = status_done_fmt if mo.status_custom == 'done' else status_pending_fmt
                
                data = [
                    mo.name,
                    mo.parent_product or '-',
                    mo.sub_product or '-',
                    mo.operation_name or '-',
                    mo.workcenter_name or '-',
                    status_label,
                    str(mo.start_time) if mo.start_time else '-',
                    str(mo.end_time) if mo.end_time else '-',
                    mo.deviation_note or '-'
                ]
                
                for col_num, cell_data in enumerate(data):
                    # Aplica formatação de cor apenas na coluna de status (índice 5)
                    if col_num == 5:
                        worksheet.write(row, col_num, cell_data, current_status_fmt)
                    else:
                        worksheet.write(row, col_num, cell_data, cell_format)
                row += 1

            workbook.close()
            output.seek(0)

            # Criar attachment temporário
            attachment = self.env['ir.attachment'].create({
                'name': f"Relatorio_{self.os_number}.xlsx",
                'type': 'binary',
                'datas': output.getvalue().hex(), # Em v16, as vezes é necessário tratar encoding, mas geralmente bytes direto funciona. Se der erro, use .hex() e ajuste o mimetype ou use base64.b64encode
                'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            })
            # Correção para envio binário direto no Odoo 16
            import base64
            attachment.datas = base64.b64encode(output.getvalue()).decode('utf-8')

            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'self',
            }
        except Exception as e:
            raise UserError(f"Erro ao gerar relatório: {str(e)}")
