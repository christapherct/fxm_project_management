# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.osv import expression


class EmployeeInheritted(models.Model):
    _inherit = "hr.employee"

    job_id = fields.Many2one('hr.job', string="Job Position")
    department_id = fields.Many2one('hr.department', string="Department")
    timesheet_management_ids = fields.One2many('timesheet.management', 'employee_management_id')
    designation = fields.Selection(
        [('designer', 'Designer'), ('copywriter', 'Copywriter'), ('crm', 'CRM'), ('tl', 'Team Lead'),
         ('digital_marketing', 'Digital Marketing Executive'), ('accountant', 'Accountant'), ('pm', 'Project Manager')], string="Designation", tracking=True)

    def action_check_timesheet(self):
        staging_tree = {
            'name': _('Timesheet'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'timesheet.management',
            'type': 'ir.actions.act_window',
            'context': {'default_employee_management_id': self.id},
            'target': 'current',
            'domain': [('employee_management_id', '=', self.id)]
        }
        return staging_tree


