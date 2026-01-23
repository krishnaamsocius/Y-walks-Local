# -*- encoding: utf-8 -*-
from odoo import models, fields


class YWalksGroupMember(models.Model):
    _name = "ywalks.group.member"
    _description = "Y-Walks Group Member"
    _rec_name = "user_id"

    group_id = fields.Many2one("ywalks.group", required=True, ondelete="cascade")
    user_id = fields.Many2one("res.users", required=True, ondelete="cascade")
    joined_on = fields.Datetime(default=fields.Datetime.now)

    _unique_group_user = models.Constraint(
        "unique(group_id, user_id)",
        "User is already a member of this group."
    )
