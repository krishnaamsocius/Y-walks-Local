# -*- coding: utf-8 -*-
from odoo import fields, models, _


class ResPartner(models.Model):
    """Inheriting res partner for including Twilio fields and functions"""
    _inherit = 'res.partner'

    mobile = fields.Char(string="Mobile")

    twilio_contact_id = fields.Many2one('twilio.sms.group',
                                        string='Twilio ID',
                                        help='Twilio Connection ID')
