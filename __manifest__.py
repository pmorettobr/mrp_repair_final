{
    'name': 'MRP Repair Integration',
    'version': '16.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Integra Ordens de Produção (MRP) com Ordens de Reparo (Repair)',
    'description': """
        Este módulo permite vincular Ordens de Produção a uma Ordem de Reparo.
        Funcionalidades:
        - Vínculo Many2one entre MO e OS.
        - Campos personalizados para rastreio de operação (Produto Pai, Sub-produto, Operação).
        - Status personalizado de chão de fábrica.
        - Cálculo automático de progresso da OS baseado nas MOs vinculadas.
        - Exportação de relatório detalhado em Excel (.xlsx).
    """,
    'author': 'Paulo Moretto (Adaptado para Odoo 16 Community)',
    'website': 'https://github.com/pmorettobr',
    'license': 'LGPL-3',
    'depends': [
        'mrp',
        'repair',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_production_views.xml',
        'views/repair_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'external_dependencies': {
        'python': ['xlsxwriter'],
    },
}
