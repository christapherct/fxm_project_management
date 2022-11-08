# -*- coding: utf-8 -*-
{
    'name': 'Project Management',
    'version': '1.1',
    'summary': 'Project Management Software',
    'sequence': -120,
    'description': """Project Management Software""""",
    'author': "Foxiom Leads Pvt Ltd",
    'category': 'Productivity',
    'website': 'https://www.foxiom.com',
    'license': 'LGPL-3',
    'depends': ['mail', 'crm', 'account', 'sale'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'reports/report.xml',
        'reports/report_task_view.xml',
        'wizard/crm_rejection_wizard.xml',
        'wizard/client_rejection_wizard.xml',
        'wizard/tl_rejection_wizard.xml',
        'wizard/lead_lost_reason_wizard.xml',
         'views/lead_management_view.xml',
         'views/client_management_views.xml',
         'views/project_management_view.xml',
         'views/task_management_views.xml',
         'views/task_event_view.xml',
         'views/designer_management_view.xml',
         'views/account_management_view.xml',
         'views/job_management_view.xml',
         'views/job_type_view.xml',
         'views/job_target_view.xml',
         'views/job_variant_view.xml',
         'views/target_management_view.xml',
         'views/account_inherit_view.xml',
         'views/employee_inherit_view.xml',





    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}

