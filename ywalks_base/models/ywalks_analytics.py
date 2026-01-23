# -*- encoding: utf-8 -*-
from odoo import models, fields, api
from datetime import date, timedelta


class YWalksAnalytics(models.Model):
    _name = "ywalks.analytics"
    _description = "Y-Walks Analytics Dashboard"

    date_from = fields.Date(default=lambda self: date.today() - timedelta(days=30))
    date_to = fields.Date(default=date.today)

    active_users = fields.Integer(compute="_compute_metrics")
    total_steps = fields.Integer(compute="_compute_metrics")
    total_rewards = fields.Integer(compute="_compute_metrics")
    active_groups = fields.Integer(compute="_compute_metrics")

    def _compute_metrics(self):
        for rec in self:
            activities = self.env["ywalks.activity.day"].search([
                ("activity_date", ">=", rec.date_from),
                ("activity_date", "<=", rec.date_to),
                ("is_active_day", "=", True),
            ])

            rec.active_users = len(activities.mapped("user_id"))
            rec.total_steps = sum(activities.mapped("steps"))

            rec.total_rewards = sum(
                self.env["ywalks.wallet.transaction"].search([
                    ("state", "=", "done"),
                    ("date", ">=", rec.date_from),
                    ("date", "<=", rec.date_to),
                ]).mapped("amount")
            )

            rec.active_groups = self.env["ywalks.group"].search_count([])
