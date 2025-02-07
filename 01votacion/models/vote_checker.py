from odoo import models, fields, api

class VoteChecker(models.Model):
    _name = 'vote.checker'
    _description = 'Vote Checker'

    is_available = fields.Boolean(string="Availability", default=True)
    abc = 'abc'

    def check_availability(self):
        return {
            'is_available' : self.is_available,
            'otra_cosa': 'otra cosa'
        }
