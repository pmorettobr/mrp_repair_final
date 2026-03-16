{
    'name': 'Repair + MRP Integration',
    'version': '16.0.1.0.0',
    'summary': 'Integra Repair Order com MRP para fluxo híbrido com subprodutos Presonalizacao para WTT-Paulmar',
    'description': """
        Integra Repair Order com MRP para fluxo híbrido:
            - Nova Ordem de Reparo
            - Integrar WorkOrder do MRP no Repair
            - Barra de Processo 
            - Campos Personalizados
            - Relatorios
            
    """,
    'author': 'Paulo Moretto',
    'website": "https://github.com/pmoretto',
    "category": "MRP/Repair",
    'depends': ['repair', 'mrp'],
    'license': 'LGPL-3',
    'data': [
        'views/repair_order_views.xml',
        'views/mrp_production_views.xml',
        'views/machine_status_views.xml',
    ],
    'installable': True,
    'application': True,
}
