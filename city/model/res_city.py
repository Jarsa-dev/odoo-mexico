# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#                  2015 Jarsa - http://www.jarsa.com.mx/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#              Isaac Lopez (isaac@vauxoo.com)
#              Alan Ramos (alan.ramos@jarsa.com.mx)
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

from openerp import models, fields, api


class res_country_state_city(models.Model):
    _description = "Country state city"
    _name = 'res.country.state.city'
    name = fields.Char(size=64, required=True,
                       help='Administrative divisions of a state.')
    state_id = fields.Many2one('res.country.state', string='State',
                               required=True)
    country_id = fields.Many2one('res.country', string='Country', store=True, readonly=True)
    code = fields.Char(string='City Code', size=5,
                       help='The city code in max. five chars.')
    _order = 'name'

    @api.onchange('state_id')
    def _onchange_country(self):
        self.country_id = self.state_id.country_id.id
