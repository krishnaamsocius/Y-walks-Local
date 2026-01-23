# -*- encoding: utf-8 -*-
from odoo import models, fields


class YWalksUserStreak(models.Model):
    _name = "ywalks.user.streak"
    _description = "Y-Walks User Streak"
    _rec_name = "user_id"

    user_id = fields.Many2one(
        "res.users",
        required=True,
        ondelete="cascade",
        unique=True
    )

    current_streak = fields.Integer(default=0)
    longest_streak = fields.Integer(default=0)

    last_active_date = fields.Date()
