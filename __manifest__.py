# -*- coding: utf-8 -*-
{
    'name': "Muti Loyalty Program",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sales_order_inherit.xml',
        'views/account_inheritances.xml',
        'data/card_sequence.xml',
        'views/card_card.xml',
        'views/card_type.xml',
        'views/card_period.xml',
        'views/card_category.xml',
        'views/card_rule.xml',
        'menu/card_menu.xml',
        # 'views/pos_layout_view.xml',
    ],
    'qweb': [
        # 'static/src/xml/layout_template.xml',
        ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}