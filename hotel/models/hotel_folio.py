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
from openerp.exceptions import except_orm, UserError, ValidationError
from openerp.tools import misc, DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import models, fields, api, _
from openerp import workflow
from decimal import Decimal
from dateutil.relativedelta import relativedelta
import datetime
import time
import pytz
import logging
_logger = logging.getLogger(__name__)


def _offset_format_timestamp1(src_tstamp_str, src_format, dst_format,
                              ignore_unparsable_time=True, context=None):
    """
    Convert a source timeStamp string into a destination timeStamp string,
    attempting to apply the
    correct offset if both the server and local timeZone are recognized,or no
    offset at all if they aren't or if tz_offset is false (i.e. assuming they
    are both in the same TZ).

    @param src_tstamp_str: the STR value containing the timeStamp.
    @param src_format: the format to use when parsing the local timeStamp.
    @param dst_format: the format to use when formatting the resulting
     timeStamp.
    @param server_to_client: specify timeZone offset direction (server=src
                             and client=dest if True, or client=src and
                             server=dest if False)
    @param ignore_unparsable_time: if True, return False if src_tstamp_str
                                   cannot be parsed using src_format or
                                   formatted using dst_format.

    @return: destination formatted timestamp, expressed in the destination
             timezone if possible and if tz_offset is true, or src_tstamp_str
             if timezone offset could not be determined.
    """
    if not src_tstamp_str:
        return False
    res = src_tstamp_str
    if src_format and dst_format:
        try:
            # dt_value needs to be a datetime.datetime object\
            # (so notime.struct_time or mx.DateTime.DateTime here!)
            dt_value = datetime.datetime.strptime(src_tstamp_str, src_format)
            if context.get('tz', False):
                try:
                    import pytz
                    src_tz = pytz.timezone(context['tz'])
                    dst_tz = pytz.timezone('UTC')
                    src_dt = src_tz.localize(dt_value, is_dst=True)
                    dt_value = src_dt.astimezone(dst_tz)
                except Exception:
                    pass
            res = dt_value.strftime(dst_format)
        except Exception:
            # Normal ways to end up here are if strptime or strftime failed
            if not ignore_unparsable_time:
                return False
            pass
    return res





