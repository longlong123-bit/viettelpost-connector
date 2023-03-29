{
    'name': 'Account Payment Extension',
    'version': '15.0.1.0',
    'summary': '',
    'description': """""",
    'category': 'Accounting/Accounting',
    'support': 'odoo.tangerine@gmail.com',
    'author': 'Tangerine',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'viettelpost_connector',
        'report_xlsx'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/category_payment_data.xml',
        'data/sequence.xml',
        'report/report.xml',
        'report/receipt_payment_voucher_report.xml',
        'wizard/debts_report_wizard.xml',
        'views/category_payment_views.xml',
        'views/account_payment_views.xml',
        'views/menus.xml'
    ],
    'application': True
}