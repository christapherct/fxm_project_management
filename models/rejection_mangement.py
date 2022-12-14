from odoo import api, fields, models, _


class TlRejection(models.TransientModel):
    _name = "tl.rejection"
    _inherit = ['mail.thread']

    task_management_id = fields.Many2one('task.management', string="Task Name", readonly=True)
    assigned_user = fields.Many2one(related="task_management_id.partner_id", readonly=True)
    project_management_id = fields.Many2one(related="task_management_id.project_management_id", readonly=True)
    job_management_id = fields.Many2one(related="task_management_id.job_management_id", readonly=True)
    reason = fields.Text(string="Reason", required=True)

    def rejection_reason(self):
        for rec in self.task_management_id:
            rec.stage_id = 'assigned'
            rec.tl_reason = self.reason


class CRMRejection(models.TransientModel):
    _name = 'crm.rejection'
    _inherit = ['mail.thread']

    task_management_id = fields.Many2one('task.management', string="Task Name", readonly=True, tracking=True)
    assigned_user = fields.Many2one(related="task_management_id.partner_id", readonly=True, tracking=True)
    project_management_id = fields.Many2one(related="task_management_id.project_management_id", readonly=True, tracking=True)
    job_management_id = fields.Many2one(related="task_management_id.job_management_id", readonly=True, tracking=True)
    reason = fields.Text(string="Reason", required=True, tracking=True)

    def rejection_reason(self):
        for rec in self.task_management_id:
            rec.stage_id = 'assigned'
            rec.crm_reason = self.reason


class ClientRejection(models.TransientModel):
    _name = 'client.rejection'
    _inherit = ['mail.thread']

    task_management_id = fields.Many2one('task.management', string="Task Name", readonly=True)
    assigned_user = fields.Many2one(related="task_management_id.partner_id", readonly=True)
    project_management_id = fields.Many2one(related="task_management_id.project_management_id", readonly=True)
    job_management_id = fields.Many2one(related="task_management_id.job_management_id", readonly=True)
    reason = fields.Text(string="Reason", required=True)

    def rejection_reason(self):
        for rec in self.task_management_id:
            rec.stage_id = 'assigned'
            rec.client_reason = self.reason