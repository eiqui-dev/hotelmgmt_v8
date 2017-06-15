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
from openerp.tools import misc, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import models, fields, api, _
from openerp import workflow
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import pytz
import time
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
            dt_value = datetime.strptime(src_tstamp_str, src_format)
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

COLOR_TYPES = {
    'pre-reservation': '#A4A4A4',
    'reservation': '#0000FF',
    'stay': '#FF00BF',
    'checkout': '#01DF01',
    'dontsell': '#000000',
    'staff': '#FF4000',
    'directsale': '#8A084B'
}

class HotelReservation(models.Model):

    @api.one
    def copy(self, default=None):
        '''
        @param self: object pointer
        @param default: dict of default values to be set
        '''
        return self.env['sale.order.line'].copy(default=default)

    @api.multi
    def _amount_line(self, field_name, arg):
        '''
        @param self: object pointer
        @param field_name: Names of fields.
        @param arg: User defined arguments
        '''
        return self.env['sale.order.line']._amount_line(field_name, arg)

    @api.multi
    def _number_packages(self, field_name, arg):
        '''
        @param self: object pointer
        @param field_name: Names of fields.
        @param arg: User defined arguments
        '''
        return self.env['sale.order.line']._number_packages(field_name, arg)

    @api.multi
    def _get_checkin(self):
        folio = False
        if 'folio_id' in self._context:
            folio = self.env['hotel.folio'].search([('id','=', self._context['folio_id'])])
        if folio and folio.room_lines:
            return folio.room_lines[0].checkin
        else:
            if self._context.get('tz'):
                to_zone = self._context.get('tz')
            else:
                to_zone = 'UTC'
            return _offset_format_timestamp1(time.strftime("%Y-%m-%d 12:00:00"),
                                             '%Y-%m-%d %H:%M:%S',
                                             '%Y-%m-%d %H:%M:%S',
                                             ignore_unparsable_time=True,
                                             context={'tz': to_zone})

    @api.model
    def _get_checkout(self):
        folio = False
        if 'folio_id' in self._context:
            folio = self.env['hotel.folio'].search([('id','=',self._context['folio_id'])])
        if folio and folio.room_lines:
            return folio.room_lines[0].checkout
        else:
            if self._context.get('tz'):
                to_zone = self._context.get('tz')
            else:
                to_zone = 'UTC'
            tm_delta = timedelta(days=1)
            return datetime.strptime(_offset_format_timestamp1
                                      (time.strftime("%Y-%m-%d 12:00:00"),
                                       '%Y-%m-%d %H:%M:%S',
                                       '%Y-%m-%d %H:%M:%S',
                                       ignore_unparsable_time=True,
                                       context={'tz': to_zone}),
                                      '%Y-%m-%d %H:%M:%S') + tm_delta



