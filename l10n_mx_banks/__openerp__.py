# -*- coding: utf-8 -*-
{
    'name': "Mexico's Banks catalog",

    'summary': """A catalog of all banks registered in Mexico""",

    'description': """
        Catalog of all banks in Mexico, 
            
            - this catalog was taken from :
            (http://www.sat.gob.mx/informacion_fiscal/factura_electronica/Documents/catalogo_complemento_nomina_Act.pdf)
    """,

    'author': "Jarsa Sistemas, S.A. de C.V.",
    'website': "http://www.jarsa.com.mx",
    'category': 'Mexico Localization',
    'version': '1.0',
    'depends': ['l10n_mx_res_partner_bank'],
    'data': ['data/res_bank_data.xml'],
}