# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import defaultdict

from odoo.exceptions import ValidationError, UserError, AccessError
from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.tools import float_compare, get_lang, format_date

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
    # state = fields.Selection([('draft', 'Draft'), ('processing', 'Processing'), ('done', 'Posted')], string="State", default='draft', tracking=True)
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

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('account.move') or 'New'
            vals['state'] = 'processing'
            if vals['state'] == 'processing':
                record = self.env['project.management'].search([('account_inherit_ids', '=', self.id)])
                record.write({'stage': 'invoiced'})
        result = super(AccountMoveMgmnt, self).create(vals)
        if not result.job_management_ids:
            raise ValidationError('Please ensure that there is jobs are included!')
        return result

    def confirm_action_post(self):
        self.state = 'posted'
        # inherit of the function from account.move to validate a new tax and the priceunit of a downpayment
        # res = super(AccountMoveMgmnt, self).action_post()
        # line_ids = self.mapped('job_management_ids')
        # for line in line_ids:
        #     try:
        #         # line.sale_line_ids.tax_id = line.tax_ids
        #         # if all(line.tax_ids.mapped('price_include')):
        #         #     line.sale_line_ids.price_unit = line.price_unit
        #         else:
        #             # To keep positive amount on the sale order and to have the right price for the invoice
        #             # We need the - before our untaxed_amount_to_invoice
        #             # line.sale_line_ids.price_unit = -line.sale_line_ids.untaxed_amount_to_invoice
        #     except UserError:
        #         # a UserError here means the SO was locked, which prevents changing the taxes
        #         # just ignore the error - this is a nice to have feature and should not be blocking
        #         pass
        # return res

    def _post(self, soft=True):
        """Post/Validate the documents.

        Posting the documents will give it a number, and check that the document is
        complete (some fields might not be required if not posted but are required
        otherwise).
        If the journal is locked with a hash table, it will be impossible to change
        some fields afterwards.

        :param soft (bool): if True, future documents are not immediately posted,
            but are set to be auto posted automatically at the set accounting date.
            Nothing will be performed on those documents before the accounting date.
        :return Model<account.move>: the documents that have been posted
        """
        if soft:
            future_moves = self.filtered(lambda move: move.date > fields.Date.context_today(self))
            future_moves.auto_post = True
            for move in future_moves:
                msg = _('This move will be posted at the accounting date: %(date)s', date=format_date(self.env, move.date))
                move.message_post(body=msg)
            to_post = self - future_moves
        else:
            to_post = self

        # `user_has_group` won't be bypassed by `sudo()` since it doesn't change the user anymore.
        # if not self.env.su and not self.env.user.has_group('account.group_account_invoice'):
        #     raise AccessError(_("You don't have the access rights to post an invoice."))
        for move in to_post:
            # if move.partner_bank_id and not move.partner_bank_id.active:
            #     raise UserError(_("The recipient bank account link to this invoice is archived.\nSo you cannot confirm the invoice."))
            # if move.state == 'posted':
            #     raise UserError(_('The entry %s (id %s) is already posted.') % (move.name, move.id))
            if not move.job_management_ids:
                raise UserError(_('You need to add a line before posting.'))
            # if move.auto_post and move.date > fields.Date.context_today(self):
            #     date_msg = move.date.strftime(get_lang(self.env).date_format)
            #     raise UserError(_("This move is configured to be auto-posted on %s", date_msg))

            # if not move.partner_id:
            #     if move.is_sale_document():
            #         raise UserError(_("The field 'Customer' is required, please complete it to validate the Customer Invoice."))
            #     elif move.is_purchase_document():
            #         raise UserError(_("The field 'Vendor' is required, please complete it to validate the Vendor Bill."))

            # if move.is_invoice(include_receipts=True) and float_compare(move.amount_total, 0.0, precision_rounding=move.currency_id.rounding) < 0:
            #     raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead. Use the action menu to transform it into a credit note or refund."))

            # Handle case when the invoice_date is not set. In that case, the invoice_date is set at today and then,
            # lines are recomputed accordingly.
            # /!\ 'check_move_validity' must be there since the dynamic lines will be recomputed outside the 'onchange'
            # environment.
            # if not move.invoice_date:
            #     if move.is_sale_document(include_receipts=True):
            #         move.invoice_date = fields.Date.context_today(self)
            #         move.with_context(check_move_validity=False)._onchange_invoice_date()
            #     elif move.is_purchase_document(include_receipts=True):
            #         raise UserError(_("The Bill/Refund date is required to validate this document."))

            # When the accounting date is prior to the tax lock date, move it automatically to the next available date.
            # /!\ 'check_move_validity' must be there since the dynamic lines will be recomputed outside the 'onchange'
            # environment.
            # if (move.company_id.tax_lock_date and move.date <= move.company_id.tax_lock_date) and (move.line_ids.tax_ids or move.line_ids.tax_tag_ids):
            #     move.date = move._get_accounting_date(move.invoice_date or move.date, True)
            #     move.with_context(check_move_validity=False)._onchange_currency()


        # for move in to_post:
            # Fix inconsistencies that may occure if the OCR has been editing the invoice at the same time of a user. We force the
            # partner on the lines to be the same as the one on the move, because that's the only one the user can see/edit.
            # wrong_lines = move.is_invoice() and move.line_ids.filtered(lambda aml: aml.partner_id != move.commercial_partner_id and not aml.display_type)
            # if wrong_lines:
            #     wrong_lines.partner_id = move.commercial_partner_id.id

        # Create the analytic lines in batch is faster as it leads to less cache invalidation.
        # to_post.mapped('line_ids').create_analytic_lines()
        # to_post.write({
        #     'state': 'posted',
        #     'posted_before': True,
        # })

        # for move in to_post:
        #     move.message_subscribe([p.id for p in [move.partner_id] if p not in move.sudo().message_partner_ids])

            # Compute 'ref' for 'out_invoice'.
        #     if move._auto_compute_invoice_reference():
        #         to_write = {
        #             'payment_reference': move._get_invoice_computed_reference(),
        #             'line_ids': []
        #         }
        #         for line in move.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable')):
        #             to_write['line_ids'].append((1, line.id, {'name': to_write['payment_reference']}))
        #         move.write(to_write)
        #
        # for move in to_post:
        #     if move.is_sale_document() \
        #             and move.journal_id.sale_activity_type_id \
        #             and (move.journal_id.sale_activity_user_id or move.invoice_user_id).id not in (self.env.ref('base.user_root').id, False):
        #         move.activity_schedule(
        #             date_deadline=min((date for date in move.line_ids.mapped('date_maturity') if date), default=move.date),
        #             activity_type_id=move.journal_id.sale_activity_type_id.id,
        #             summary=move.journal_id.sale_activity_note,
        #             user_id=move.journal_id.sale_activity_user_id.id or move.invoice_user_id.id,
        #         )
        #
        # customer_count, supplier_count = defaultdict(int), defaultdict(int)
        # for move in to_post:
        #     if move.is_sale_document():
        #         customer_count[move.partner_id] += 1
        #     elif move.is_purchase_document():
        #         supplier_count[move.partner_id] += 1
        # for partner, count in customer_count.items():
        #     (partner | partner.commercial_partner_id)._increase_rank('customer_rank', count)
        # for partner, count in supplier_count.items():
        #     (partner | partner.commercial_partner_id)._increase_rank('supplier_rank', count)

        # Trigger action for paid invoices in amount is zero
        # to_post.filtered(
        #     lambda m: m.is_invoice(include_receipts=True) and m.currency_id.is_zero(m.amount_total)
        # ).action_invoice_paid()
        #
        # # Force balance check since nothing prevents another module to create an incorrect entry.
        # # This is performed at the very end to avoid flushing fields before the whole processing.
        # to_post._check_balanced()
        return

