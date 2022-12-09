import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _


class TimesheeetAssignment(models.Model):
    _name = "timesheet.management"
    _inherit = ['mail.thread']
    _description = "Tasks"

    task_management_id = fields.Many2one('task.management', tracking=True)
    designer_management_id = fields.Many2one('designer.management', tracking=True)
    employee_management_id = fields.Many2one('hr.employee', tracking=True)
    name = fields.Char(string="Name", tracking=True)
    user_id = fields.Many2one(related="task_management_id.employee_id", readonly=False, tracking=True)
    project_management_id = fields.Many2one(related="task_management_id.project_management_id", tracking=True, required=True)
    date_from = fields.Datetime(string="Date From", tracking=True, readonly=True)
    date_to = fields.Datetime(string="Date To", tracking=True, readonly=True)
    notes = fields.Text(string="Notes", tracking=True)
    time_spent = fields.Char(string="Time spent(Hrs)", tracking=True, compute="date_difference", store=True)

    def current_start_time(self):
        self.date_from = fields.Datetime.now()
        return

    def current_end_time(self):
        self.date_to = fields.Datetime.now()
        return

    @api.depends('date_from', 'date_to')
    def date_difference(self):
        if self.date_from and self.date_to:
            start_dt = fields.Datetime.from_string(self.date_from)
            finish_dt = fields.Datetime.from_string(self.date_to)
            difference = finish_dt - start_dt
            d4 = (difference.seconds/3600)
            d5 = (difference.days*24)
            self.time_spent = d4+d5
