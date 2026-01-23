# -*- encoding: utf-8 -*-
from odoo import models, fields, api


class YWalksWallet(models.Model):
    _name = "ywalks.wallet"
    _description = "Y-Walks Wallet"
    _rec_name = "user_id"

    user_id = fields.Many2one(
        "res.users",
        required=True,
        ondelete="cascade",
        unique=True
    )

    balance = fields.Integer(
        compute="_compute_balance",
        store=True
    )

    transaction_ids = fields.One2many(
        "ywalks.wallet.transaction",
        "wallet_id"
    )

    @api.depends("transaction_ids.amount", "transaction_ids.state")
    def _compute_balance(self):
        for wallet in self:
            wallet.balance = sum(
                wallet.transaction_ids
                .filtered(lambda t: t.state == "done")
                .mapped("amount")
            )

    def credit_wallet(self, amount, transaction_type, reference):
        self.ensure_one()

        self.env["ywalks.wallet.transaction"].sudo().create({
            "wallet_id": self.id,
            "amount": amount,
            "transaction_type": transaction_type,
            "reference": reference,
            "state": "done",
        })