class HotelFolio(models.Model):

    @api.multi
    def name_get(self):
        res = []
        disp = ''
        for rec in self:
            if rec.order_id:
                disp = str(rec.name)
                res.append((rec.id, disp))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        args += ([('name', operator, name)])
        mids = self.search(args, limit=100)
        return mids.name_get()

    @api.model
    def _needaction_count(self, domain=None):
        """
         Show a count of draft state folio on the menu badge.
         @param self: object pointer
        """
        return self.search_count([('state', '=', 'draft')])

    #~ @api.model
    #~ def _get_checkin(self):
        #~ if self._context.get('tz'):
            #~ to_zone = self._context.get('tz')
        #~ else:
            #~ to_zone = 'UTC'
        #~ return _offset_format_timestamp1(time.strftime("%Y-%m-%d 12:00:00"),
                                         #~ '%Y-%m-%d %H:%M:%S',
                                         #~ '%Y-%m-%d %H:%M:%S',
                                         #~ ignore_unparsable_time=True,
                                         #~ context={'tz': to_zone})

    #~ @api.model
    #~ def _get_checkout(self):
        #~ if self._context.get('tz'):
            #~ to_zone = self._context.get('tz')
        #~ else:
            #~ to_zone = 'UTC'
        #~ tm_delta = datetime.timedelta(days=1)
        #~ return datetime.datetime.strptime(_offset_format_timestamp1
                                          #~ (time.strftime("%Y-%m-%d 12:00:00"),
                                           #~ '%Y-%m-%d %H:%M:%S',
                                           #~ '%Y-%m-%d %H:%M:%S',
                                           #~ ignore_unparsable_time=True,
                                           #~ context={'tz': to_zone}),
                                          #~ '%Y-%m-%d %H:%M:%S') + tm_delta

    @api.multi
    def copy(self, default=None):
        '''
        @param self: object pointer
        @param default: dict of default values to be set
        '''
        return self.env['sale.order'].copy(default=default)

    @api.multi
    def _invoiced(self, name, arg):
        '''
        @param self: object pointer
        @param name: Names of fields.
        @param arg: User defined arguments
        '''
        return self.env['sale.order']._invoiced(name, arg)

    @api.multi
    def _invoiced_search(self, obj, name, args):
        '''
        @param self: object pointer
        @param name: Names of fields.
        @param arg: User defined arguments
        '''
        return self.env['sale.order']._invoiced_search(obj, name, args)

    _name = 'hotel.folio'
    _description = 'hotel folio new'
    _rec_name = 'order_id'
    _order = 'id'
    _inherit = ['ir.needaction_mixin','mail.thread']

    name = fields.Char('Folio Number', readonly=True, index=True,
                       default='New')
    order_id = fields.Many2one('sale.order', 'Order', delegate=True,
                               required=True, ondelete='cascade')
    #~ checkin = fields.Datetime('Check In', required=True, readonly=True,
                                   #~ states={'draft': [('readonly', False)]},
                                   #~ default=_get_checkin)
    #~ checkout = fields.Datetime('Check Out', required=True, readonly=True,
                                    #~ states={'draft': [('readonly', False)]},
                                    #~ default=_get_checkout)
    room_lines = fields.One2many('hotel.reservation', 'folio_id',
                                 readonly=True,
                                 states={'done': [('readonly', False)]},
                                 help="Hotel room reservation detail.")
    service_lines = fields.One2many('hotel.service.line', 'folio_id',
                                    readonly=True,
                                    states={'done': [('readonly', False)]},
                                    help="Hotel services detail provide to"
                                    "customer and it will include in "
                                    "main Invoice.")
    hotel_policy = fields.Selection([('prepaid', 'On Booking'),
                                     ('manual', 'On Check In'),
                                     ('picking', 'On Checkout')],
                                    'Hotel Policy', default='manual',
                                    help="Hotel policy for payment that "
                                    "either the guest has to payment at "
                                    "booking time or check-in "
                                    "check-out time.")
    duration = fields.Float('Duration in Days',
                            help="Number of days which will automatically "
                            "count from the check-in and check-out date. ")
    currrency_ids = fields.One2many('currency.exchange', 'folio_no',
                                    readonly=True)
    hotel_invoice_id = fields.Many2one('account.invoice', 'Invoice')
    invoices_amount = fields.Monetary(compute='compute_invoices_amount',store=True)
    refund_amount = fields.Monetary(compute='_compute_invoices_refund')
    invoices_paid = fields.Monetary(compute='compute_invoices_amount',store=True)
    booking_pending = fields.Integer ('Booking pending', compute='_compute_booking_pending')
    cardex_count = fields.Integer('Cardex counter', compute='_compute_cardex_count')
    cardex_pending = fields.Boolean('Cardex Pending', compute='_compute_cardex_pending')
    cardex_pending_num = fields.Integer('Cardex Pending', compute='_compute_cardex_pending')
    checkins_reservations = fields.Boolean('checkins reservations',compute='_compute_checkins')
    checkouts_reservations = fields.Boolean('checkouts reservations',compute='_compute_checkouts')
    partner_internal_comment = fields.Text(string='Internal Partner Notes',related='partner_id.comment')

    @api.multi
    def _compute_checkins(self):
        for fol in self:
            for line in fol.room_lines:
                checkin_dt = datetime.datetime.strptime(line.checkin, DEFAULT_SERVER_DATETIME_FORMAT)
                checkin_str = checkin_dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                if checkin_str == datetime.datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT):
                    fol.checkins_reservations = True
                    return True

    @api.multi
    def _compute_checkouts(self):
        for fol in self:
            for line in fol.room_lines:
                checkout_dt = datetime.datetime.strptime(line.checkout, DEFAULT_SERVER_DATETIME_FORMAT)
                checkout_str = checkout_dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                if checkout_str == datetime.datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT):
                    fol.checkouts_reservations = True

    #~ @api.model
    #~ def checks_today(self):
        #~ self.env['hotel.folio'].search([]).write({'checkins_reservations':False,'checkout_reservations':False})
        #~ today_start = datetime.datetime.now().replace(hour=00, minute=00, second=00).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        #~ today_end = datetime.datetime.now().replace(hour=00, minute=00, second=00).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        #~ reservations = self.env[('hotel.reservation')].search([
            #~ ('checkout','>=',today_start),
            #~ ('checkin','<=',today_end)
            #~ ])
        #~ folios_out_ids = reservations.filtered(lambda r: r.checkout >= today_start).mapped('folio_id.id')
        #~ folios_in_ids = reservations.filtered(lambda r: r.checkin <= today_end).mapped('folio_id.id')
        #~ self.env['hotel.folio'].search([('id','in',folios_in_ids)]).write({'checkins_reservations':True})
        #~ self.env['hotel.folio'].search([('id','in',folios_out_ids)]).write({'checkout_reservations':True})

    @api.depends('invoice_ids.residual','invoice_ids.amount_total')
    def compute_invoices_amount(self):
        for fol in self:
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
                inv_pending = total_folio - total_inv
            fol.invoices_amount = inv_pending
            fol.invoices_paid = total_folio - inv_pending
            _logger.info("ONCHANGEEEE FULLLL")
            _logger.info(fol.invoices_amount)

    @api.multi
    def _compute_invoices_refund(self):
        self.ensure_one()
        inv_pending = 0
        total_inv = 0
        total_folio = self.amount_total
        for inv in self.invoice_ids:
            if inv.type == 'out_refund':
                total_inv += inv.amount_total
        self.refund_amount = total_inv

    @api.multi
    def action_invoices(self):
        self.ensure_one()
        invoices = self.mapped('invoice_ids.id')
        return{
        'name': _('Invoices'),
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'account.invoice',
        'type': 'ir.actions.act_window',
        'domain': [('id','in', invoices),('type','!=','out_refund')]
        }

    @api.multi
    def action_refunds_invoices(self):
        self.ensure_one()
        invoices = self.mapped('invoice_ids.id')
        return{
        'name': _('Invoices'),
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'account.invoice',
        'type': 'ir.actions.act_window',
        'domain': [('id','in', invoices),('type','=','out_refund')]
        }


    @api.multi
    def action_checks(self):
        self.ensure_one()
        rooms = self.mapped('room_lines.id')
        return {
        'name': _('Cardexs'),
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'cardex',
        'type': 'ir.actions.act_window',
        'domain': [('reservation_id','in', rooms)]
        }

    @api.multi
    def action_folios_in(self):
        checkin_dt = datetime.datetime.now().replace(hour=00, minute=00, second=00)
        checkout_dt = datetime.datetime.now().replace(hour=23, minute=59, second=59)
        local = pytz.timezone(self.env.context.get('tz','UTC'))
        local_dt_in = local.localize(checkin_dt, is_dst=False)
        utc_dt_in = local_dt_in.astimezone(pytz.utc)
        local_dt_out = local.localize(checkout_dt, is_dst=False)
        utc_dt_out = local_dt_out.astimezone(pytz.utc)
        reservations = self.env['hotel.reservation'].search([
                    ('checkin','>=',utc_dt_in.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                    ('checkin','<=',utc_dt_out.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                    ('state','not in',['booking','cancelled'])])
        folios = reservations.mapped('folio_id.id')
        return {
            'name': _('Checkins'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hotel.folio',
            'type': 'ir.actions.act_window',
            'domain': [('id','in', folios)]
        }

    @api.multi
    def action_folios_out(self):
        checkin_dt = datetime.datetime.now().replace(hour=00, minute=00, second=00)
        checkout_dt = datetime.datetime.now().replace(hour=23, minute=59, second=59)
        local = pytz.timezone(self.env.context.get('tz','UTC'))
        local_dt_in = local.localize(checkin_dt, is_dst=False)
        utc_dt_in = local_dt_in.astimezone(pytz.utc)
        local_dt_out = local.localize(checkin_dt, is_dst=False)
        utc_dt_out = local_dt_out.astimezone(pytz.utc)
        reservations = self.env['hotel.reservation'].search([
                    ('checkout','>=',utc_dt_in.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                    ('checkout','<=',utc_dt_out.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                    ('state','=','booking')])
        folios = reservations.mapped('folio_id.id')
        return {
            'name': _('Checkouts'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hotel.folio',
            'type': 'ir.actions.act_window',
            'domain': [('id','in', folios)]
        }

    @api.multi
    def action_folios_amount(self):
        reservations = self.env['hotel.reservation'].search([
                    ('checkout','<=',datetime.datetime.now().replace(hour=00, minute=00, second=00).strftime(DEFAULT_SERVER_DATETIME_FORMAT))
                     ])
        folio_ids = reservations.mapped('folio_id.id')
        folios = self.env['hotel.folio'].search([('id','in',folio_ids)])
        folios = folios.filtered(lambda r: r.invoices_amount > 0)
        return {
        'name': _('Pending'),
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'hotel.folio',
        'type': 'ir.actions.act_window',
        'domain': [('id','in', folios.ids)]
        }



    @api.multi
    def _compute_cardex_count(self):
        num_cardex = 0
        for reser in self.room_lines:
            num_cardex += len(reser.cardex_ids)
        self.cardex_count = num_cardex

    @api.multi
    def _compute_cardex_pending(self):
        pending = 0
        for reser in self.room_lines:
            pending += reser.adults + reser.children - len(reser.cardex_ids)
        if pending <= 0:
            self.cardex_pending = False
        else:
            self.cardex_pending = True
        self.cardex_pending_num = pending


    @api.multi
    def go_to_currency_exchange(self):
        '''
         when Money Exchange button is clicked then this method is called.
        -------------------------------------------------------------------
        @param self: object pointer
        '''
        cr, uid, context = self.env.args
        context = dict(context)
        for rec in self:
            if rec.partner_id.id and len(rec.room_lines) != 0:
                context.update({'folioid': rec.id, 'guest': rec.partner_id.id,
                                'room_no': rec.room_lines[0].product_id.name,
                                'hotel': rec.warehouse_id.id})
                self.env.args = cr, uid, misc.frozendict(context)
            else:
                raise except_orm(_('Warning'), _('Please Reserve Any Room.'))
        return {'name': _('Currency Exchange'),
                'res_model': 'currency.exchange',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'form,tree',
                'view_type': 'form',
                'context': {'default_folio_no': context.get('folioid'),
                            'default_hotel_id': context.get('hotel'),
                            'default_guest_name': context.get('guest'),
                            'default_room_number': context.get('room_no')
                            },
                }

    @api.constrains('room_lines')
    def folio_room_lines(self):
        '''
        This method is used to validate the room_lines.
        ------------------------------------------------
        @param self: object pointer
        @return: raise warning depending on the validation
        '''
        folio_rooms = []
        for room in self[0].room_lines:
            if room.product_id.id in folio_rooms:
                raise ValidationError(_('You Cannot Take Same Room Twice'))
            folio_rooms.append(room.product_id.id)

#     @api.constrains('checkin', 'checkout')
#     def check_dates(self):
#         '''
#         This method is used to validate the checkin and checkout.
#         -------------------------------------------------------------------
#         @param self: object pointer
#         @return: raise warning depending on the validation
#         '''
#         if self.checkin >= self.checkout:
#                 raise ValidationError(_('Check in Date Should be \
#                 less than the Check Out Date!'))
#         if self.date_order and self.checkin:
#             if self.checkin < self.date_order:
#                 raise ValidationError(_('Check in date should be \
#                 greater than the current date.'))

    #~ @api.onchange('checkout', 'checkin')
    #~ def onchange_dates(self):
        #~ '''
        #~ This mathod gives the duration between check in and checkout
        #~ if customer will leave only for some hour it would be considers
        #~ as a whole day.If customer will check in checkout for more or equal
        #~ hours, which configured in company as additional hours than it would
        #~ be consider as full days
        #~ --------------------------------------------------------------------
        #~ @param self: object pointer
        #~ @return: Duration and checkout
        #~ '''
        #~ company_obj = self.env['res.company']
        #~ configured_addition_hours = 0
        #~ company_ids = company_obj.search([])
        #~ if company_ids.ids:
            #~ configured_addition_hours = company_ids[0].additional_hours
        #~ myduration = 0
        #~ checkin = self.checkin
        #~ checkout = self.checkout
        #~ if checkin and checkout:
            #~ server_dt = DEFAULT_SERVER_DATETIME_FORMAT
            #~ chkin_dt = datetime.datetime.strptime(checkin, server_dt)
            #~ chkout_dt = datetime.datetime.strptime(checkout, server_dt)
            #~ dur = chkout_dt - chkin_dt
            #~ sec_dur = dur.seconds
            #~ if (not dur.days and not sec_dur) or (dur.days and not sec_dur):
                #~ myduration = dur.days
            #~ else:
                #~ myduration = dur.days + 1
            #~ if configured_addition_hours > 0:
                #~ additional_hours = abs((dur.seconds / 60) / 60)
                #~ if additional_hours >= configured_addition_hours:
                    #~ myduration += 1
        #~ self.duration = myduration

    @api.model
    def create(self, vals, check=True):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        @return: new record set for hotel folio.
        """
        if not 'service_lines' and 'folio_id' in vals:
            tmp_room_lines = vals.get('room_lines', [])
            vals['order_policy'] = vals.get('hotel_policy', 'manual')
            vals.update({'room_lines': []})
            folio_id = super(HotelFolio, self).create(vals)
            for line in (tmp_room_lines):
                line[2].update({'folio_id': folio_id})
            vals.update({'room_lines': tmp_room_lines})
            folio_id.write(vals)
        else:
            if not vals:
                vals = {}
            vals['name'] = self.env['ir.sequence'].next_by_code('hotel.folio')
            folio_id = super(HotelFolio, self).create(vals)

        return folio_id

    #~ @api.multi
    #~ def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        #~ folio_room_line_obj = self.env['folio.room.line']
#        reservation_line_obj = self.env['hotel.room.reservation.line']
        #~ product_obj = self.env['product.product']
        #~ h_room_obj = self.env['hotel.room']
        #~ room_lst1 = []
        #~ for rec in self:
            #~ for res in rec.room_lines:
                #~ room_lst1.append(res.product_id.id)
        #~ folio_write = super(HotelFolio, self).write(vals)
        #~ room_lst = []
        #~ for folio_obj in self:
            #~ for folio_rec in folio_obj.room_lines:
                #~ room_lst.append(folio_rec.product_id.id)
            #~ new_rooms = set(room_lst).difference(set(room_lst1))
            #~ if len(list(new_rooms)) != 0:
                #~ room_list = product_obj.browse(list(new_rooms))
                #~ for rm in room_list:
                    #~ room_obj = h_room_obj.search([('name', '=', rm.name)])
                    #~ vals = {'room_id': room_obj.id,
                            #~ 'checkin': folio_obj.checkin,
                            #~ 'checkout': folio_obj.checkout,
                            #~ 'folio_id': folio_obj.id,
                            #~ }
                    #~ folio_room_line_obj.create(vals)
            #~ if len(list(new_rooms)) == 0:
                #~ room_list_obj = product_obj.browse(room_lst1)
                #~ for rom in room_list_obj:
                    #~ room_obj = h_room_obj.search([('name', '=', rom.name)])
                    #~ room_vals = {'room_id': room_obj.id,
                                 #~ 'checkin': folio_obj.checkin,
                                 #~ 'checkout': folio_obj.checkout,
                                 #~ 'folio_id': folio_obj.id,
                                 #~ }
                    #~ folio_romline_rec = (folio_room_line_obj.search
                                         #~ ([('folio_id', '=', folio_obj.id)]))
                    #~ folio_romline_rec.write(room_vals)
#            if folio_obj.reservation_id:
#                for reservation in folio_obj.reservation_id:
#                    reservation_obj = (reservation_line_obj.search
#                                       ([('reservation_id', '=',
#                                          reservation.id)]))
#                    if len(reservation_obj) == 1:
#                        for line_id in reservation.reservation_line:
#                            line_id = line_id.reserve
#                            for room_id in line_id:
#                                vals = {'room_id': room_id.id,
#                                        'checkin': folio_obj.checkin,
#                                        'checkout': folio_obj.checkout,
#                                        'state': 'assigned',
#                                        'reservation_id': reservation.id,
#                                        }
#                                reservation_obj.write(vals)
        #~ return folio_write

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        '''
        When you change warehouse it will update the warehouse of
        the hotel folio as well
        ----------------------------------------------------------
        @param self: object pointer
        '''
        return self.order_id._onchange_warehouse_id()

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        '''
        When you change partner_id it will update the partner_invoice_id,
        partner_shipping_id and pricelist_id of the hotel folio as well
        ---------------------------------------------------------------
        @param self: object pointer
        '''
        if self.partner_id:
            partner_rec = self.env['res.partner'].browse(self.partner_id.id)
            order_ids = [folio.order_id.id for folio in self]
            if not order_ids:
                self.partner_invoice_id = partner_rec.id
                self.partner_shipping_id = partner_rec.id
                self.pricelist_id = partner_rec.property_product_pricelist.id
                raise UserError('Not Any Order For  %s ' % (partner_rec.name))
            else:
                self.partner_invoice_id = partner_rec.id
                self.partner_shipping_id = partner_rec.id
                self.pricelist_id = partner_rec.property_product_pricelist.id
            for line in self.room_lines:
                _logger.info(line.id)
                tz = self._context.get('tz')
                chkin_dt = fields.Datetime.from_string(line.checkin)
                chkout_dt = fields.Datetime.from_string(line.checkout)
                if tz:
                    chkin_dt = chkin_dt.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(tz))
                    chkout_dt = chkout_dt.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(tz))
                days_diff = abs((chkout_dt - chkin_dt).days)
                res = line.prepare_reservation_lines(chkin_dt, days_diff)
                line.reservation_lines = res['commands']
                line.price_unit = res['total_price']
        self.currency_id = self.env.ref('base.main_company').currency_id
        #WARNING MESSAGES IN PARTNER FOR FOLIOS
        if not self.partner_id:
            return
        warning = {}
        title = False
        message = False
        partner = self.partner_id

        # If partner has no warning, check its company
        if partner.sale_warn == 'no-message' and partner.parent_id:
            partner = partner.parent_id

        if partner.sale_warn != 'no-message':
            # Block if partner only has warning but parent company is blocked
            if partner.sale_warn != 'block' and partner.parent_id and partner.parent_id.sale_warn == 'block':
                partner = partner.parent_id
            title =  _("Warning for %s") % partner.name
            message = partner.sale_warn_msg
            warning = {
                    'title': title,
                    'message': message,
            }
            if self.partner_id.sale_warn == 'block':
                self.update({'partner_id': False, 'partner_invoice_id': False, 'partner_shipping_id': False, 'pricelist_id': False})
                return {'warning': warning}

        if warning:
            return {'warning': warning}

    @api.multi
    def button_dummy(self):
        '''
        @param self: object pointer
        '''
        for folio in self:
            folio.order_id.button_dummy()
        return True

    @api.multi
    def action_done(self):
        self.write({'state': 'done'})
        for line in self.room_lines:
            line.write({'state': 'done'})


    @api.multi
    def action_invoice_create(self, grouped=False, states=None):
        '''
        @param self: object pointer
        '''
        if states is None:
            states = ['confirmed', 'done']
        order_ids = [folio.order_id.id for folio in self]
        room_lst = []
        sale_obj = self.env['sale.order'].browse(order_ids)
        invoice_id = (sale_obj.action_invoice_create
                      (grouped=False, states=['confirmed', 'done']))
        for line in self:
            values = {'invoiced': True,
                      'state': 'progress' if grouped else 'progress',
                      'hotel_invoice_id': invoice_id
                      }
            line.write(values)
            for rec in line.room_lines:
                room_lst.append(rec.product_id)
            for room in room_lst:
                room_obj = self.env['hotel.room'
                                    ].search([('name', '=', room.name)])
        return invoice_id

    @api.multi
    def action_invoice_cancel(self):
        '''
        @param self: object pointer
        '''
        order_ids = [folio.order_id.id for folio in self]
        sale_obj = self.env['sale.order'].browse(order_ids)
        res = sale_obj.action_invoice_cancel()
        for sale in self:
            for line in sale.order_line:
                line.write({'invoiced': 'invoiced'})
        sale.write({'state': 'invoice_except'})
        return res

    @api.multi
    def action_cancel(self):
        '''
        @param self: object pointer
        '''
        order_ids = [folio.order_id.id for folio in self]
        sale_obj = self.env['sale.order'].browse(order_ids)
        rv = sale_obj.action_cancel()
        for res in self.room_lines:
            res.action_cancel()
        for sale in self:
            for pick in sale.picking_ids:
                workflow.trg_validate(self._uid, 'stock.picking', pick.id,
                                      'button_cancel', self._cr)
            for invoice in sale.invoice_ids:
                workflow.trg_validate(self._uid, 'account.invoice',
                                      invoice.id, 'invoice_cancel',
                                      self._cr)
                sale.write({'state': 'cancel'})
        return rv

    @api.multi
    def action_confirm(self):
        for order in self.order_id:
            order.state = 'sale'
            order.order_line._action_procurement_create()
            for room in self.room_lines:
                room.write({'state': 'confirm','to_assign':False})
            if not order.project_id:
                for line in order.order_line:
                    if line.product_id.invoice_policy == 'cost':
                        order._create_analytic_account()
                        break
        if self.env['ir.values'].get_default('sale.config.settings',
                                             'auto_done_setting'):
            self.order_id.action_done()

    @api.multi
    def test_state(self, mode):
        '''
        @param self: object pointer
        @param mode: state of workflow
        '''
        write_done_ids = []
        write_cancel_ids = []
        if write_done_ids:
            test_obj = self.env['sale.order.line'].browse(write_done_ids)
            test_obj.write({'state': 'done'})
        if write_cancel_ids:
            test_obj = self.env['sale.order.line'].browse(write_cancel_ids)
            test_obj.write({'state': 'cancel'})

    @api.multi
    def action_ship_create(self):
        '''
        @param self: object pointer
        '''
        for folio in self:
            folio.order_id.action_ship_create()
        return True

    @api.multi
    def action_ship_end(self):
        '''
        @param self: object pointer
        '''
        for order in self:
            order.write({'shipped': True})

    @api.multi
    def has_stockable_products(self):
        '''
        @param self: object pointer
        '''
        for folio in self:
            folio.order_id.has_stockable_products()
        return True

    @api.multi
    def action_cancel_draft(self):
        '''
        @param self: object pointer
        '''
        if not len(self._ids):
            return False
        for room in self.room_lines:
            room.state = 'draft'
        query = "select id from sale_order_line \
        where order_id IN %s and state=%s"
        self._cr.execute(query, (tuple(self._ids), 'cancel'))
        cr1 = self._cr
        line_ids = map(lambda x: x[0], cr1.fetchall())
        self.write({'state': 'draft', 'invoice_ids': [], 'shipped': 0})
        sale_line_obj = self.env['sale.order.line'].browse(line_ids)
        sale_line_obj.write({'invoiced': False, 'state': 'draft',
                             'invoice_lines': [(6, 0, [])]})
        return True
