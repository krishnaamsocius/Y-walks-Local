# -*- encoding: utf-8 -*-
from odoo import models, fields
from datetime import date, timedelta


class YWalksLeaderboardEntry(models.Model):
    _name = "ywalks.leaderboard.entry"
    _description = "Y-Walks Leaderboard Entry"
    _order = "rank asc"

    user_id = fields.Many2one("res.users", required=True)
    group_id = fields.Many2one("ywalks.group", string="Group")
    metric = fields.Selection([("steps", "Steps"), ("coins", "Coins"), ("streak", "Streak"), ], required=True)
    period = fields.Selection([("daily", "Daily"), ("weekly", "Weekly"), ("monthly", "Monthly"), ], required=True)
    period_start = fields.Date(required=True)
    value = fields.Integer(required=True)
    rank = fields.Integer(required=True)

    _unique_leaderboard = models.Constraint(
        "unique(user_id, metric, period, period_start, group_id)",
        "Duplicate leaderboard entry not allowed."
    )

    def compute_daily_steps(self, target_date=None):
        if not target_date:
            target_date = date.today() - timedelta(days=1)

        self.search([
            ("metric", "=", "steps"),
            ("period", "=", "daily"),
            ("period_start", "=", target_date),
        ]).unlink()

        activities = self.env["ywalks.activity.day"].search([
            ("activity_date", "=", target_date),
            ("is_active_day", "=", True)
        ])

        user_steps = {}
        for rec in activities:
            user_steps[rec.user_id.id] = user_steps.get(rec.user_id.id, 0) + rec.steps

        sorted_users = sorted(user_steps.items(), key=lambda x: x[1], reverse=True)

        rank = 1
        for user_id, steps in sorted_users:
            self.create({
                "user_id": user_id,
                "metric": "steps",
                "period": "daily",
                "period_start": target_date,
                "value": steps,
                "rank": rank,
            })
            rank += 1

    def compute_daily_coins(self, target_date=None):
        if not target_date:
            target_date = date.today() - timedelta(days=1)

        self.search([
            ("metric", "=", "coins"),
            ("period", "=", "daily"),
            ("period_start", "=", target_date),
        ]).unlink()

        wallets = self.env["ywalks.wallet"].search([])

        sorted_wallets = sorted(wallets, key=lambda w: w.balance, reverse=True)

        rank = 1
        for wallet in sorted_wallets:
            if wallet.balance <= 0:
                continue
            self.create({
                "user_id": wallet.user_id.id,
                "metric": "coins",
                "period": "daily",
                "period_start": target_date,
                "value": wallet.balance,
                "rank": rank,
            })
            rank += 1

    def compute_daily_streak(self):
        today = date.today()

        self.search([
            ("metric", "=", "streak"),
            ("period", "=", "daily"),
            ("period_start", "=", today),
        ]).unlink()

        streaks = self.env["ywalks.user.streak"].search([])

        sorted_streaks = sorted(
            streaks,
            key=lambda s: s.current_streak,
            reverse=True
        )

        rank = 1
        for rec in sorted_streaks:
            if rec.current_streak <= 0:
                continue
            self.create({
                "user_id": rec.user_id.id,
                "metric": "streak",
                "period": "daily",
                "period_start": today,
                "value": rec.current_streak,
                "rank": rank,
            })
            rank += 1
