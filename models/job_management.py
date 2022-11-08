from stdnum.at import uid

from odoo import api, fields, models, _
from odoo.addons.base.models.report_paperformat import PAPER_SIZES
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class JobManagement(models.Model):
    _name = "job.management"
    _inherit = ['mail.thread']
    _description = "Job Management"
    _rec_name = 'job_name'

    task_management_ids = fields.One2many('task.management', 'job_management_id')
    client_id = fields.Many2one('client.management')
    project_management_id = fields.Many2one('project.management', string="Project", track_visibility=True)
    client_management_id = fields.Many2one(related="project_management_id.client_id", readonly=False, string="Client", track_visibility=True, required=True)
    checklist = fields.Text(related="project_management_id.checklist", readonly=False, string="Checklist", track_visibility=True)
    job_target_id = fields.Many2one('job.target')
    name = fields.Char(readonly=True, copy=False, track_visibility=True, default='New')
    job_name = fields.Char(string="Job Name", required=True)
    job_type = fields.Selection(selection=[('new', 'New'), ('edit', 'Edit')],
                            string="Job Type", track_visibility=True)
    social_medias = fields.Boolean(string="Social Media", track_visibility=True)
    created_date = fields.Date(related="project_management_id.start_date", string="Created Date", readonly=False)
    amount_untaxed = fields.Float(string="Price", track_visibility=True)
    price_subtotal = fields.Float(string="Total Price", track_visibility=True)
    price_tax = fields.Float(string="Tax(%)")
    sum = fields.Char(default='sum', track_visibility=True)
    stage = fields.Selection([('new', 'New'), ('processing', 'Processing'), ('hold', 'Hold'),('completed', 'Completed')],
                            string="Stage", default='new', tracking=True)
    job_category = fields.Selection([('print', 'Print'), ('digital_work', 'Digital Work'), ('branding', 'Branding')],
                            compute="get_job_category", string="Job Category", tracking=True, store=True, readonly=False)
    # customer_type = fields.Selection(selection="_get_customer_type", string="Customer Type")
    print_category = fields.Selection([('brochure', 'Brochure'), ('tshirt', 'T-Shirt'), ('catalog', 'Catalog'), ('billboard', 'Bill Board'), ('stationary', 'Stationary Design'),
                                       ('flyer', 'Flyer/Leaflet'), ('menucard', 'Menu Card'), ('business_card', 'Business Card'), ('banner', 'Banner'), ('letter_head', 'Letter Head'),
                                       ('package_design', 'Package Design'), ('hoarding', 'Hoardings'), ('seal', 'Seal'), ('voucher', 'Voucher Design')],
                             string="Job Sub Category", tracking=True, store=True)
    digital_category = fields.Selection([('ppt', 'PPT'), ('sm', 'SM'), ('e_business_card', 'E-Business card'), ('website_design', 'Website Designs '),
                                            ('2d_animation', '2D Animations'), ('3d_animation', '3D Animations'), ('video', 'Video'),
                                            ('motion_graphics', 'Motion Graphics'), ('digital_drawings', 'Digital Drawings'), ('content_writing', 'Content Writing'), ('e_profile', 'E-Profile'),
                                         ('script_writing', 'Script Writing'), ('e_catalog', 'E-Catalog')],
                            string="Job Sub Category", tracking=True, store=True)
    branding_category = fields.Selection([('logo_basic', 'Logo- Basic Package'), ('logo_advanced','Logo- Advanced Package'), ('brand_naming_tagline', 'Brand- Naming & Tagline')],
                            string="Job Sub Category", tracking=True, store=True)
    pending_task_count = fields.Integer(compute="get_pending_job")
    # completed_task_count = fields.Integer(compute="get_completed_job")

    @api.model
    def create(self, vals):
        print("hii")
        record = self.env['job.management'].create({
            'stage': 'processing'
        })
        return record

    def write(self, vals):
        if any(stage == 'completed' for stage in set(self.mapped('stage'))):
            raise UserError(_("No edits in Completed jobs"))
        else:
            return super().write(vals)

    def name_get(self):
        result = []
        for rec in self:
            if self.env.context.get('hide_code'):
                name = rec.job_name + '[' + rec.name + ']'
            else:
                name = rec.job_name
            result.append((rec.id, name))
        return result

    def action_complete_job(self):
        data = []
        for rec in self.task_management_ids:
            data.append(rec.stage_id)
        if 'new' in data or 'processing' in data or 'hold' in data:
            raise ValidationError("Please ensure that all of the tasks were completed")
        elif not self.task_management_ids:
            raise ValidationError("There is no tasks found")
        else:
            self.stage = 'completed'

    def action_set_hold(self):
        val = 1
        self.stage = 'hold'

    def get_pending_job(self):
        self.pending_task_count = self.env['task.management'].search_count([('job_management_id', '=', self.id), ('stage_id', '!=', 'completed')])
        staging_tree = {
             'name': _('Completed Jobs'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'task.management',
            'type': 'ir.actions.act_window',
            'context': {'default_job_management_id': self.id},
            'target': 'current',
            'domain': [('job_management_id', '=', self.id), ('stage_id', '!=', 'completed')]
        }
        return staging_tree

    @api.depends('amount_untaxed', 'price_tax', 'price_subtotal')
    def _compute_amount(self):
        for line in self:
            price = line.amount_untaxed
            taxes = line.price_tax
            a = taxes
            b = a / 100
            amount_tax = b * price
            line.update({
                'amount_untaxed': price,
                'price_tax': taxes,
                'price_subtotal': amount_tax,
            })

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('job.management') or 'New'
        result = super(JobManagement, self).create(vals)

        return result

    def task_creation(self):
        return {
            'res_model': 'task.management',
            'type': 'ir.actions.act_window',
            'context': {'default_job_management_id': self.id,
                        },
            'view_mode': 'form',
            'view_id': self.env.ref("fxm_project_management.task_management_view").id,
        }

    @api.onchange('job_category')
    def get_job_category(self):
        for record in self.project_management_id:
            if record.project_type == 'monthly':
                self.job_category = 'digital_work'

    # def _get_customer_type(self):
    #         # if self.name:
    #     if self.env['project.management'].search([('project_type', '!=', 'monthly')]):
    #         return [('cash_customer', 'Cash Customer'), ('credit_customer', 'Credit Customer'),
    #                 ('cash_customer_vendor', 'Cash Customer and Vendor'),
    #                 ('credit_customer_vendor', 'Credit Customer and Vendor')]
    #     else:
    #         return [('cash_customer', 'Cash Customer'), ('credit_customer', 'Credit Customer')]

    @api.onchange('task_management_ids')
    def check_stages(self):
        for order in self.task_management_ids:
            if order.stage_id != 'completed':
                self.stage ='draft'
            else:
                return
            self.stage ='completed'


class JobJobType(models.Model):
    _name = "job.job.type"
    _description = "Job Types"

    name = fields.Char(string="Name")


class JobVariants(models.Model):
    _name = "job.variants"
    _description = "Variants Job "

    name = fields.Char(string="Name")




