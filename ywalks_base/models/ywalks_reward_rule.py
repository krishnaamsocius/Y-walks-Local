# -*- encoding: utf-8 -*-
from odoo import models, fields


class YWalksRewardRule(models.Model):
    _name = "ywalks.reward.rule"
    _description = "Y-Walks Reward Rule"

    name = fields.Char(required=True)

    reward_type = fields.Selection(
        [
            ("activity", "Activity Milestone"),
            ("ad", "Advertisement"),
        ],
        required=True
    )

    min_steps = fields.Integer(
        string="Minimum Steps",
        help="Applicable for activity rewards only"
    )

    streak_days = fields.Integer(
        string="Minimum Streak Days",
        help="Optional streak condition"
    )

    coins = fields.Integer(required=True)

    active = fields.Boolean(default=True)
