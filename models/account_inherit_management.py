# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from odoo.osv import expression

SII_VAT = '60805000-0'


class AccountMoveMgmnt(models.Model):
    _inherit = "account.move"

    project_management_id = fields.Many2one('project.management', string="Project Name")
    client_management_id = fields.Many2one(related="project_management_id.client_id", string="Customer Name", track_visibility=True)
    test = fields.Char(string="Test")
    project_type = fields.Selection(related="project_management_id.project_type", string="Project Type",
                                    track_visibility=True)
    start_date = fields.Date(related="project_management_id.start_date", string="Start Date", track_visibility=True)
    end_date = fields.Date(related="project_management_id.end_date", string="End Date", track_visibility=True)
    project_category = fields.Selection(related="project_management_id.project_category", string="Project Category")
    job_management_ids = fields.One2many(related="project_management_id.job_management_ids", readonly=False)
    amount_untaxed = fields.Float(string="Price", store=True, readonly=True, compute='_amount_all', )
    amount_total = fields.Float(string="Total Amount", store=True, readonly=True, compute="_amount_all")
    amount_tax = fields.Float(string="Tax(%)", store=True, readonly=True, compute='_amount_all', )
    note = fields.Text()

    @api.depends('job_management_ids.price_subtotal')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.job_management_ids:
                amount_untaxed += line.amount_untaxed
                a = line.price_tax
                b = a / 100
                amount_tax = b * amount_untaxed
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    # def action_post(self):
    #     if not self.job_management_ids:
    #         raise ValidationError("There is no Jobs found")
