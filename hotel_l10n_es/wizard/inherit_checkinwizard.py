# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import UserError
from openerp.tools.translate import _
import logging
_logger=logging.getLogger(__name__)


class Wizard(models.TransientModel):
    _inherit = 'checkin.wizard'

    def default_enter_date(self):
        if 'reservation_id' in self.env.context:
            reservation = self.env['hotel.reservation'].search([('id','=',self.env.context['reservation_id'])])
            return reservation.checkin
        if 'enter_date' in self.env.context:
            return self.env.context['enter_date']
        return False

    def default_exit_date(self):
        if 'reservation_id' in self.env.context:
            reservation = self.env['hotel.reservation'].search([('id','=',self.env.context['reservation_id'])])
            return reservation.checkout
        if 'exit_date' in self.env.context:
            return self.env.context['exit_date']
        return False

    def default_reservation_id(self):
        if 'reservation_id' in self.env.context:
            reservation = self.env['hotel.reservation'].search([('id','=',self.env.context['reservation_id'])])
            return reservation
        if 'reserva_id' in self.env.context:
            return self.env.context['reserva_id']
        return False

    def default_partner_id(self):
        if 'reservation_id' in self.env.context:
            reservation = self.env['hotel.reservation'].search([('id','=',self.env.context['reservation_id'])])
            return reservation.partner_id
        if 'partner_id' in self.env.context:
            return self.env.context['partner_id']
        return False

    def default_cardex_ids(self):
        if 'reservation_id' in self.env.context:
            reservation = self.env['hotel.reservation'].search([('id','=',self.env.context['reservation_id'])])
            return reservation.cardex_ids

    def default_count_cardex(self):
        if 'reservation_id' in self.env.context:
            reservation = self.env['hotel.reservation'].search([('id','=',self.env.context['reservation_id'])])
            return reservation.cardex_count

    def default_pending_cardex(self):
        if 'reservation_id' in self.env.context:
            reservation = self.env['hotel.reservation'].search([('id','=',self.env.context['reservation_id'])])
            return reservation.adults + reservation.children - reservation.cardex_count

    def comp_checkin_list_visible(self):
        if 'partner_id' in self.env.context:
            self.list_checkin_cardex = False
        return

    def comp_checkin_edit(self):
        if 'edit_cardex' in self.env.context:
            return True
        return False

    documenttype_cardex = fields.Selection([
        ('D', 'DNI'),
        ('P', 'Pasaporte'),
        ('C', 'Permiso de Conducir'),
        ('I', 'Carta o Doc. de Identidad'),
        ('N', 'Permiso Residencia Español'),
        ('X', 'Permiso Residencia Europeo')],
        help='blabla',
        required=True,
        string='Doc. type',
        related='partner_id.documenttype')
    poldocument_cardex = fields.Char('Doc. number', required=True, related='partner_id.poldocument')
    polexpedition_cardex = fields.Date('Expedition date', required=True, related='partner_id.polexpedition')
    birthdate_date_cardex = fields.Date("Birthdate", required=True, related='partner_id.birthdate_date')
    gender_cardex = fields.Selection([('male', 'Male'),
                               ('female', 'Female')],
                                required=True, related='partner_id.gender')
    firstname_cardex = fields.Char('Firstname', required=True, related='partner_id.firstname')
    lastname_cardex = fields.Char('Lastname', required=True, related='partner_id.lastname')
    mobile_cardex = fields.Char('Mobile', related='partner_id.mobile', store=True)
    code_ine_cardex = fields.Many2one('code_ine',
            help='Country or province of origin. Used for INE statistics.',
            required=True,
            related='partner_id.code_ine')
    category_id_cardex = fields.Many2many('res.partner.category', 'id', related='partner_id.category_id', required=True)


