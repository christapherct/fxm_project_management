from multiprocessing import context
from statistics import mode

from odoo import api, fields, models, _, exceptions
from datetime import datetime

from odoo.exceptions import ValidationError


class LeadManagement(models.Model):
    _name = "lead.management"
    _inherit = ['mail.thread']
    _description = "Leads"

    lost_reason_ids = fields.One2many('lead.lost.reason', 'lead_management_id')
    # project_management_ids = fields.One2many('project.management', 'lead_id')
    customer_management_ids = fields.One2many('client.management', 'lead_mgmt_id')
    name = fields.Char(string="Lead Name", required=True, tracking=True)
    customer_name = fields.Char(string="Customer Name", tracking=True)
    customer_phone = fields.Char(string="Customer Phone", tracking=True)
    customer_address = fields.Text(string="Address", tracking=True)
    company_category = fields.Char(string="Company Category", tracking=True)
    customer_id = fields.Many2one('client.management', string="Customer Name", tracking=True)
    probability = fields.Float(string="Probability", tracking=True)
    project_type = fields.Selection(
        selection=[('one-time', 'One Time'), ('monthly', 'Monthly'), ('emergency', 'Emergency')],
        string="Project Type", tracking=True)
    note = fields.Text(string="Notes", tracking=True)
    assigned_date = fields.Datetime(string="Assigned Date", default=fields.Date.today, readonly=True, tracking=True)
    ended_date = fields.Datetime(string="End Date", readonly=True, tracking=True)
    stage = fields.Selection(
        selection=[('new', 'New'), ('hold', 'Hold'), ('client', 'Converted to Client'), ('lost', 'Lost')], tracking=True, default='new')
    lost_reason = fields.Text(string="Lost Reason", readonly=True, tracking=True)
    next_followup = fields.Date(string="Next Follow-up Date", readonly=False, tracking=True)
    diff_date = fields.Integer(tracking=True)

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

    def check_client(self):
        staging_tree = {
            'name': _('Clients'),
            'view_type': 'tree',
            'view_mode': 'tree',
            'view_id': self.env.ref("fxm_project_management.action_client_mgmt").id,
            'res_model': 'client.management',

            'type': 'ir.actions.act_window',
            'context': {'default_name': self.customer_name,
                        },
            'target': 'current',
            'domain': [('name', '=', self.customer_name)]
        }
        return staging_tree

    def action_view_client(self):
        action = self.env['ir.actions.act_window']._for_xml_id('fxm_project_management.action_client_mgmt')
        if self.name:
            action['domain'] = [('name', '=', self.customer_name)]
            # action['views'] = [(False, 'form')]
            action['res_id'] = self.customer_id.id
        return action

    def action_view_customer(self):
        action = self.env["ir.actions.actions"]._for_xml_id("fxm_project_management.action_client_mgmt")
        action['views'] = [(False, 'form')]
        action['res_id'] = self.customer_management_ids.id
        return action

    def restore_lead(self):
        for rec in self.lost_reason_ids:
            self.stage = rec.stage_det

    def client_creation(self):
        self.probability = 100
        self.stage = 'client'
        return {
            'res_model': 'client.management',
            'type': 'ir.actions.act_window',
            'context': {'default_name': self.customer_name,
                        'default_address': self.customer_address,
                        'default_contact': self.customer_phone,
                        'default_lead_mgmt_id': self.id,
                        },
            'view_mode': 'form',
            'view_id': self.env.ref("fxm_project_management.client_form_view").id,
        }


class LostLeadManagement(models.TransientModel):
    _name = 'lead.lost.reason'
    _inherit = ['mail.thread']

    reason = fields.Text(string="Reason", track_visibility=True, required=True)
    lead_management_id = fields.Many2one('lead.management')
    stage_det = fields.Selection(
        selection=[('new', 'New'), ('hold', 'Hold'), ('client', 'Converted to Client'), ('lost', 'Lost')], track_visibility=True,
        default='new')

    def lead_lost_reason(self):
        for rec in self.lead_management_id:
            self.stage_det = rec.stage
            rec.probability = 0
            rec.stage = 'lost'
            rec.lost_reason = self.reason
            rec.ended_date = datetime.today()



