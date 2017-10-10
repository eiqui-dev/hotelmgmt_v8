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
from openerp import models, api


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    @api.multi
    @api.depends('name')
    def name_get(self):
        pricelist_id = self.env['ir.values'].sudo().get_default('hotel.config.settings', 'parity_pricelist_id')
        if pricelist_id:
            pricelist_id = int(pricelist_id)
        org_name = super(ProductPricelist, self).name_get()
        names = []
        for record in self:
            if record.id == pricelist_id:
                names.append((record.id, '%s (Parity)' % record.name))
            else:
                names.append((record.id, record.name))
        return names
