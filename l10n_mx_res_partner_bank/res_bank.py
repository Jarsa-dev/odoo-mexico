# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Juan Carlos Funes (juan@vauxoo.com)
#    Coded by: Luis Torres (luis_t@vauxoo.com)
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Coded by: isaac (isaac@vauxoo.com)
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
from openerp import fields, models, api


class res_partner_bank(models.Model):
    _inherit = 'res.partner.bank'

    @api.one
    @api.depends('acc_number')
    def _get_last_digits(self):
        if self.acc_number == False:
            self.last_acc_number = ' '
        else:
            self.last_acc_number = str(self.acc_number)[-4:]

    clabe = fields.Char(string='Clabe Interbancaria',
                        size=64,
                        required=False)
    last_acc_number = fields.Char(compute='_get_last_digits',
                                  string='Last 4 digits',
                                  store=True,
                                  size=4,)
    currency2_id = fields.Many2one('res.currency',
                                   string='Currency',)
    reference = fields.Char(string='Reference',
                            size=64,
                            help='Reference used in this bank')
