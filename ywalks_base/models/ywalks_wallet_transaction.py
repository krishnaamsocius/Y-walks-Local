# -*- encoding: utf-8 -*-
from odoo import models, fields


class YWalksWalletTransaction(models.Model):
    _name = "ywalks.wallet.transaction"
    _description = "Y-Walks Wallet Transaction"
    _order = "create_date desc"

    wallet_id = fields.Many2one(
        "ywalks.wallet",
        required=True,
        ondelete="cascade"
    )

    user_id = fields.Many2one(
        related="wallet_id.user_id",
        store=True
    )

    amount = fields.Integer(
        help="Positive = credit, Negative = debit"
    )

    transaction_type = fields.Selection(
        [
            ("activity", "Activity Reward"),
            ("ad", "Advertisement Reward"),
            ("purchase", "In-App Purchase"),
            ("rede reminder", "Redemption"),
            ("admin", "Admin Adjustment"),
        ],
        required=True
    )

    reference = fields.Char(
        help="Unique reference to prevent duplicate credits"
    )

    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("done", "Completed"),
            ("failed", "Failed"),
            ("cancelled", "Cancelled"),
        ],
        default="pending"
    )

    _unique_reference = models.Constraint(
        "unique(reference)",
        "Duplicate wallet transaction is not allowed."
    )
