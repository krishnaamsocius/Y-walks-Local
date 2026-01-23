# -*- encoding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ywalks_daily_step_goal = fields.Integer(
        string="Daily Step Goal",
        default=5000,
        config_parameter="ywalks.daily_step_goal",
    )

    ywalks_streak_min_days = fields.Integer(
        string="Minimum Days for Streak Reward",
        default=7,
        config_parameter="ywalks.streak_min_days",
    )

    ywalks_enable_rewards = fields.Boolean(
        string="Enable Rewards System",
        default=True,
        config_parameter="ywalks.enable_rewards",
    )
