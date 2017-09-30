# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 Solucións Aloxa S.L. <info@aloxa.eu>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID


class HotelConfiguration(osv.osv_memory):
    _name = 'hotel.config.settings'
    _inherit = 'res.config.settings'

    _columns = {
        'parity_pricelist_id': fields.integer('Product Pricelist ID', required=True),
        'parity_restrictions_id': fields.integer('Restrictions ID', required=True)
    }

    def set_parity_pricelist_id(self, cr, uid, ids, context=None):
        parity_pricelist_id = self.browse(cr, uid, ids, context=context).parity_pricelist_id
        return self.pool.get('ir.values').set_default(cr, SUPERUSER_ID, 'hotel.config.settings', 'parity_pricelist_id', parity_pricelist_id)

    def set_parity_restrictions_id(self, cr, uid, ids, context=None):
        parity_restrictions_id = self.browse(cr, uid, ids, context=context).parity_restrictions_id
        return self.pool.get('ir.values').set_default(cr, SUPERUSER_ID, 'hotel.config.settings', 'parity_restrictions_id', parity_restrictions_id)