#    def _get_uom_id(self):
#        try:
#            proxy = self.pool.get('ir.model.data')
#            result = proxy.get_object_reference(self._cr, self._uid,
#              'product','product_uom_unit')
#            return result[1]
#        except Exception:
#            return False

    _name = 'hotel.reservation'
    _description = 'hotel folio1 room line'


    @api.depends('state', 'reservation_type')
    def _compute_color(self):
        now_str = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        for rec in self:
            now_date = datetime.strptime(now_str,
                                                  DEFAULT_SERVER_DATETIME_FORMAT)
            checkin_date = (datetime.strptime(
                                rec.checkin,
                                DEFAULT_SERVER_DATETIME_FORMAT))
            difference_checkin = relativedelta(now_date, checkin_date)
            checkout_date = (datetime.strptime(
                                rec.checkout,
                                DEFAULT_SERVER_DATETIME_FORMAT))
            difference_checkout = relativedelta(now_date, checkout_date)
            if rec.reservation_type == 'staff':
                rec.reserve_color = COLOR_TYPES.get('staff')
            elif rec.reservation_type == 'out':
                rec.reserve_color = COLOR_TYPES.get('dontsell')
            elif rec.state == 'draft':
                rec.reserve_color = COLOR_TYPES.get('pre-reservation')
            elif rec.state == 'confirm':
                rec.reserve_color = COLOR_TYPES.get('reservation')
            elif rec.state == 'checkin' and difference_checkout.days == 0:
                rec.reserve_color = COLOR_TYPES.get('checkout')
            else:
                rec.reserve_color = "#FFFFFF"

    reservation_no = fields.Char('Reservation No', size=64, readonly=True)
    adults = fields.Integer('Adults', size=64, readonly=True,
                            states={'draft': [('readonly', False)]},
                            help='List of adults there in guest list. ')
    children = fields.Integer('Children', size=64, readonly=True,
                              states={'draft': [('readonly', False)]},
                              help='Number of children there in guest list.')
    to_assign = fields.Boolean('To Assign')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),
                              ('booking', 'Booking'), ('done', 'Done'),
                              ('cancelled', 'Cancelled')],
                             'State', readonly=True,
                             default=lambda *a: 'draft')
    reservation_type = fields.Selection([
                                ('normal', 'Normal'),
                                ('staff', 'Staff'),
                                ('out', 'Out of Service')
                                ], 'Reservation Type', default=lambda *a: 'normal')
    out_service_description = fields.Text('Cause of out of service')
    reserve_color = fields.Char(compute='_compute_color',string='Color', store=True)
    order_line_id = fields.Many2one('sale.order.line', string='Order Line',
                                    required=True, delegate=True,
                                    ondelete='cascade')
    folio_id = fields.Many2one('hotel.folio', string='Folio',
                               ondelete='cascade')
    checkin = fields.Datetime('Check In', required=True,
                                   default=_get_checkin)
    checkout = fields.Datetime('Check Out', required=True,
                                    default=_get_checkout)
    room_type_id = fields.Many2one('hotel.room.type',string='Room Type')
    virtual_room_id = fields.Many2one('hotel.virtual.room',string='Channel Room Type')
    partner_id = fields.Many2one (related='folio_id.partner_id')
    reservation_lines = fields.One2many('hotel.reservation.line',
                                        'reservation_id',
                                        readonly=True,
                                        states={'draft': [('readonly', False)],
                                                'sent': [('readonly', False)]})
    cardex_ids = fields.One2many('cardex', 'reservation_id')
    cardex_count = fields.Integer('Cardex counter', compute='_compute_cardex_count')
    cardex_pending = fields.Boolean('Cardex Pending', compute='_compute_cardex_pending')
    cardex_pending_num = fields.Integer('Cardex Pending', compute='_compute_cardex_pending')
    service_line_ids = fields.One2many('hotel.service.line','ser_room_line')
    pricelist_id = fields.Many2one('product.pricelist',related='folio_id.pricelist_id',readonly="1")

    def _compute_cardex_count(self):
        self.cardex_count = len(self.cardex_ids)

    def _compute_cardex_pending(self):
        self.cardex_pending_num = self.adults + self.children - len(self.cardex_ids)
        if (self.adults + self.children - len(self.cardex_ids))<=0:
            self.cardex_pending = False
        else:
            self.cardex_pending = True

