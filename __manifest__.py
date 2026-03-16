{
    'name': 'Repair + MRP Integration',
    'version': '16.0.1.0.0',
    'summary': 'Integra Repair Order com MRP para fluxo híbrido com subprodutos',
    'author': 'Paulo Dev',
    'depends': ['repair', 'mrp'],
    'data': [
        'views/repair_order_views.xml',
        'views/mrp_production_views.xml',
        'views/machine_status_views.xml',
    ],
    'installable': True,
    'application': True,
}
