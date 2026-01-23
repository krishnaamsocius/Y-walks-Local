# -*- coding: utf-8 -*-
{
    'name': 'Ywalks Twilio SMS Gateway',
    'version': '19.0.0.0.0',
    'summary': 'Facilitating individual and group SMS communication through '
               'the Twilio gateway.',
    'description': 'This module empowers seamless SMS communication via '
                   'Twilio',
    'author': 'SIGB',
    'depends': [],
    'data': [
            # 'data/ir_cron_data.xml',
            'security/ir.model.access.csv',
            'views/twilio_account_views.xml',
            'views/twilio_sms_group_views.xml',
            'views/twilio_sms_template_views.xml',
            'views/twilio_sms_views.xml',
            'wizard/sms_builder_views.xml'
    ],
    'external_dependencies': {
        'python': ['twilio'],
        },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
