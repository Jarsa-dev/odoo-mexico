# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    Israel Cruz Argil (israel.cruz@hesatecnica.com
############################################################################
#    Coded by: Israel Cruz Argil (israel.cruz@hesatecnica.com
#    Financed by: http://www.transportesmar.com.mx/ Jesús Alan Ramos Rodríguez <alan.ramos@transportesmar.com.mx>
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name" : "CFDI - PAC Comercio Digital",
    "version" : "1.0",
    "author" : "Hesatec & Vauxoo",
    "category" : "Localization/Mexico",
    "description" : """This module creates interface for e-invoice files from invoices with Comercio Digital.
    http://www.comercio-digital.mx
Ubuntu Package Depends:
    sudo apt-get install python-soappy
    
Also you need to replace one line from:
FILE: /directory of mexico's localization/l10n_mx_facturae/invoice.py
LINE: 1205
                    'descripcion': line.name or '',
REPLACE WITH:
                    'descripcion': line.name.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
""",
    "website" : "http://www.hesatecnica.com/",
    "license" : "AGPL-3",
    "depends" : ["l10n_mx_facturae_groups", "l10n_mx_params_pac", 
        "l10n_mx_account_tax_category",
        "l10n_mx_facturae_report",
        "l10n_mx_facturae_seq", 
        "l10n_mx_ir_attachment_facturae",
        "l10n_mx_facturae_pac",
        "l10n_mx_facturae_group_show_wizards",
        #"l10n_mx_settings_facturae",
        ],
    "demo" : [],
    "data" : [
        "wizard/wizard_cancel_invoice_pac_cd_view.xml",
        "wizard/wizard_export_invoice_pac_cd_view_v6.xml",
        "invoice_view.xml",
    ],
    "test" : [],
    "installable" : True,
    "active" : False,
    #"sequence": 99,
}
