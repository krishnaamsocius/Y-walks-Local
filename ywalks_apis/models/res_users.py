# -*- coding: utf-8 -*-
from odoo import models, api, exceptions, _, fields
from passlib.context import CryptContext
from datetime import timedelta
import random
from twilio.rest import Client

from odoo.exceptions import UserError
from odoo.http import request
from twilio.base.exceptions import TwilioException

pwd_context = CryptContext(schemes=["pbkdf2_sha512"], deprecated="auto")


class ResUsers(models.Model):
    _inherit = 'res.users'

    is_mobile_user = fields.Boolean("Mobile User", default=False)

    @api.model
    def login_with_email(self, login, password):

        if not login or not password:
            raise exceptions.UserError(_("Login and password are required."))

        # Find User
        user = self.sudo().search([('login', '=', login)], limit=1)

        if not user:
            raise exceptions.AccessDenied(_("User does not exist."))

        # Get hashed password and verify
        self.env.cr.execute("SELECT password FROM res_users WHERE id = %s", (user.id,))
        result = self.env.cr.fetchone()
        stored_hash = result[0] if result else None

        # Verify password
        if not stored_hash or not pwd_context.verify(password, stored_hash):
            raise exceptions.AccessDenied(_("Invalid login credentials."))

        # Return user info
        return {
            'id': user.id,
            'login': user.login,
            'email': user.email,
            'name': user.name,
            'partner_id': user.partner_id.id,
        }

    @api.model
    def signup_with_email(self, name, email, password, confirm_password):
        """ Normal Signup API """

        # Required field validation
        if not name or not email or not password or not confirm_password:
            raise exceptions.UserError(
                _("Name, Email, Password and Confirm Password are required."))

        # Password match validation
        if password != confirm_password:
            raise exceptions.UserError(
                _("Password and Confirm Password do not match.") )

        # Email already exists check
        existing_user = self.sudo().search(
            [('login', '=', email)], limit=1 )
        if existing_user:
            raise exceptions.UserError(
                _("An account already exists with this email."))

        # Create user
        user = self.sudo().create({
            'name': name,
            'login': email,
            'email': email,
            'password': password,
            'is_mobile_user': True,
        })

        return {
            "success": True,
            "message": "Signup successful",
            "user": {
                "id": user.id,
                "name": user.name,
                "login": user.login,
                "email": user.email,
                "partner_id": user.partner_id.id,
            }
        }

    @api.model
    def signup_with_mobile(self, name, phone, password, confirm_password, country_code="+91"):
        """ Signup using mobile number with password """

        # Validate required inputs
        if not name or not phone or not password or not confirm_password:
            raise UserError(_("Name, Mobile Number, Password and Confirm Password are required."))

        # Password match check
        if password != confirm_password:
            raise UserError(_("Password and Confirm Password do not match."))

        # Normalize phone number
        country_code = country_code.strip()
        if not country_code.startswith('+'):
            country_code = f"+{country_code}"

        login = f"{country_code}{phone}"

        # Check if user already exists
        existing_user = self.sudo().search(
            [('login', '=', login)], limit=1
        )
        if existing_user:
            raise UserError(_("An account already exists with this mobile number."))

        # Create user
        user = self.sudo().create({
            'name': name,
            'login': login,  # mobile used as login
            'phone': login,
            'password': password,
            'is_mobile_user': True,
        })

        # Ensure partner phone is set
        if user.partner_id:
            user.partner_id.sudo().write({
                'phone': login,
                'email': False,
            })

        return {
            "success": True,
            "message": "Signup successful.",
            "user": {
                "id": user.id,
                "name": user.name,
                "login": user.login,
                "phone": user.phone,
                "partner_id": user.partner_id.id,
            }
        }

    @api.model
    def send_otp_to_phone(self, phone_number, country_code="+91"):
        try:
            if not phone_number:
                return {'success': False, 'message': 'Phone number is required.'}

            # Normalize inputs
            phone_number = str(phone_number).strip()
            country_code = str(country_code).strip()

            if not country_code.startswith('+'):
                country_code = f"+{country_code}"

            if not phone_number.startswith('+'):
                phone_number = f"{country_code}{phone_number}"

            # Check user
            user = self.sudo().search([('login', '=', phone_number)], limit=1)
            if not user:
                return {'success': False, 'message': 'No user found with this login.'}

            # Remove previous OTPs
            self.env['mobile.otp'].sudo().search([
                ('phone', '=', phone_number),
                ('purpose', '=', 'login'),
            ]).unlink()

            # #  Check active OTP
            # active_otp = self.env['mobile.otp'].sudo().search([
            #     ('phone', '=', phone_number),
            #     ('purpose', '=', 'login'),
            #     ('expiry', '>', fields.Datetime.now())
            # ], limit=1)
            #
            # if active_otp:
            #     return {
            #         'success': False,
            #         'message': 'OTP already sent. Please wait before requesting again.'
            #     }

            # Generate OTP
            otp = str(random.randint(1000, 9999))

            # Twilio config
            twilio_account = self.env['twilio.account'].sudo().search([], limit=1)
            if not twilio_account:
                return {'success': False, 'message': 'Twilio account is not configured.'}

            if not all([
                twilio_account.account_sid,
                twilio_account.auth_token,
                twilio_account.from_number
            ]):
                return {'success': False, 'message': 'Twilio credentials are incomplete.'}

            # Send SMS
            try:
                client = Client(
                    twilio_account.account_sid,
                    twilio_account.auth_token
                )
                client.messages.create(
                    body=f"Your OTP is {otp}. Valid for 2 minutes.",
                    from_=twilio_account.from_number,
                    to=phone_number
                )
            except Exception as sms_error:
                return {
                    'success': False,
                    'message': f"Failed to send OTP SMS. {str(sms_error)}"
                }

            #  Save OTP after SMS success
            self.env['mobile.otp'].sudo().create({
                'phone': phone_number,
                'otp': otp,
                'expiry': fields.Datetime.now() + timedelta(minutes=2),
                'purpose': 'login',
            })

            return {
                'success': True,
                'message': 'OTP sent successfully',
                'OTP': otp

            }

        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }

    @api.model
    def verify_otp(self, phone_number, otp, country_code="+91"):
        if not phone_number or not otp:
            return {'success': False, 'message': 'Phone number and OTP are required.'}

        # Normalize country code
        country_code = str(country_code).strip()
        if not country_code.startswith('+'):
            country_code = f"+{country_code}"

        # Normalize phone
        phone_number = str(phone_number).strip()
        if not phone_number.startswith('+'):
            phone_number = f"{country_code}{phone_number}"

        # Fetch OTP
        otp_rec = self.env['mobile.otp'].sudo().search([
            ('phone', '=', phone_number),
            ('purpose', '=', 'login')
        ], limit=1)

        if not otp_rec:
            return {'success': False, 'message': 'OTP not found. Please request again.'}

        # Compare OTP explicitly
        if otp_rec.otp != str(otp):
            return {'success': False, 'message': 'Invalid OTP.'}

        # Expiry check
        if otp_rec.is_expired():
            otp_rec.unlink()
            return {'success': False, 'message': 'OTP has expired.'}

        otp_rec.unlink()

        # Fetch user by LOGIN
        user = self.sudo().search([('login', '=', phone_number)], limit=1)
        if not user:
            return {'success': False, 'message': 'User not found.'}

        # Generate token only if missing
        if not user.api_rest_key:
            user.generate_api_rest_key()

        return {
            'success': True,
            'message': 'OTP verified successfully',
            'api_key': user.api_rest_key,
            'user': {
                'id': user.id,
                'name': user.name,
                'phone': user.login,
            }
        }

    # @api.model
    # def send_otp_to_phone(self, phone_number, country_code="+91"):
    #     try:
    #         # Validate phone
    #         if not phone_number:
    #             return {
    #                 'success': False,
    #                 'message': 'Phone number is required.'
    #             }
    #
    #         # Existing user check
    #         user = self.sudo().search([('phone', '=', phone_number)], limit=1)
    #         if not user:
    #             return {
    #                 'success': False,
    #                 'message': 'No user found with this phone number.'
    #             }
    #
    #         country_code = str(country_code).strip()
    #         if not country_code.startswith('+'):
    #             country_code = f"+{country_code}"
    #
    #         # Generate OTP
    #         otp = str(random.randint(1000, 9999))
    #
    #         # Remove previous OTPs
    #         self.env['mobile.otp'].sudo().search([
    #             ('phone', '=', phone_number),
    #             ('purpose', '=', 'login')
    #         ]).unlink()
    #
    #         # Store OTP (2 minutes validity)
    #         self.env['mobile.otp'].sudo().create({
    #             'phone': phone_number,
    #             'otp': otp,
    #             'expiry': fields.Datetime.now() + timedelta(minutes=2),
    #             'purpose': 'login',
    #         })
    #
    #         # Twilio credentials
    #         twilio_account = self.env['twilio.account'].sudo().search([], limit=1)
    #
    #         if not twilio_account:
    #             return {
    #                 'success': False,
    #                 'message': 'Twilio account is not configured.'
    #             }
    #
    #         account_sid = twilio_account.account_sid
    #         auth_token = twilio_account.auth_token
    #         from_number = twilio_account.from_number
    #
    #         if not all([account_sid, auth_token, from_number]):
    #             return {
    #                 'success': False,
    #                 'message': 'Twilio credentials are not configured.'
    #             }
    #
    #         # Send OTP via Twilio
    #         client = Client(account_sid, auth_token)
    #         client.messages.create(
    #             body=f"Your OTP is {otp}. Valid for 2 minutes.",
    #             from_=from_number,
    #             to=f"{country_code}{phone_number}"
    #         )
    #
    #         return {
    #             'success': True,
    #             'message': 'OTP sent successfully',
    #             'OTP': otp,
    #         }
    #
    #     except TwilioException:
    #         return {
    #             'success': False,
    #             'message': 'Failed to send OTP. Please try again.'
    #         }
    #
    #     except Exception as e:
    #         return {
    #             'success': False,
    #             'message': str(e)
    #         }

    # @api.model
    # def verify_otp(self, phone_number, otp):
    #     """
    #     Verify OTP for mobile login
    #     """
    #     # Validate inputs
    #     if not phone_number or not otp:
    #         return {
    #             'success': False,
    #             'message': 'Phone number and OTP are required.'
    #         }
    #
    #     # Find OTP record
    #     otp_rec = self.env['mobile.otp'].sudo().search([
    #         ('phone', '=', phone_number),
    #         ('otp', '=', otp),
    #         ('purpose', '=', 'login')
    #     ], limit=1)
    #
    #     if not otp_rec:
    #         return {
    #             'success': False,
    #             'message': 'Invalid OTP.'
    #         }
    #
    #     # Check expiry
    #     if otp_rec.is_expired():
    #         otp_rec.unlink()
    #         return {
    #             'success': False,
    #             'message': 'OTP has expired.'
    #         }
    #
    #     # OTP is valid → delete it
    #     otp_rec.unlink()
    #
    #     # Fetch user
    #     user = self.sudo().search([('phone', '=', phone_number)], limit=1)
    #     if not user:
    #         return {
    #             'success': False,
    #             'message': 'User not found.'
    #         }
    #
    #     # request.session.uid = user.id
    #     # request.session.login = user.login
    #     user.generate_api_rest_key()
    #
    #     return {
    #         'success': True,
    #         'message': 'OTP verified successfully',
    #         'api_key': user.api_rest_key,
    #         'user': {
    #             'id': user.id,
    #             'name': user.name,
    #             'phone': user.phone,
    #         }
    #     }

    @api.model
    def request_password_reset(self, email):
        """
        Generate reset token and send reset email
        """
        user = self.sudo().search([('login', '=', email)], limit=1)

        if not user:
            return True

        user.sudo().action_reset_password()

        return True

    @api.model
    def api_update_password(self, token, new_password, confirm_password):
        if not new_password or not confirm_password:
            raise UserError("Password and Confirm Password are required")

        if new_password != confirm_password:
            raise UserError("Passwords do not match")

        partner = self.env['res.partner'].sudo()._get_partner_from_token(token)
        if not partner:
            raise UserError("Invalid or expired reset token")

        user = partner.user_ids.filtered(lambda u: u.active)[:1]
        if not user:
            raise UserError("No active user found")

        user.sudo().write({'password': new_password})

        return {
            "success": True,
            "message": "Password updated successfully"
        }





