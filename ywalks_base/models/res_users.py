# -*- encoding: utf-8 -*-
from odoo import models, fields, api



class ResUsers(models.Model):
    _inherit = "res.users"

    # Mobile-related
    phone_number = fields.Char(string="Mobile Number")

    def create_wallet_if_not_exists(self):
        for user in self:
            if not self.env["ywalks.wallet"].sudo().search(
                [("user_id", "=", user.id)], limit=1
            ):
                self.env["ywalks.wallet"].sudo().create({
                    "user_id": user.id
                })

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        users.create_wallet_if_not_exists()
        return users

