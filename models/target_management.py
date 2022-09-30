#

import time
from datetime import datetime
import babel

from odoo import fields, models, api, _, tools
from odoo.exceptions import UserError, ValidationError
from odoo import exceptions
from odoo.exceptions import Warning, UserError


class TargetAssignment(models.Model):
    _name = "target.management"
    _inherit = ['mail.thread']
    _description = "Target"

    name = fields.Char(string='Reference', readonly=True)
    internal_note = fields.Text(string='Internal Note')
    target_ids = fields.One2many('daily.target.line', 'target_id', string='Target')
    target_amount = fields.Float(string='Total Target', readonly=False, required=True)
    achieved_total = fields.Float(string='Total Achieved')
    account_management_ids = fields.One2many('account.management', 'target_management_id')
    date = fields.Date(string='Date', default=lambda self: fields.Date.today())
    to_date = fields.Date(string='To Date', default=lambda self: fields.Date.today())
    client_management_id = fields.Many2one('client.management', string="Client")
    notes = fields.Text(string="Notes")

    @api.onchange('date', 'to_date', 'client_management_id')
    def target_records(self):
        if self.date and self.to_date:
            d1 = datetime.strptime(str(self.date), '%Y-%m-%d')
            d2 = datetime.strptime(str(self.to_date), '%Y-%m-%d')
            if d2 < d1:
                raise ValidationError('End date should not before than start date.')

            if self.client_management_id:
                self.account_management_ids = self.env['account.management'].search(
                                [('invoice_today', '>=', self.date), ('invoice_today', '<=', self.to_date), ('add_client_id.id', '=', self.client_management_id.id)]).ids
            else:
                self.account_management_ids = self.env['account.management'].search([('invoice_today', '>=', self.date), ('invoice_today', '<=', self.to_date)])
        else:
            if self.client_management_id:
                self.account_management_ids = self.env['account.management'].search([('add_client_id.id', '=', self.client_management_id.id)]).ids
            else:
                return


        # if self.date and self.to_date and self.client_management_id is False:
        #     print("Date and end date")
        #     self.account_management_ids = self.env['account.management'].search([('invoice_today', '>=', self.date), ('invoice_today', '<=', self.to_date)])
        #     print(self.account_management_ids)
        # elif self.client_management_id and self.date is False:
        #     print("Only Client")
        #     self.account_management_ids = self.env['account.management'].search([('add_client_id.id', '=', self.client_management_id.id)]).ids
        #     print(self.account_management_ids)
        # elif self.date and self.to_date and self.client_management_id:
        #     self.account_management_ids = self.env['account.management'].search(
        #                     [('invoice_today', '>=', self.date), ('invoice_today', '<=', self.to_date), ('add_client_id.id', '=', self.client_management_id.id)]).ids
        #     print(self.account_management_ids)


        # print(self.any_name)
        # self.account_management_ids = any_name
        achieved_amount = 0
        if self.account_management_ids:
            for i in self.account_management_ids:
                achieved_amount = achieved_amount + i.amount_total
                self.achieved_total = achieved_amount
                print(self.achieved_total)

    # @api.onchange('date', 'to_date')
    # def calculate_target(self):
    #     """This method is used to calculate the target of the salesperson from lines"""
    #     # target_total = 0
    #     # if self.target_ids:
    #     #     for i in self.target_ids:
    #     #         target_total = target_total + i.target
    #     # self.target_amount = target_total
    #
    #     achieved_amount = 0
    #     if self.account_management_ids:
    #         for i in self.account_management_ids:
    #             achieved_amount = achieved_amount + i.amount_total
    #             self.achieved_total = achieved_amount
    #             print(self.achieved_total)

    @api.model
    def create(self, values):
        """
        Over writted this method to give the name for record
        :param values:
        :return:
        """
        res = super(TargetAssignment, self).create(values)
        d11 = fields.Date.today()

        for this in res:
            d1 = datetime.strptime(str(d11), '%Y-%m-%d')
            locale = res.env.context.get('lang') or 'en_US'
            this.name = 'Target of  ' + ' _ ' + tools.ustr(
                babel.dates.format_date(date=d1, format='MMMM-y', locale=locale))

        return res



    # def action_pending(self):
    #     pending_tree = {
    #         'name': _('Target'),
    #         'view_type': 'form',
    #         'view_mode': 'tree,form',
    #         'view_id': False,
    #         'res_model': 'account.management',
    #         # 'context': {'default_add_client_id': self.id},
    #         'type': 'ir.actions.act_window',
    #         'target': 'current',
    #         'domain': [('invoice_today', '>=', self.date), ('invoice_today', '<=', self.to_date)]
    #     }
    #     return pending_tree



class DailyTargetLine(models.Model):
    _name = 'daily.target.line'
    _description = 'Daily Target Line'
    _order = "id desc"

    target = fields.Float(string='Target')
    target_id = fields.Many2one('target.management', string='Target Program')
    achieved_amount = fields.Float(string='Achievement', readonly=True, copy=False)
    date = fields.Date(string='Date', default=lambda self: fields.Date.today())
    to_date = fields.Date(string='To Date', default=lambda self: fields.Date.today())

    # @api.onchange('date', 'to_date')
    # def get_amount(self):
    #     field1 = self.env['account.management'].search([('invoice_today', '=', self.date)])
    #     field2 = self.env['account.management'].search([('invoice_today', '=', self.to_date)])
    #     for rec in self:
    #         rec.update({
    #             'date': field1,
    #             'to_date': field2
    #         })
