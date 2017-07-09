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
from openerp import models, fields


class ReservationRestrictionItem(models.Model):
    _name = 'reservation.restriction.item'

    restriction_id = fields.Many2one('reservation.restriction', 'Restriction Plan', ondelete='cascade', select=True)
    virtual_room_id = fields.Many2one('hotel.virtual.room', 'Virtual Room')
    date_start = fields.Date('From')
    date_end = fields.Date("To")
    applied_on = fields.Selection([
        ('1_global', 'Global'),
        ('0_virtual_room', 'Virtual Room')], string="Apply On", required=True,
        help='Pricelist Item applicable on selected option')

    min_stay = fields.Integer("Min. Stay")
    min_stay_arrival = fields.Integer("Min. Stay Arrival")
    max_stay = fields.Integer("Max. Stay")
    closed = fields.Boolean('Closed')
    closed_departure = fields.Boolean('Closed Departure')
    closed_arrival = fields.Boolean('Closed Arrival')
