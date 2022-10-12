from stdnum.at import uid

from odoo import api, fields, models, _
from odoo.addons.base.models.report_paperformat import PAPER_SIZES
from odoo.exceptions import ValidationError
from datetime import datetime


class JobManagement(models.Model):
    _name = "job.management"
    _inherit = ['mail.thread']
    _description = "Job Management"
    _rec_name = 'job_name'

    task_management_ids = fields.One2many('task.management', 'job_management_id')
    client_id = fields.Many2one('client.management')
    project_management_id = fields.Many2one('project.management', string="Project", track_visibility=True, required=True)
    client_management_id = fields.Many2one(related="project_management_id.client_id", readonly=False, string="Client", track_visibility=True, required=True)
    checklist = fields.Text(related="project_management_id.checklist", readonly=False, string="Checklist", track_visibility=True)
    job_target_id = fields.Many2one('job.target')
    name = fields.Char(readonly=True, copy=False, track_visibility=True, default='New')
    job_name = fields.Char(string="Job Name", required=True)
    job_type = fields.Selection(selection=[('new', 'New'), ('edit', 'Edit')],
                            string="Job Type", track_visibility=True, required=True)
    social_medias = fields.Boolean(string="Social Media", track_visibility=True)
    created_date = fields.Date(related="project_management_id.start_date", string="Created Date", readonly=False)
    amount_untaxed = fields.Float(string="Price", track_visibility=True)
    price_subtotal = fields.Float(string="Total Price", track_visibility=True)
    price_tax = fields.Float(string="Tax(%)")
    sum = fields.Char(default='sum', track_visibility=True)
    stage = fields.Selection([('new', 'New'), ('draft', 'Draft'), ('completed', 'Completed')],
                            string="Stage", default='new', tracking=True)
    job_category = fields.Selection([('print', 'Print'), ('digital_work', 'Digital Work'), ('branding', 'Branding')],
                            compute="get_job_category", string="Job Category", tracking=True, store=True, required=True, readonly=False)
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

    def name_get(self):
        result = []
        for rec in self:
            if self.env.context.get('hide_code'):
                name = rec.job_name + '[' + rec.name + ']'
            else:
                name = rec.job_name
            result.append((rec.id, name))
        return result

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

    @api.onchange('task_management_ids')
    def check_stages(self):
        for order in self.task_management_ids:
            if order.stage_id != 'completed':
                self.stage ='draft'
            else:
                return
            self.stage ='completed'

    # def check_project_type(self):
    #     for record in self.env['job.management'].search([]):
    #         if record.project_type in ['monthly']:
    #             print("monthly")


class JobJobType(models.Model):
    _name = "job.job.type"
    _description = "Job Types"

    name = fields.Char(string="Name")


class JobVariants(models.Model):
    _name = "job.variants"
    _description = "Variants Job "

    name = fields.Char(string="Name")




