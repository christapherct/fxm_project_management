from odoo import fields, models,_,api


class TaskEvents(models.Model):
    _name = "task.event"
    _inherit = 'task.management'

    client_management_ids = fields.Many2many('client.management', string="Clients")
    client_management = fields.Many2one('client.management', string="Clients")
    task_management_id = fields.Many2one('task.management')
    name = fields.Char(string="Name")
    deadline = fields.Date()

    # @api.model
    # def create(self, values):
    #     print("Hiiiiiiiiiiiiiiiii")
    #
    #     res = super(TaskEvents, self).create(values)
    #     # print(self.id, "hlooo")
    #     for self.client_management_ids in [4,5]:
    #         print("Beginner")
    #         self.env['task.management'].create({
    #             'name': values['name'],
    #             'deadline': values['deadline'],
    #
    #         })
    #     return res

    def onchange_contact_person_many(self, cr, uid, ids, client_management_ids, context=None):
        if client_management_ids:
            li_emp = []

            for i in client_management_ids[0][2]:
                li_emp.append(i)

            emp = tuple(li_emp)

        return {'domain': {'client_management': [('id', 'in', emp)]}}









