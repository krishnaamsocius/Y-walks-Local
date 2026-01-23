# -*- encoding: utf-8 -*-
from odoo import models, fields, api


class YWalksActivityDay(models.Model):
    _name = "ywalks.activity.day"
    _description = "Y-Walks Daily Activity"
    _order = "activity_date desc"
    _rec_name = "display_name"

    display_name = fields.Char(compute="_compute_display_name", store=True)
    user_id = fields.Many2one("res.users",required=True,ondelete="cascade",index=True)
    activity_date = fields.Date(required=True,index=True)
    steps = fields.Integer(default=0)
    distance_km = fields.Float(default=0.0)
    calories = fields.Float(default=0.0)
    is_active_day = fields.Boolean(string="Active Day", compute="_compute_is_active",store=True)

    _unique_user_date = models.Constraint(
        "unique(user_id, activity_date)",
        "Only one activity record per user per day."
    )

    @api.depends("user_id", "activity_date")
    def _compute_display_name(self):
        for rec in self:
            if rec.user_id and rec.activity_date:
                rec.display_name = f"{rec.user_id.name} - {rec.activity_date}"
            else:
                rec.display_name = "Y-Walks Activity"

    @api.depends("steps")
    def _compute_is_active(self):
        daily_goal = int(self.env["ir.config_parameter"].sudo().get_param("ywalks.daily_step_goal", 5000))
        for rec in self:
            rec.is_active_day = rec.steps >= daily_goal

    def _update_user_streak(self):
        for rec in self:
            if not rec.is_active_day:
                streak = self.env["ywalks.user.streak"].sudo().search(
                    [("user_id", "=", rec.user_id.id)], limit=1
                )
                if streak:
                    streak.current_streak = 0
                continue

            streak = self.env["ywalks.user.streak"].sudo().search([("user_id", "=", rec.user_id.id)],limit=1)

            if not streak:
                streak = self.env["ywalks.user.streak"].sudo().create({
                    "user_id": rec.user_id.id,
                    "current_streak": 1,
                    "longest_streak": 1,
                    "last_active_date": rec.activity_date,
                })
                continue

            if streak.last_active_date:
                delta = (rec.activity_date - streak.last_active_date).days
            else:
                delta = None

            if delta == 1:
                streak.current_streak += 1
            elif delta == 0:
                return
            else:
                streak.current_streak = 1


            streak.last_active_date = rec.activity_date
            streak.longest_streak = max(streak.longest_streak,streak.current_streak)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._update_user_streak()
        return records

    def write(self, vals):
        res = super().write(vals)
        if "steps" in vals:
            self._update_user_streak()
        return res
