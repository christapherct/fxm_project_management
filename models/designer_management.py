from odoo import api, fields, models, _


class DesignerAssignment(models.Model):
    _name = "designer.management"
    _inherit = ['mail.thread']
    _description = "Designer"

    add_task_ids = fields.One2many('task.management', 'partner_id')
    timesheet_management_ids = fields.One2many('timesheet.management', 'designer_management_id', compute="action_staging")

    name = fields.Char(string='Designer Name', track_visibility=True, required=True)
    department = fields.Char(string="Department", track_visibility=True)
    project_manager = fields.Char(string="Project Manager", track_visibility=True)

    def action_staging(self):
        staging_tree = {
            'name': _(''),
            'view_type': 'tree',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'timesheet.management',
            'type': 'ir.actions.act_window',
            'context': {'default_user_id': self.id},
            'target': 'current',
            'domain': [('user_id', '=', self.id)]
        }
        return staging_tree
