# -*- encoding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class YWalksGroup(models.Model):
    _name = "ywalks.group"
    _description = "Y-Walks Group"

    name = fields.Char(required=True)
    description = fields.Text()
    owner_id = fields.Many2one("res.users", required=True, ondelete="cascade", string="Group Owner")
    is_public = fields.Boolean(default=True, help="Public groups can be joined by any user")
    member_ids = fields.One2many("ywalks.group.member", "group_id", string="Members")
    member_count = fields.Integer(compute="_compute_member_count", store=True)
    league_id = fields.Many2one(
        "ywalks.league",
        ondelete="cascade",
        string="League"
    )

    @api.depends("member_ids")
    def _compute_member_count(self):
        for group in self:
            group.member_count = len(group.member_ids)

    @api.model
    def create(self, vals):
        group = super().create(vals)
        # Auto-add owner as member
        self.env["ywalks.group.member"].sudo().create({
            "group_id": group.id,
            "user_id": group.owner_id.id,
        })
        return group

    def join_group(self, user):
        """
        Temporary backend join method
        """
        self.ensure_one()

        Member = self.env["ywalks.group.member"].sudo()

        # Check if already a member
        existing = Member.search([
            ("group_id", "=", self.id),
            ("user_id", "=", user.id)
        ], limit=1)

        if existing:
            raise ValidationError("User is already a member of this group.")

        Member.create({
            "group_id": self.id,
            "user_id": user.id
        })

        return True

    def leave_group(self, user):
        """
        Temporary backend leave method
        """
        self.ensure_one()

        Member = self.env["ywalks.group.member"].sudo()

        membership = Member.search([
            ("group_id", "=", self.id),
            ("user_id", "=", user.id)
        ], limit=1)

        if not membership:
            raise ValidationError("User is not a member of this group.")

        membership.unlink()
        return True

