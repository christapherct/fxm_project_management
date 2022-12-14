import datetime
import sys

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class ProjectAssignment(models.Model):
    _name = "project.management"
    _inherit = ['mail.thread']
    _description = "Project"

    account_management_id = fields.One2many('account.management', 'project_management_id', tracking=True)
    account_inherit_ids = fields.One2many('account.move', 'project_management_id', tracking=True)
    job_management_ids = fields.One2many('job.management', 'project_management_id', tracking=True)
    task_management_ids = fields.One2many('task.management', 'project_management_id', tracking=True)
    name = fields.Char(string="Project Name", tracking=True, required=True)
    client_id = fields.Many2one('client.management', string="Client Name", tracking=True, required=True)
    checklist = fields.Text(related="client_id.checklist", readonly=False, string="Checklist", tracking=True)
    proposal = fields.Boolean(related="client_id.proposal", readonly=False, string="Add Proposal", tracking=True)
    job_ids = fields.One2many(related="client_id.job_management_ids", readonly=False, string="Jobs", tracking=True)
    project_type = fields.Selection(selection=[('one_time', 'One Time'), ('monthly', 'Monthly'), ('emergency', 'Emergency')],
                                    string="Project Type", tracking=True)
    start_date = fields.Date(default=fields.Date.today, readonly=False, string="Start Date", tracking=True)
    end_date = fields.Date(string="End Date", tracking=True)
    project_category = fields.Selection(
        selection=[('standard', 'Standard'), ('creative', 'Creative')], string="Project Category", track_visibility=True)
    description = fields.Text(string="Description", tracking=True)

    stage_id = fields.Selection([('new', 'New'), ('assigned', 'Assigned'), ('submission', 'Submission'), ('completed', 'Completed')],
                                string="Stage", default='new', tracking=True)
    note = fields.Text(string="Notes")
    state = fields.Selection(related="account_management_id.state", tracking=True)
    show_jobs = fields.Boolean(string="Show All Jobs", tracking=True, default=True)
    monthly_proposal = fields.Boolean(string="Monthly Proposal", compute="check_monthly_proposal", tracking=True)
    # lead_id = fields.Many2one('lead.management')
    pending_job_count = fields.Integer(compute="get_pending_job_count", tracking=True)
    completed_job_count = fields.Integer(compute="get_completed_job_count", tracking=True)
    stage = fields.Selection(selection=[('new', 'New'), ('in_progress', 'In Progress'), ('done', 'Done'), ('invoiced', 'Invoiced'),
                                        ('cancel', 'Cancelled')], tracking=True, default='new')

    @api.model
    def create(self, vals):
        vals['stage'] = 'in_progress'
        return super(ProjectAssignment, self).create(vals)

    def set_kanban_color(self):
        for record in self:
            record.kanbancolor = 0
            if record.stage_id == 'new':
                record.kanbancolor = 1
            elif record.stage_id == 'assigned':
                record.kanbancolor = 2
            elif record.stage_id == 'submission':
                record.kanbancolor = 3
            elif record.stage_id == 'completed':
                record.kanbancolor = 4
            else:
                record.kanbancolor = 5
            record.kanbancolor = record.kanbancolor
            print(record.kanbancolor)

    def get_task_num(self):
        for partner in self:
            partner.task_count = self.env['task.management'].search_count([self.task_management_ids])

    @api.onchange('start_date', 'end_date')
    def date_difference(self):
        if self.start_date and self.end_date:
            d1 = datetime.strptime(str(self.start_date), '%Y-%m-%d')
            d2 = datetime.strptime(str(self.end_date), '%Y-%m-%d')
            if d2 < d1:
                raise ValidationError('End date should not before than start date.')

    def action_complete_project(self):
        data = []
        for rec in self.job_management_ids:
            data.append(rec.stage)
        if 'new' in data or 'processing' in data or 'hold' in data:
            raise ValidationError("Please ensure that all of the Jobs were completed")
        elif not self.job_management_ids:
            raise ValidationError("There is no Jobs found")
        else:
            self.stage = 'done'

    def action_check_invoice(self):
        return {
            'res_model': 'account.management',
            'type': 'ir.actions.act_window',
            'context': {'default_project_management_id': self.id,
                        },
            'view_mode': 'form',
            'view_id': self.env.ref("fxm_project_management.account_task_view").id,
        }

    def action_check_ins_invoice(self):
        return {
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'context': {'default_project_management_id': self.id,
                        },
            'view_mode': 'form',
            'view_id': self.env.ref("account.view_move_form").id,
        }

    def completed_jobs(self):
        staging_tree = {
            'name': _('Completed Jobs'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'job.management',
            'type': 'ir.actions.act_window',
            'context': {'default_project_management_id': self.id},
            'target': 'current',
            'domain': [('project_management_id', '=', self.id), ('stage', '=', 'completed')]
        }
        return staging_tree

    def pending_jobs(self):
        staging_tree = {
            'name': _('Completed Jobs'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'job.management',
            'type': 'ir.actions.act_window',
            'context': {'default_project_management_id': self.id},
            'target': 'current',
            'domain': [('project_management_id', '=', self.id), ('stage', '!=', 'completed')]
        }
        return staging_tree

    def get_pending_job_count(self):
        self.pending_job_count = self.env['job.management'].search_count([('project_management_id', '=', self.id), ('stage', '!=', 'completed')])

    def get_completed_job_count(self):
        self.completed_job_count = self.env['job.management'].search_count([('project_management_id', '=', self.id), ('stage', '=', 'completed')])

    def job_creation(self):
        return {
            'res_model': 'job.management',
            'type': 'ir.actions.act_window',
            'context': {'default_project_management_id': self.id,
                        },
            'view_mode': 'form',
            'view_id': self.env.ref("fxm_project_management.job_task_view").id,
            }

    @api.depends('start_date')
    def _check_project_date(self):
        for rec in self.job_management_ids:
            print("Hiii")
            if self.start_date:
                print("hloo")
                rec.created_date = self.start_date
    # rec.start_date = self.created_date

    @api.onchange('proposal', 'project_type')
    def check_monthly_proposal(self):
        for rec in self.client_id:
            if rec.proposal == True:
                if self.project_type == 'monthly':
                    self.monthly_proposal = True
                else:
                    self.monthly_proposal = False
            else:
                self.monthly_proposal = False









