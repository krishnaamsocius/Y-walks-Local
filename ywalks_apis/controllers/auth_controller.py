# -*- encoding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied


class MobileAuthController(http.Controller):

    @http.route('/api/mobile/login',type='json',auth='none',methods=['POST'],csrf=False)
    def mobile_login(self, **kwargs):
        """
        Login API
        """

        login = kwargs.get('login')
        password = kwargs.get('password')

        if not login or not password:
            return {
                "success": False,
                "message": "Login and password are required"
            }

        try:
            uid = request.session.authenticate(
                request.session.db,
                login,
                password
            )
        except AccessDenied:
            return {
                "success": False,
                "message": "Invalid login or password"
            }

        if not uid:
            return {
                "success": False,
                "message": "Authentication failed"
            }

        user = request.env['res.users'].sudo().browse(uid)

        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "uid": uid,
                "session_id": request.session.sid,
                "name": user.name,
                "login": user.login,
                "email": user.email,
                "company_id": user.company_id.id,
                "company_name": user.company_id.name,
            }
        }
