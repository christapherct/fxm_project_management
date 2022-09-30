from odoo import api, fields, models, _
from odoo.addons.base.models.report_paperformat import PAPER_SIZES
from odoo.exceptions import ValidationError
from datetime import datetime


class LeadManagement(models.Model):
    _name = "lead.management"
    _inherit = ['mail.thread']
    _description = "Leads"

    lost_reason_ids = fields.One2many('lead.lost.reason', 'lead_management_id')
    name = fields.Char(string="Lead Name", required=True, track_visibility=True)
    customer_id = fields.Many2one('client.management', string="Customer Name", required=True, track_visibility=True)
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
        selection=[('new', 'New'), ('postponed', 'Postponed'), ('project', 'Project'), ('lost', 'Lost')], track_visibility=True)
    lost_reason = fields.Text(string="Lost Reason", readonly=True)

    def action_lost_lead(self):
            return {
                'res_model': 'lead.lost.reason',
                'type': 'ir.actions.act_window',
                'context': {'default_lead_management_id': self.id},
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
            }


class LostLeadManagement(models.TransientModel):
    _name = 'lead.lost.reason'
    _inherit = ['mail.thread']

    reason = fields.Text(string="Reason", track_visibility=True, required=True)
    lead_management_id = fields.Many2one('lead.management')

    def lead_lost_reason(self):
        print("Haii")
        print(self.lead_management_id.id)
        print(self.id)
        for rec in self.lead_management_id:
            print("jjjjj")
            rec.stage = 'lost'
            rec.lost_reason = self.reason
            rec.ended_date = datetime.today()