#    product_uom = fields.Many2one('product.uom',string='Unit of Measure',
#                                  required=True, default=_get_uom_id)

    @api.multi
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'

    @api.multi
    def action_reservation_checkout(self):
        for r in self:
            self.state = 'done'

    @api.model
    def create(self, vals, check=True):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        @return: new record set for hotel folio line.
        """
        if 'folio_id' in vals:
            folio = self.env["hotel.folio"].browse(vals['folio_id'])
            vals.update({'order_id': folio.order_id.id})
        record = super(HotelReservation, self).create(vals)
        if record.adults == 0:
            room = self.env['hotel.room'].search([('product_id','=',record.product_id.id)])
            record.adults = room.capacity
        return record

    #~ @api.multi
    #~ def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        sale_line_obj = self.env['sale.order.line']
        #~ fr_obj = self.env['folio.room.line']
        #~ for line in self:
            #~ if line.order_line_id:
                #~ sale_unlink_obj = (sale_line_obj.browse
                                   #~ ([line.order_line_id.id]))
                #~ for rec in sale_unlink_obj:
                    #~ room_obj = self.env['hotel.room'
                                        #~ ].search([('name', '=', rec.name)])
                    #~ if room_obj.id:
                        #~ folio_arg = [('folio_id', '=', line.folio_id.id),
                                     #~ ('room_id', '=', room_obj.id)]
                        #~ folio_room_line_myobj = fr_obj.search(folio_arg)
                        #~ if folio_room_line_myobj.id:
                            #~ folio_room_line_myobj.unlink()
                #~ sale_unlink_obj.unlink()
        #~ return super(HotelReservation, self).unlink()

    @api.multi
    def uos_change(self, product_uos, product_uos_qty=0, product_id=None):
        '''
        @param self: object pointer
        '''
        for folio in self:
            line = folio.order_line_id
            line.uos_change(product_uos, product_uos_qty=0,
                            product_id=None)
        return True

    @api.onchange('product_id')
    def product_id_change(self):
        if self.product_id and self.folio_id.partner_id:
            self.name = self.product_id.name
            self.product_uom = self.product_id.uom_id
            tax_obj = self.env['account.tax']
            prod = self.product_id
            self.price_unit = tax_obj._fix_tax_included_price(prod.price,
                                                              prod.taxes_id,
                                                              self.tax_id)

            #~ price_list_global = self.env['product.pricelist.item'].search([
            #~ ('pricelist_id', '=', self.folio_id.pricelist_id.id),
            #~ ('compute_price', '=', 'fixed'),
            #~ ('applied_on', '=', '3_global')
            #~ ], order='sequence ASC, id DESC', limit=1)
            #~ date_diff = abs((date_start-date_end).days)+1
            #~ for i in range(0, date_diff):
                #~ ndate = date_start + timedelta(days=i)
                #~ price_list = self.env['product.pricelist.item'].search([
                    #~ ('pricelist_id', '=', self.folio_id.pricelist_id.id),
                    #~ ('applied_on', '=', '2_product_category'),
                    #~ ('categ_id', '=', cat.id),
                    #~ ('date_start', '<=', ndate.replace(hour=0, minute=0, second=0).strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                    #~ ('date_end', '>=', ndate.replace(hour=23, minute=59, second=59).strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                    #~ ('compute_price', '=', 'fixed'),
                #~ ], order='sequence ASC, id DESC', limit=1)
                #~ price_day = self.product_id.lst_price



    @api.onchange('product_uom')
    def product_uom_change(self):
        if not self.product_uom:
            self.price_unit = 0.0
            return
        self.price_unit = self.product_id.lst_price
        if self.folio_id.partner_id:
            prod = self.product_id.with_context(
                lang=self.folio_id.partner_id.lang,
                partner=self.folio_id.partner_id.id,
                quantity=1,
                date_order=self.folio_id.date_order,
                pricelist=self.folio_id.pricelist_id.id,
                uom=self.product_uom.id
            )
            tax_obj = self.env['account.tax']
            self.price_unit = tax_obj._fix_tax_included_price(prod.price,
                                                              prod.taxes_id,
                                                              self.tax_id)

    @api.onchange('reservation_lines')
    def on_change_reservation_lines(self):
        self.price_unit = sum(self.reservation_lines.mapped('price'))

    @api.onchange('checkin', 'checkout', 'product_id')
    def on_change_checkin_checkout_product_id(self):
        _logger.info("PASA ONCHANGE 1")
        if not self.checkin:
            self.checkin = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if not self.checkout:
            self.checkout = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        _logger.info("PASA ONCHANGE 2")
        if self._context.get('regenerate', True):
            _logger.info("PASA ONCHANGE 3")
            # UTC -> Local
            tz = self._context.get('tz')
            chkin_dt = fields.Datetime.from_string(self.checkin).replace(tzinfo=pytz.utc)
            chkout_dt = fields.Datetime.from_string(self.checkout).replace(tzinfo=pytz.utc)
            if tz:
                chkin_dt = chkin_dt.astimezone(pytz.timezone(tz))
                chkout_dt = chkout_dt.astimezone(pytz.timezone(tz))
            days_diff = abs((chkout_dt - chkin_dt).days)
            _logger.info("PASA AA")
            _logger.info(days_diff)
            res = self.prepare_reservation_lines(chkin_dt, days_diff)
            self.reservation_lines = res['commands']
            self.price_unit = res['total_price']
            _logger.info("PASA ONCHANGE 4")
            _logger.info(res['commands'])
        _logger.info("PASA ONCHANGE 5")

    @api.model
    def prepare_reservation_lines(self, datefrom, days):
        total_price = 0.0
        cmds = [(5, False, False)]
        for i in range(0, days):
            ndate = datefrom + timedelta(days=i)
            ndate_str = ndate.strftime(DEFAULT_SERVER_DATE_FORMAT)
            product_id = self.product_id.with_context(
                lang=self.order_partner_id.lang,
                partner=self.order_partner_id.id,
                quantity=1,
                date_order=ndate_str,
                pricelist=self.order_id.pricelist_id.id)
            line_price = product_id.list_price
            cmds.append((0, False, {
                'date': ndate_str,
                'price': line_price
            }))
            total_price += line_price
        if self.adults == 0 and self.product_id:
            room = self.env['hotel.room'].search([('product_id', '=', product_id.id)])
            self.adults = room.capacity
        return {'total_price': total_price, 'commands': cmds}

    @api.onchange('checkin', 'checkout','room_type_id','virtual_room_id')
    def on_change_checkout(self):
        '''
        When you change checkin or checkout it will checked it
        and update the qty of hotel folio line
        -----------------------------------------------------------------
        @param self: object pointer
        '''
        if not self.checkin:
            self.checkin = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if not self.checkout:
            self.checkout = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        checkin = self.checkin
        checkout = self.checkout
        if checkin and checkout:
            server_dt = DEFAULT_SERVER_DATETIME_FORMAT
            chkin_dt = datetime.strptime(checkin, server_dt)
            chkout_dt = datetime.strptime(checkout, server_dt)
            dur = chkout_dt - chkin_dt
            sec_dur = dur.seconds
            if (not dur.days and not sec_dur) or (dur.days and not sec_dur):
                myduration = dur.days
            else:
                myduration = dur.days + 1
        self.product_uom_qty = myduration
        res = self.env['hotel.reservation'].search([
            ('state','!=','cancelled'),
            ('checkin','>=',self.folio_id.date_order),
            ('checkout','>=',self.checkin),
            ('checkin','<=',self.checkout)
            ])
        res_in = res.search([
            ('checkin','>=',self.checkin),
            ('checkin','<=',self.checkout)])
        res_out = res.search([
            ('checkout','>=',self.checkin),
            ('checkout','<=',self.checkout)])
        res_full = res.search([
            ('checkin','<',self.checkin),
            ('checkout','>',self.checkout)])
        occupied = res_in | res_out | res_full
        occupied &= res
        rooms_occupied= occupied.mapped('product_id.id')
        domain_rooms = [('isroom','=',True),('id', 'not in', rooms_occupied)]
        if self.room_type_id:
            domain_rooms.append(('categ_id.id', '=', self.room_type_id.cat_id.id))
        if self.virtual_room_id:
            room_categories = self.virtual_room_id.room_type_ids.mapped('cat_id.id')
            link_virtual_rooms = self.virtual_room_id.room_ids | self.env['hotel.room'].search([('categ_id.id','in',room_categories)])
            room_ids = link_virtual_rooms.mapped('product_id.id')
            domain_rooms.append(('id','in',room_ids))
        return {'domain': {'product_id': domain_rooms}}


    @api.multi
    def button_confirm(self):
        '''
        @param self: object pointer
        '''
        for folio in self:
            line = folio.order_line_id
            line.button_confirm()
        return True

    @api.multi
    def button_done(self):
        '''
        @param self: object pointer
        '''
        lines = [folio_line.order_line_id for folio_line in self]
        lines.button_done()
        self.write({'state': 'done'})
        for folio_line in self:
            workflow.trg_write(self._uid, 'sale.order',
                               folio_line.order_line_id.order_id.id,
                               self._cr)
        return True

    @api.one
    def copy_data(self, default=None):
        '''
        @param self: object pointer
        @param default: dict of default values to be set
        '''
        line_id = self.order_line_id.id
        sale_line_obj = self.env['sale.order.line'].browse(line_id)
        return sale_line_obj.copy_data(default=default)

    @api.constrains('checkin', 'checkout')
    def check_dates(self):
        """
        1.-When date_order is less then checkin date or
        Checkout date should be greater than the checkin date.
        3.-Check the reservation dates are not occuped
        """
        if self.checkin >= self.checkout:
                raise ValidationError(_('Room line Check In Date Should be \
                less than the Check Out Date!'))
        #if self.folio_id.date_order and self.checkin:
            #if self.checkin <= self.folio_id.date_order:
                #raise ValidationError(_('Room line check in date should be \
                #greater than the current date.'))
        res = self.env['hotel.reservation'].search([
        ('id','!=',self.id),
        ('checkin','>=',self.folio_id.date_order),
        ('product_id','=',self.product_id.id)
        ])
        res_in = self.env['hotel.reservation'].search([
            ('checkin','>=',self.checkin),
            ('checkin','<=',self.checkout)])
        res_out = self.env['hotel.reservation'].search([
            ('checkout','>=',self.checkin),
            ('checkout','<=',self.checkout)])
        occupied = res_in | res_out
        occupied &= res
        occupied_name = ','.join(str(x.id) for x in occupied)
        if occupied:
           warning_msg = 'You tried to confirm \
               reservation with room those already reserved in this \
               reservation period: %s' % occupied_name
           raise ValidationError(warning_msg)


