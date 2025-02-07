from odoo import models, fields, api

class VoteProcessor(models.Model):
    _name = 'vote.processor'
    _description = 'Vote Processor'

    vote_checker_id = fields.Many2one('validation.check.vote', string="Vote Checker", default=True)

    def process_vote(self):
        validation_result = self.vote_checker_id.check_availability()

        if validation_result['is_available']:
            self.votar()
        else:
            self.no_votar()

    def votar(self):
        pass

    def no_votar(self):
        pass