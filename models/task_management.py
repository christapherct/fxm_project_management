import datetime
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class TaskAssignment(models.Model):
    _name = "task.management"
    _inherit = ['mail.thread']
    _description = "Tasks"

    tl_rejection_ids = fields.One2many('tl.rejection', 'task_management_id')
    crm_rejection_ids = fields.One2many('crm.rejection', 'task_management_id')
    client_rejection_ids = fields.One2many('client.rejection', 'task_management_id')

    task_event_ids = fields.One2many('task.event', 'task_management_id')
    job_management_id = fields.Many2one('job.management', string="Job", required=True)
    account_management_id = fields.Many2one('account.management')
    timesheet_management_ids = fields.One2many('timesheet.management', 'task_management_id')
    name = fields.Char(string="Name", required=True)
    project_management_id = fields.Many2one(related="job_management_id.project_management_id", string="Project", required=True)
    user_id = fields.Many2one('designer.management')
    partner_id = fields.Many2one('designer.management', string="Assigned to")
    employee_id = fields.Many2one('hr.employee', string="Assigned to")
    assigned_date = fields.Datetime(string="Assigned Date", readonly=True)
    updated_date = fields.Datetime(string="Last Updated Date", readonly=True)
    submitted_date = fields.Datetime(string="Submitted Date", readonly=True)
    deadline = fields.Date(string="Deadline")
    client_id = fields.Many2one(related="job_management_id.client_management_id", readonly=False, string="Client", track_visibility=True, required=True)
    checklist = fields.Text(related="job_management_id.checklist", readonly=False, string="Checklist", track_visibility=True)
    description = fields.Text(string="Description")
    kanban_state = fields.Selection([('normal', 'In Progress'), ('blocked', 'Blocked'), ('done', 'Ready for next stage')],
                                    string='Kanban State', required=True, default='normal', tracking=True)
    stage_id = fields.Selection([('new', 'New'), ('assigned', 'Assigned'), ('submission', 'Submission'), ('tl_approval', 'TL Approval'),
                                 ('crm_approval', 'CRM Approval'), ('client_approval', 'Client Approval'), ('completed', 'Completed')],
                                string="Stage", default='new', tracking=True)
    total_days = fields.Integer(store=True, readonly=True)
    file = fields.Binary("Submit Attachment")
    file_name = fields.Char("File Name")
    file_link = fields.Char(string="File Link")
    priority = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
                                string="Priority", tracking=True)
    task_priority = fields.Selection([('expired', 'Expired'), ('today', 'Today'), ('tomorrow', 'Tomorrow'), ('week', 'In this Week'), ('x_later', 'Later')],
                                     string='Task Priority', tracking=True)
    d4 = fields.Date(default=fields.Date.today, readonly=True)
    tl_reason = fields.Text(string="Reason for Rejection By Team Leader", tracking=True)
    crm_reason = fields.Text(string="Reason for Rejection By CRM", tracking=True)
    client_reason = fields.Text(string="Reason for Rejection By Client")

    @api.onchange('partner_id')
    def change_date_field(self):
        if self.partner_id:
            self.assigned_date = fields.Datetime.now()
            self.stage_id = 'assigned'
        else:
            self.assigned_date = None
            self.stage_id = 'new'

    @api.onchange('deadline', 'total_days')
    def calculate_date(self):
        if self.deadline:
            d11 = fields.Date.today()
            d1 = datetime.strptime(str(d11), '%Y-%m-%d')
            d2 = datetime.strptime(str(self.deadline), '%Y-%m-%d')
            d3 = d2 - d1
            self.total_days = str(d3.days)

    def open_tl_reject_wizard(self):
        return {
            'res_model': 'tl.rejection',
            'type': 'ir.actions.act_window',
            'context': {'default_task_management_id': self.id,
                        },
            'view_mode': 'form',
            'target': 'new',

            }

    def open_crm_reject_wizard(self):
        return {
            'res_model': 'crm.rejection',
            'type': 'ir.actions.act_window',
            'context': {'default_task_management_id': self.id,
                        },
            'view_mode': 'form',
            'target': 'new',

            }

    def open_client_reject_wizard(self):
        return {
            'res_model': 'client.rejection',
            'type': 'ir.actions.act_window',
            'context': {'default_task_management_id': self.id,
                        },
            'view_mode': 'form',
            'target': 'new',

            }

    @api.onchange('timesheet_management_ids')
    def change_updation_time(self):
        self.updated_date = fields.Datetime.now()

    def approve_attachment(self):
        if self.file_link and self.partner_id:
            for rec in self:
                rec.stage_id = 'submission'
                rec.submitted_date = fields.Datetime.now()
        else:
            raise ValidationError("Make sure that the Assigned user and File link fields are not be empty")

    def check_telegram(self):
        return {
            'type': 'ir.actions.act_url',
            'url': 'https://telegram.me/+sGNT-_FMPUBiZmNl'
        }

    def approve_tl_stage_stage(self):
        self.stage_id = 'tl_approval'

    def approve_crm_approval(self):
        self.stage_id = 'crm_approval'

    def approve_client_approval(self):
        self.stage_id = 'client_approval'

    def completed_jobs(self):
        self.stage_id = 'completed'

    def write(self, vals):
        if any(stage_id == 'completed' for stage_id in set(self.mapped('stage_id'))):
            raise UserError(_("No edits in Completed task"))
        else:
            return super().write(vals)

    @api.onchange('total_days')
    def date_difference(self):
        if self.total_days:
            if self.total_days > 1 and self.total_days < 7:
                self.task_priority = 'week'
            elif self.total_days > 7:
                self.task_priority = 'x_later'
            elif self.total_days == 1:
                self.task_priority ='tomorrow'
            elif self.total_days == 0:
                self.task_priority = 'today'
            else:
                self.task_priority = 'expired'
                abs(self.total_days)





