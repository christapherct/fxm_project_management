import time

import babel
from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _, tools
from odoo.exceptions import UserError, ValidationError
from odoo import exceptions
from odoo.exceptions import Warning, UserError
from datetime import datetime

from odoo.tools import date_utils


class JobTargetAchieved(models.Model):
    _name = "job.target"
    _inherit = ['mail.thread']
    _description = "Target"

    name = fields.Char(string='Reference', required=True)
    job_management_ids = fields.One2many('job.management', 'job_target_id')
    target = fields.Float(string="Target Amount", required=True)
    achieved_total = fields.Float(string='Total Achieved', store=True)
    date_type = fields.Selection(selection=[('daily', 'Today'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
                                string="Time Period", track_visibility=True, default='daily', required=True)
    today_date = fields.Date(string="Created Date", default=datetime.now(), readonly=True)

    notes = fields.Text(string="Notes")

    @api.onchange('date_type')
    def datetype_search(self):
        achieved_amount = 0
        if self.job_management_ids:
            for i in self.job_management_ids:
                achieved_amount = achieved_amount + i.amount_untaxed
                self.achieved_total = achieved_amount
                print(self.achieved_total)

        for order in self:
            if order.date_type == 'daily':
                today_date = datetime.now()
                order.job_management_ids = order.env['job.management'].search([('created_date', '=', today_date)]).ids
                achieved_amount = 0
                if self.job_management_ids:
                    for i in self.job_management_ids:
                        achieved_amount = achieved_amount + i.amount_untaxed
                        self.achieved_total = achieved_amount
                        print(self.achieved_total)
            elif order.date_type == 'weekly':
                date_week = date_utils.subtract(order.today_date, weeks=1)
                order.job_management_ids = order.env['job.management'].search([('created_date', '>=', date_week)]).ids
                achieved_amount = 0
                if self.job_management_ids:
                    for i in self.job_management_ids:
                        achieved_amount = achieved_amount + i.amount_untaxed
                        self.achieved_total = achieved_amount
                        print(self.achieved_total)
            elif order.date_type == 'monthly':
                date_month = date_utils.subtract(order.today_date, months=1)
                order.job_management_ids = order.env['job.management'].search([('created_date', '>=', date_month)]).ids
                achieved_amount = 0
                if self.job_management_ids:
                    for i in self.job_management_ids:
                        achieved_amount = achieved_amount + i.amount_untaxed
                        self.achieved_total = achieved_amount
                        print(self.achieved_total)





