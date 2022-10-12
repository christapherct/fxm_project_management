from odoo import api, fields, models, _
from datetime import datetime


class LeadManagement(models.Model):
    _name = "lead.management"
    _inherit = ['mail.thread']
    _description = "Leads"

    lost_reason_ids = fields.One2many('lead.lost.reason', 'lead_management_id')
    project_management_ids = fields.One2many('project.management', 'lead_id')
    name = fields.Char(string="Lead Name", required=True, track_visibility=True)
    customer_id = fields.Many2one('client.management', string="Customer Name", required=True, track_visibility=True)
    checklist = fields.Text(related="customer_id.checklist", readonly=False, string="Checklist", track_visibility=True)
    proposal = fields.Boolean(related="customer_id.proposal", readonly=False, string="Add Proposal",
                              track_visibility=True)
    customer_address = fields.Text(related="customer_id.address", string="Customer Address", track_visibility=True, readonly=False)
    customer_phone = fields.Char(related="customer_id.contact", string="Customer Phone", track_visibility=True, readonly=False)
    customer_mail = fields.Char(related="customer_id.contact", string="Customer Email", track_visibility=True, readonly=False)
    customer_website = fields.Char(related="customer_id.website", string="Website", track_visibility=True, readonly=False)
    probability = fields.Float(string="Probability", track_visibility=True)
    project_type = fields.Selection(
        selection=[('one-time', 'One Time'), ('monthly', 'Monthly'), ('emergency', 'Emergency')],
        string="Project Type", track_visibility=True)
    note = fields.Text(string="Notes")
    assigned_date = fields.Datetime(string="Assigned Date", default=fields.Date.today, readonly=True)
    ended_date = fields.Datetime(string="End Date", readonly=True)
    stage = fields.Selection(
        selection=[('new', 'New'), ('hold', 'Hold'), ('project', 'Project'), ('lost', 'Lost')], track_visibility=True, default='new')
    lost_reason = fields.Text(string="Lost Reason", readonly=True)
    project_count = fields.Integer(compute="check_project_count")
    next_followup = fields.Date(string="Next Follow-up Date", readonly=False)
    diff_date = fields.Integer()

    def action_lost_lead(self):
            return {
                'res_model': 'lead.lost.reason',
                'type': 'ir.actions.act_window',
                'context': {'default_lead_management_id': self.id},
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
            }

    def action_lead_hold(self):
        self.stage = 'hold'

    def project_creation(self):
        self.probability = 100
        self.stage = 'project'
        return {
            'res_model': 'project.management',
            'type': 'ir.actions.act_window',
            'context': {'default_client_id': self.customer_id.id,
                        'default_lead_id': self.id,
                        'default_project_type': self.project_type
                        },
            'view_mode': 'form',
            'view_id': self.env.ref("fxm_project_management.project_management_view").id,
            }

    def check_projects(self):
        staging_tree = {
            'name': _('Projects'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'project.management',
            'type': 'ir.actions.act_window',
            'context': {'default_lead_id': self.id,
                        },
            'domain': [('lead_id', '=', self.id)],
            'target': 'current',
        }
        return staging_tree

    def check_project_count(self):
        self.project_count = self.env['project.management'].search_count([('lead_id', '=', self.id)])

    def restore_lead(self):
        for rec in self.lost_reason_ids:
            self.stage = rec.stage_det
    #
    # @api.depends('next_followup')
    # @api.onchange('next_followup')
    # def create_notification(self):
    #     if self.diff_date:
    #         today = fields.date.today()
    #         print(today, "tod")
    #
    #         for rec in self:
    #             d1 = datetime.strptime(str(today), '%Y-%m-%d')
    #             d2 = datetime.strptime(str(rec.next_followup), '%Y-%m-%d')
    #             print(d2, "nx")
    #             d3 = d2-d1
    #             rec.diff_date = str(d3.days)
    #             print(rec.diff_date)
    #             if rec.diff_date < 3 and rec.diff_date >=0:
    #                 return {
    #                     'type': 'ir.actions.client',
    #                     'tag': 'display_notification',
    #                     'params': {
    #                         'title': '_(Warning)',
    #                         'message': 'Followup date is here',
    #                         'sticky': True
    #
    #                     }
    #                 }
    #             elif rec.diff_date <0 :
    #                 print("Exceeded")
    #             else:
    #                 return
    #     else:
    #         return


class LostLeadManagement(models.TransientModel):
    _name = 'lead.lost.reason'
    _inherit = ['mail.thread']

    reason = fields.Text(string="Reason", track_visibility=True, required=True)
    lead_management_id = fields.Many2one('lead.management')
    stage_det = fields.Selection(
        selection=[('new', 'New'), ('hold', 'Hold'), ('project', 'Project'), ('lost', 'Lost')], track_visibility=True,
        default='new')

    def lead_lost_reason(self):
        for rec in self.lead_management_id:
            self.stage_det = rec.stage
            print(self.stage_det)
            rec.probability = 0
            rec.stage = 'lost'
            rec.lost_reason = self.reason
            rec.ended_date = datetime.today()

