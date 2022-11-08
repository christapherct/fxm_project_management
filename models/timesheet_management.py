import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _


class TimesheeetAssignment(models.Model):
    _name = "timesheet.management"
    _inherit = ['mail.thread']
    _description = "Tasks"

    task_management_id = fields.Many2one('task.management')
    designer_management_id = fields.Many2one('designer.management')
    employee_management_id = fields.Many2one('hr.employee')
    name = fields.Char(string="Name", track_visibility=True)
    user_id = fields.Many2one(related="task_management_id.partner_id", readonly=False, track_visibility=True)
    project_management_id = fields.Many2one(related="task_management_id.project_management_id", track_visibility=True, required=True)
    date_from = fields.Datetime(string="Date From", track_visibility=True, readonly=True)
    date_to = fields.Datetime(string="Date To", track_visibility=True, readonly=True)
    notes = fields.Text(string="Notes", track_visibility=True)
    time_spent = fields.Char(string="Time spent(Hrs)", track_visibility=True, compute="date_difference", store=True)

    def current_start_time(self):
        self.date_from = fields.Datetime.now()

    def current_end_time(self):
        self.date_to = fields.Datetime.now()

    # @api.onchange('date_to', 'date_from')
    # def date_difference(self):
    #     if self.date_to and self.date_from:
    #         # d1 = datetime.strptime(str(self.date_from), '%Y-%m-%d %H:%M:%S')
    #         d1 = datetime.strptime(self.date_from, '%Y-%m-%d %H:%M:%S')
    #         # d2 = datetime.strptime(str(self.date_to), '%Y-%m-%d %H:%M:%S')
    #         d2 = datetime.strptime(self.date_from, '%Y-%m-%d %H:%M:%S')
    #         # d4 = datetime.today()
    #         # d3 = (self.date_to - self.date_from)
    #         d3 = (d2 - d1)
    #         d4 = (d3.seconds / 3600)
    #         print("seconds", d4)
    #         d5 = (d3.days * 24)
    #         # print("days", d5)
    #         self.time_spent = d4 + d5

    @api.depends('date_from', 'date_to')
    def date_difference(self):
        if self.date_from and self.date_to:
            start_dt = fields.Datetime.from_string(self.date_from)
            finish_dt = fields.Datetime.from_string(self.date_to)
            difference = finish_dt - start_dt
            d4 = (difference.seconds/3600)
            d5 = (difference.days*24)
            self.time_spent = d4+d5
