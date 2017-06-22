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
from openerp.tools import misc, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import models, fields, api, _
from openerp import workflow
from decimal import Decimal
import datetime
import urllib2
import time


class ReservationRestriction(models.Model):
    _name ='reservation.restriction'

    name = fields.Char('name')
    room_ids = fields.Many2many('hotel.room',string='Rooms')
    room_type_ids = fields.Many2many('hotel.virtual.room',string='Room Types')
    init_date = fields.Date('From')
    end_date = fields.Date("To")
    min_stay = fields.Integer("Min. Nights")
    min_stay_arrival = fields.Integer("Min. Nights")
    max_stay = fields.Integer("Min. Nights")
    no_ota = fields.Boolean('No Ota')
    close = fields.Selection([
        ('open', 'Open'),
        ('close', 'Close'),
        ('close_arrival', 'Close Arrival')],
        'Close')
    no_checkout= fields.Boolean('No Checkout')
    mo = fields.Boolean('Mon')
    tu = fields.Boolean('Tue')
    we = fields.Boolean('Wed')
    th = fields.Boolean('Thu')
    fr = fields.Boolean('Fri')
    sa = fields.Boolean('Sat')
    su = fields.Boolean('Sun')







