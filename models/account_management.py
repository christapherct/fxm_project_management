from odoo import api, fields, models, _
from odoo.addons.base.models.report_paperformat import PAPER_SIZES
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class AccountManagement(models.Model):
    _name = "account.management"
    _inherit = ['mail.thread']
    _description = "Account Task"

    target_management_id = fields.Many2one('target.management', tracking=True)
    name = fields.Char(readonly=True, copy=False, tracking=True,  required=True, default='New')
    project_management_id = fields.Many2one('project.management', string="Project Name", required=True, tracking=True)
    add_client_id = fields.Many2one(related="project_management_id.client_id", string="Client Name", tracking=True)
    project_type = fields.Selection(related="project_management_id.project_type", string="Project Type", tracking=True)
    start_date = fields.Date(related="project_management_id.start_date", string="Start Date", tracking=True)
    end_date = fields.Date(related="project_management_id.end_date", string="End Date", tracking=True)
    project_category = fields.Selection(related="project_management_id.project_category", string="Project Category", tracking=True)
    job_management_ids = fields.One2many(related="project_management_id.job_management_ids", readonly=False, tracking=True)
    note = fields.Text(string="Notes", tracking=True)
    invoice_today = fields.Date(string="Order Date", default=datetime.today(), tracking=True)
    amount_untaxed = fields.Float(string="Price", store=True, readonly=True, compute='_amount_all', tracking=True)
    amount_total = fields.Float(string="Total Amount", store=True, readonly=True, compute="_amount_all", tracking=True)
    amount_tax = fields.Float(string="Tax(%)", store=True, readonly=True, compute='_amount_all', tracking=True)
    client_management_id = fields.Many2one('client.management', tracking=True)
    state = fields.Selection([('draft', 'Draft'), ('processing', 'Processing'), ('done', 'Posted')], string="State", default='draft', tracking=True)
    _sql_constraints = [('project_management_id', 'unique (project_management_id)', 'This one is already selected.')]

    def action_invoice_sent(self):
        return

    def action_register_payment(self):
        self.state = 'done'

    @api.depends('job_management_ids.price_subtotal')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.job_management_ids:
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
            vals['state'] = 'processing'
            if vals['state'] == 'processing':
                record = self.env['project.management'].search([('account_management_id', '=', self.id)])
                record.write({'stage': 'invoiced'})
        result = super(AccountManagement, self).create(vals)
        if not result.job_management_ids:
            raise ValidationError('Please ensure that there is jobs are included!')
        return result







