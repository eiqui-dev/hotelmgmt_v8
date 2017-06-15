# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services PVT. LTD.
#    (<http://www.serpentcs.com>)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# ---------------------------------------------------------------------------
from openerp import models, fields, api, _


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.model
    def create(self, vals):
        cr, uid, context = self.env.args
        context = dict(context)
        if context.get('invoice_origin', False):
            vals.update({'origin': context['invoice_origin']})
        return super(AccountInvoice, self).create(vals)

    @api.depends('residual','amount_total')
    def update_folio(self):
        fol = self.env['hotel.folio'].search([('name','=',self.origin)])
        if fol:
            inv_pending = 0
            total_inv = 0
            total_folio = fol.amount_total
            for inv in fol.invoice_ids:
                if inv.type != 'out_refund':
                    if inv.state == 'draft':
                        total_inv += inv.amount_total
                        inv_pending += inv.amount_total
                    else:
                        total_inv += inv.amount_total
                        inv_pending += inv.residual
            if total_inv < total_folio:
                inv_pending += total_folio
            fol.invoices_amount = inv_pending
            fol.invoices_paid = total_inv - inv_pending

    #~ @api.multi
    #~ def confirm_paid(self):
        #~ '''
        #~ This method change pos orders states to done when folio invoice
        #~ is in done.
        #~ ----------------------------------------------------------
        #~ @param self: object pointer
        #~ '''
        #~ pos_order_obj = self.env['pos.order']
        #~ res = super(AccountInvoice, self).confirm_paid()
        #~ pos_odr_rec = pos_order_obj.search([('invoice_id', 'in', self._ids)])
        #~ pos_odr_rec and pos_odr_rec.write({'state': 'done'})
        #~ return res

