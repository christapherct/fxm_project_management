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

    def check_project_count(self):
        for partner in self:
            partner.project_count = len(partner.project_management_ids)

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
        return {
            'res_model': 'project.management',
            'type': 'ir.actions.act_window',
            'context': {'default_client_id': self.customer_id.id,
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
            'context': {'lead_id': self.id,
                        },
            'target': 'current',
            'domain': [('lead_id', '=', self.id)]
        }
        return staging_tree


class LostLeadManagement(models.TransientModel):
    _name = 'lead.lost.reason'
    _inherit = ['mail.thread']

    reason = fields.Text(string="Reason", track_visibility=True, required=True)
    lead_management_id = fields.Many2one('lead.management')

    def lead_lost_reason(self):
        for rec in self.lead_management_id:
            rec.stage = 'lost'
            rec.lost_reason = self.reason
            rec.ended_date = datetime.today()
