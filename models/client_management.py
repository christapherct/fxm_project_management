from odoo import api, fields, models, _, exceptions


class ClientAssignment(models.Model):
    _name = "client.management"
    _inherit = ['mail.thread']
    _description = "Clients"

    name = fields.Char(string="Name", tracking=True, required=True)
    email = fields.Char(string="Email", tracking=True)
    category = fields.Selection(selection=[('premium', 'Premium'), ('normal', 'Normal')],
                                string="Category", tracking=True)
    address = fields.Text(string="Customer Address", tracking=True)
    checklist = fields.Text(string="Checklist", tracking=True)
    contact = fields.Char(string="Contact no", tracking=True)
    office_num = fields.Char(string="Office no", tracking=True)
    website = fields.Char(string="Website", tracking=True)
    facebook_url = fields.Char(string="Facebook URL", tracking=True)
    instagram_url = fields.Char(string="Instagram URL", tracking=True)
    social_media = fields.Selection(selection=[('instagram', 'Instagram'), ('facebook', 'Facebook')],
                                    string="Social Media", tracking=True)
    state = fields.Selection([('pending', 'Pending'), ('assign', 'Assigned'), ('done', 'Completed'),
                              ('cancel', 'Cancelled')], string="Status", readonly=True, default="pending", tracking=True)
    account_management_ids = fields.One2many('account.management', 'client_management_id', tracking=True)
    proposal = fields.Boolean(string="Add Proposal", tracking=True)
    job_management_ids = fields.One2many('job.management', 'client_id', tracking=True)
    # lead_management_ids = fields.One2many('lead.management', 'customer_id', tracking=True)
    lead_mgmt_id = fields.Many2one('lead.management')
    project_count = fields.Integer(compute="check_projects", tracking=True)

    def project_creation(self):
        return {
            'res_model': 'project.management',
            'type': 'ir.actions.act_window',
            'context': {'default_client_id': self.id,
                        'default_lead_id': self.id,
                        },
            'view_mode': 'form',
            'view_id': self.env.ref("fxm_project_management.project_management_view").id,
        }

    def check_projects(self):
        self.project_count = self.env['project.management'].search_count([('client_id', '=', self.id)])
        staging_tree = {
            'name': _('Projects'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'project.management',
            'type': 'ir.actions.act_window',
            'context': {'default_client_id': self.id,
                        },
            'domain': [('client_id', '=', self.id)],
            'target': 'current',
        }
        return staging_tree

    # @api.model
    # def create(self, vals):
    #     if self.env['lead.management'].search([('customer_id', '!=', self.id)]):
    #         raise exceptions.Warning(_('Customer Exist for this particular lead'))
    #     else:
    #         return super(ClientAssignment, self).create(vals)


