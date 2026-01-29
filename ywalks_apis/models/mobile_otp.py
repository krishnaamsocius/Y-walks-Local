# -*- coding: utf-8 -*-
from odoo import models, fields


class MobileOTP(models.Model):
    _name = 'mobile.otp'
    _description = 'Mobile OTP'
    _rec_name = 'phone'
    _order = 'create_date desc'

    phone = fields.Char(string="Phone Number", required=True, index=True)
    otp = fields.Char(string="OTP", required=True)
    expiry = fields.Datetime(string="Expiry Time", required=True)

    purpose = fields.Selection([
        ('login', 'Login'),
        ('signup', 'Signup'),
        ('reset', 'Reset Password'),
    ], default='login', required=True)

    attempts = fields.Integer(string="Attempts", default=0)

    def is_expired(self):
        """Check whether OTP is expired"""
        self.ensure_one()
        return fields.Datetime.now() > self.expiry
