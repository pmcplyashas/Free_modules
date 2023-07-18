# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# This module tracks all the inventory moves and captures it in inventory sub-master set,
# then re-directs to Inventory consolidated set after the start and end date is given

{
    'name': 'Power Product Inventory Master',
    'version': '0.1',
    'summary': 'Power set of Master report',
    'sequence': -1,
    'description': """Product Power Master""",
    'depends': ['base', 'stock', 'contacts', 'account', 'purchase', 'product','sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/power_master_inv.xml',
        'views/inv_start_date.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
