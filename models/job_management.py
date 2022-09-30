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
    # project_type = fields.Selection(related="project_management_id.project_type", string="Job Type", readonly=False, track_visibility=True, compute="check_project_type")
    # job_type_id = fields.Many2one("job.job.type", string="Job Type")
    # job_variant_id = fields.Many2one("job.job.type", string="Job Name")
    job_name = fields.Char(string="Job Name", required=True)
    job_type = fields.Selection(selection=[('new', 'New'), ('edit', 'Edit')],
                                    string="Job Type", track_visibility=True, required=True)
    social_medias = fields.Boolean(string="Social Media", track_visibility=True)
    # category = fields.Selection(selection=[('special', 'Special Day'), ('branding', 'Branding'), ('product', 'Product/Service'), ('engagement', 'Engagement'),
    #                                        ('informative', 'Informative'), ('moment', 'Moment Marking'), ('other', 'Other')],
    #                                 string="Job Category", track_visibility=True, store=True)
    created_date = fields.Date(related="project_management_id.start_date", string="Created Date", readonly=False)
    amount_untaxed = fields.Float(string="Price", track_visibility=True)
    price_subtotal = fields.Float(string="Total Price", track_visibility=True)
    price_tax = fields.Float(string="Tax(%)")
    sum = fields.Char(default='sum', track_visibility=True)
    stage = fields.Selection([('new', 'New'), ('draft', 'Draft'), ('completed', 'Completed')],
                            string="Stage", default='new', tracking=True)
    job_category = fields.Selection([('print', 'Print'), ('digital_work', 'Digital Work'), ('branding', 'Branding')],
                             compute="check_job_category", string="Job Category", tracking=True, store=True, required=True, readonly=False, default='print')
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


    # def _check_project_date(self):
    #     for rec in self.project_management_id:
    #         if rec.start_date:
                # self.created_date = rec.start_date
                # rec.start_date = self.created_date


    # @api.onchange('project_management_id')
    # def update_related(self):
    #     print("hlo")
    #     if self.project_management_id:
    #         print("hii")
    #         for rec in self:
    #             rec.update({
    #                 'client_management_id': self.project_management_id.client_id
    #             })
    #             print(self.client_management_id)

    # def name_get(self):
    #     result = []
    #     for rec in self:
    #         name = rec.job_name
    #         result.append((rec.id, name))
    #     return result

    def name_get(self):
        result = []
        for rec in self:
            # name = rec.name
            if self.env.context.get('hide_code'):
                name = rec.job_name+ '[' + rec.name + ']'
                # name += "({})".format(rec.job_name)
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

    # def get_job_category(self):
        # if self.project_type:
        #     if self.project_type == 'monthly':
        #         self.job_category = 'digital_work'
        #     else:
        #         raise ValidationError("You have been selected Monthly project")
        # vals = []
        # for record in self.env['job.management'].search([]):
        #     if record.project_type in ['monthly']:
        #         vals.extend([('digital_work', 'Digital Work')])

    @api.onchange('project_type')
    def check_job_category(self):
        for rec in self.project_management_id:
            if rec.project_type == 'monthly':
                self.job_category = 'digital_work'

    # @api.onchange('project_type', 'digital_work')
    # def check_status(self):
    #     for rec in self:
    #         print(rec.job_category,"Categr")
    #         print(rec.project_type,"projct")
    #         if rec.project_type == 'monthly':
    #             print("TEST")
    #             if rec.job_category != 'digital_work':
    #                 print("Mixer")
    #                 raise ValidationError("Daaaa")
    #             else:
    #                 print("DEMO")
    #                 return

    # def check_job_category_selection(self):
    #     print(self.project_type, "CHECKKK")
    #     for rec in self:
    #         if rec.project_type != 'monthly':
    #             print("VVVVVVVVVVVVVVVVVVVV")
    #             rec.abc_categ = rec.a_sel
                # selection = [
                #     ('print', 'Print'),
                #     ('branding', 'Branding')
                # ]
                # return selection
            # elif self.project_type != 'one_time' or self.project_type != 'emergency' and self.project_type != 'monthly':
            #     print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            #     selection = [
            #         ('digital_work', 'Digital Work')
            #     ]
            #     return selection
            # else:
            #     print("OOOOOOOOOOOOOOOOOOOOOOOOOO")
            #     rec.abc_categ = rec.b_sel
            # selection = [
            #     ('digital_work', 'Digital')
            # ]
            # return selection


        # elif self.project_type == 'one_time' or self.project_type == 'emergency':
        #     self.job_category = 'print'
        # elif self.project_type == 'emergency' or self.project_type == 'one_time':
        #     self.job_category = 'branding'
        # else:
        #     raise ValidationError("Make sure you are selected Job category are same compared to Project Type")

    # @api.onchange('task_management_ids')
    # def check_stage(self):
    #     for order in self:
    #         for rec in self.task_management_ids:
    #             if rec.stage_id:
    #                 if rec.stage_id == 'completed':
    #                     # stage = rec.stage_id
    #                     # self.stage = 'completed'
    #                     print("hiiiiiiiiiiiiiiiiiiiiiii")
    #                 else:
    #                     # self.stage = 'draft'
    #                     print("hlooo")
    #                 print("KRRRRRRRRRRRRR")
    #             else:
    #                 print("howwwww")
                    # stage2 = rec.stage_id
            # order.update({
            #     'stage': stage,

            # })

    # @api.onchange('task_management_ids')
    # def check_stages(self):
    #     err_products = []
    #     for partner in self:
    #         for rec in partner.task_management_ids:
    #             data_mod = rec.env['task.management'].search([('stage_id', '!=', 'completed')])
    #             if data_mod not in err_products:
    #             # err_products = rec.env['task.management'].search([('stage_id', '!=', 'completed')]):
    #                 partner.stage = 'draft'
    #                 print("ppppppppppppppppppp")
    #             else:
    #                 partner.stage = 'completed'
    #                 print("qqqqqqqqqqqqqqqqqq")

    @api.onchange('task_management_ids')
    def check_stages(self):
        for order in self.task_management_ids:
            if order.stage_id != 'completed':
                self.stage ='draft'
            else:
                return
            self.stage ='completed'

    def check_project_type(self):
        for record in self.env['job.management'].search([]):
            if record.project_type in ['monthly']:
                print("monthly")


class JobJobType(models.Model):
    _name = "job.job.type"
    _description = "Job Types"

    name = fields.Char(string="Name")


class JobVariants(models.Model):
    _name = "job.variants"
    _description = "Variants Job "

    name = fields.Char(string="Name")




