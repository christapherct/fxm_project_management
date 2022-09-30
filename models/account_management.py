from odoo import api, fields, models, _
from odoo.addons.base.models.report_paperformat import PAPER_SIZES
from odoo.exceptions import ValidationError
from datetime import datetime


class AccountManagement(models.Model):
    _name = "account.management"
    _inherit = ['mail.thread']
    _description = "Account Task"

    target_management_id = fields.Many2one('target.management')
    name = fields.Char(readonly=True, copy=False, track_visibility=True,  required=True, default='New')
    project_management_id = fields.Many2one('project.management', string="Project Name", required=True)
    add_client_id = fields.Many2one(related="project_management_id.client_id", string="Client Name", track_visibility=True)
    project_type = fields.Selection(related="project_management_id.project_type", string="Project Type", track_visibility=True)
    start_date = fields.Date(related="project_management_id.start_date", string="Start Date", track_visibility=True)
    end_date = fields.Date(related="project_management_id.end_date", string="End Date", track_visibility=True)
    project_category = fields.Selection(related="project_management_id.project_category", string="Project Category")
    job_management_ids = fields.One2many(related="project_management_id.job_management_ids", readonly=False)
    note = fields.Text()
    invoice_today = fields.Date(string="Order Date", default=datetime.today())
    amount_untaxed = fields.Float(string="Price", store=True, readonly=True, compute='_amount_all',)
    amount_total = fields.Float(string="Total Amount", store=True, readonly=True, compute="_amount_all")
    amount_tax = fields.Float(string="Tax(%)", store=True, readonly=True, compute='_amount_all',)
    client_management_id = fields.Many2one('client.management')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Sale Order')], string="Stage", default='draft', tracking=True)
    _sql_constraints = [('project_management_id', 'unique (project_management_id)', 'This one is already selected.')]

    @api.depends('job_management_ids.price_subtotal')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            # a = self.amount_tax
            for line in order.job_management_ids:
                # line._compute_amount()
                amount_untaxed += line.amount_untaxed
                a = line.price_tax
                b = a /100
                amount_tax = b * amount_untaxed
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('account.management') or 'New'
            vals['state'] = 'done'
        result = super(AccountManagement, self).create(vals)

        return result






