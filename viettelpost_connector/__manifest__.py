{
    'name': 'Viettel Post Connector',
    'version': '15.0.1.0',
    'summary': 'Connect Odoo Application with Viettel Post',
    'description': """
        The Viettel Post Connector module is an integrated product between the odoo application and the carrier Viettel Post. 
        The application provides features, which through the api to manipulate directly into the dashboard of Viettel Post.
    """,
    'category': 'Services/Connector',
    'support': 'odoo.tangerine@gmail.com',
    'author': 'Tangerine',
    'license': 'OPL-1',
    'depends': [
        'base',
        'mail',
        'sale',
        'sale_management',
        'product',
        'stock',
        'delivery',
        'contacts',
        'report_xlsx'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/api_connect_config_data.xml',
        'data/category_payment_data.xml',
        'data/api_endpoints_config_data.xml',
        'data/viettelpost_national_type_data.xml',
        'data/viettelpost_product_type_data.xml',
        'data/viettelpost_waybill_type_data.xml',
        'data/viettelpost_status_data.xml',
        'data/delivery_carrier_data.xml',
        'data/ir_cron_data.xml',
        'data/sequence.xml',
        'report/report.xml',
        'report/receipt_payment_voucher_report.xml',
        'wizard/account_payment_wizard.xml',
        'wizard/create_store_wizard_views.xml',
        'wizard/print_waybill_wizard.xml',
        'wizard/debs_report_wizard.xml',
        'views/api_connect_config_views.xml',
        'views/api_endpoint_config_views.xml',
        'views/category_payment_views.xml',
        'views/api_connect_history_views.xml',
        'views/viettelpost_province_views.xml',
        'views/viettelpost_district_views.xml',
        'views/viettelpost_ward_views.xml',
        'views/vtp_office_views.xml',
        'views/vtp_service_views.xml',
        'views/vtp_store_views.xml',
        'views/sale_order_views.xml',
        'views/product_template_views.xml',
        'views/delivery_carrier_views.xml',
        'views/vtp_national_type_views.xml',
        'views/vtp_product_type_views.xml',
        'views/vtp_waybill_type_views.xml',
        'views/vtp_status_views.xml',
        'views/res_partner_views.xml',
        'views/stock_picking_views.xml',
        'views/account_payment_views.xml',
        'views/ir_cron_views.xml',
        'views/menus.xml'
    ],
    'assets': {
        'web.assets_qweb': [
            'viettelpost_connector/static/src/xml/button.xml'
        ],
        'web.assets_backend': [
            'viettelpost_connector/static/src/js/handle_button.js'
        ]
    },
    'external_dependencies': {
        'python': ['selenium']
    },
    'images': ['static/description/thumbnail.gif'],
    'application': True
}