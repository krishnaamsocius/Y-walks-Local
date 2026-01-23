# -*- encoding: utf-8 -*-
from odoo import models, fields


class YWalksLeague(models.Model):
    _name = "ywalks.league"
    _description = "Y-Walks League"
    _order = "start_date desc"

    name = fields.Char(required=True)
    league_type = fields.Selection([("corporate", "Corporate"), ("city", "City"), ("challenge", "Challenge"), ],
                                   required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    visibility = fields.Selection([("public", "Public"), ("private", "Private"), ], default="public")
    max_participants = fields.Integer(help="Maximum allowed users across all groups")
    leaderboard_metric = fields.Selection([("steps", "Steps"), ("streak", "Streak"), ("coins", "Coins"), ],
                                          default="steps")
    active = fields.Boolean(default=True)
