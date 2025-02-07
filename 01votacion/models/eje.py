def vote_candidate(self):
    if not self.selected_candidate_id:
        raise exceptions.UserError('Debes seleccionar un candidato para votar.')

    if not self.selected_process_id:
        raise exceptions.UserError('Debes seleccionar un proceso de votación.')

    # Verificar si el estudiante ya ha votado
    existing_vote = self.env['voting.candidate.vote'].search([
        ('student_id_input', '=', self.student_id_input),
        ('voting_process_id', '=', self.selected_process_id.id),
    ], limit=1)

    if existing_vote:
        raise exceptions.UserError(f'El estudiante con ID {self.student_id_input} ya ha votado en este proceso de votación.')

    # Si no ha votado, proceder con el registro del voto
    vote_record = self.env['voting.candidate.vote'].search([
        ('voting_process_id', '=', self.selected_process_id.id),
        ('candidate_id', '=', self.selected_candidate_id.id)
    ], limit=1)

    if vote_record:
        vote_record.vote_count += 1
    else:
        self.env['voting.candidate.vote'].create({
            'voting_process_id': self.selected_process_id.id,
            'candidate_id': self.selected_candidate_id.id,
            'vote_count': 1,
        })

    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': '¡Éxito!',
            'message': f'Has votado por {self.selected_candidate_id.name}.',
            'type': 'success',
            'sticky': False,
        }
    }
