# -*- encoding: utf-8 -*-
{
    "name": "Y-Walks Base",
    "version": "19.0.0.0.0",
    "author": "Socius",
    "license": 'AGPL-3',
    "description": """Base module for Y-Walks mobile application""",
    "depends": [
        'base','base_setup',
    ],
    "data": [
        "security/security.xml",
        "data/cron.xml",
        "security/ir.model.access.csv",
        "views/res_users.xml",
        "views/ywalks_activity_day.xml",
        "views/ywalks_user_streak.xml",
        "views/ywalks_wallet.xml",
        "views/ywalks_reward_rule.xml",
        "views/ywalks_group.xml",
        "views/ywalks_leaderboard_entry.xml",
        "views/ywalks_league.xml",
        # "views/ywalks_analytics.xml",
        "views/ywalks_menu.xml",
        "views/res_config_settings.xml",
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
}
