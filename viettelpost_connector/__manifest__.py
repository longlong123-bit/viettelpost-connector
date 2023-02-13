{
    'name': 'Odoo Viettel Post Connector',
    'version': '14.0.1.0',
    'summary': 'Connect Odoo Application with Viettel Post',
    'description': """
        The Odoo Viettel Post Connector module is an integrated product between the odoo application and the carrier Viettel Post. 
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
        'contacts'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/viettelpost_national_type_data.xml',
        'data/api_connect_config_data.xml',
        'data/viettelpost_product_type_data.xml',
        'data/viettelpost_waybill_type_data.xml',
        'data/viettelpost_status_data.xml',
        'data/uom_uom_data.xml',
        'data/delivery_carrier_data.xml',
        'data/api_endpoints_config_data.xml',
        'wizard/create_store_wizard_views.xml',
        'wizard/print_waybill_wizard.xml',
        'views/assets.xml',
        'views/api_connect_config_views.xml',
        'views/api_connect_history_views.xml',
        'views/vtp_country_province_views.xml',
        'views/vtp_country_district_views.xml',
        'views/vtp_country_ward_views.xml',
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
        'views/api_endpoint_config_views.xml',
        'views/menus.xml'
    ],
    'qweb': ['static/src/xml/button.xml'],
    'external_dependencies': {
        'python': ['selenium']
    },
    'images': ['static/description/thumbnail.png'],
    'application': True
}