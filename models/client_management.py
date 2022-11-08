from odoo import api, fields, models, _


class ClientAssignment(models.Model):
    _name = "client.management"
    _inherit = ['mail.thread']
    _description = "Clients"

    name = fields.Char(string="Name", track_visibility=True, required=True)
    email = fields.Char(string="Email", track_visibility=True)
    category = fields.Selection(selection=[('premium', 'Premium'), ('normal', 'Normal')],
                                string="Category", track_visibility=True)
    address = fields.Text(string="Customer Address", track_visibility=True)
    checklist = fields.Text(string="Checklist", track_visibility=True)
    contact = fields.Char(string="Contact no", track_visibility=True)
    office_num = fields.Char(string="Office no", track_visibility=True)
    website = fields.Char(string="Website", track_visibility=True)
    facebook_url = fields.Char(string="Facebook URL", track_visibility=True)
    instagram_url = fields.Char(string="Instagram URL", track_visibility=True)
    social_media = fields.Selection(selection=[('instagram', 'Instagram'), ('facebook', 'Facebook')],
                                    string="Social Media", track_visibility=True)
    state = fields.Selection([('pending', 'Pending'), ('assign', 'Assigned'), ('done', 'Completed'),
                              ('cancel', 'Cancelled')], string="Status", readonly=True, default="pending", track_visibility=True)
    account_management_ids = fields.One2many('account.management', 'client_management_id')
    proposal = fields.Boolean(string="Add Proposal")
    job_management_ids = fields.One2many('job.management', 'client_id')
    lead_management_ids = fields.One2many('lead.management', 'customer_id')
    project_count = fields.Integer(compute="check_projects")

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



