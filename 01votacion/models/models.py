# -*- coding: utf-8 -*-


# Archivo Python: modelos.py
from pytz import timezone, UTC
from odoo.exceptions import ValidationError
from odoo import models, fields, api, exceptions
from odoo import models, fields, api
import base64
import csv
from io import StringIO

class DownloadVotingTemplateWizard(models.TransientModel):
    _name = 'download.voting.template.wizard'
    _description = 'Wizard para descargar e importar plantilla de procesos de votación'

    file = fields.Binary(string='Archivo CSV', help="Suba el archivo CSV con los datos de los procesos de votación.")

    def action_download_template(self):
        """Genera y descarga un archivo CSV de ejemplo."""
        # Crear el contenido del CSV
        csv_data = "Descripcion;Fecha de Inicio;Fecha de Fin;Estado;Pais de la Sede;Candidatos\n"
        csv_data += "Proceso 1;2023-10-01 00:00:00;2023-10-10 23:59:59;draft;codigo del pais eje CO;candidato\n"
        csv_data += "Proceso 1;2023-10-01 00:00:00;2023-10-10 23:59:59;draft;codigo del pais eje AR;candidato\n"

        # Convertir el contenido a base64
        csv_file = base64.b64encode(csv_data.encode('utf-8'))

        # Crear un registro temporal para almacenar el archivo
        attachment = self.env['ir.attachment'].create({
            'name': 'plantilla_procesos_votacion.csv',
            'datas': csv_file,
            'mimetype': 'text/csv; charset=utf-8',
        })

        # Devolver la acción de descarga
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def action_import(self):
        """Importa los datos del archivo CSV y crea los procesos de votación."""
        self.ensure_one()

        # Verificar si se cargó un archivo
        if not self.file:
            raise models.ValidationError("Por favor, suba un archivo CSV.")

        # Decodificar el archivo
        file_content = base64.b64decode(self.file)

        # Intentar decodificar con UTF-8, y si falla, intentar con ISO-8859-1
        try:
            file_content = file_content.decode('utf-8-sig')  # Usar 'utf-8-sig' para manejar el BOM
        except UnicodeDecodeError:
            try:
                file_content = file_content.decode('iso-8859-1')
            except UnicodeDecodeError as e:
                raise models.ValidationError(f"No se pudo decodificar el archivo: {e}")

        csv_file = StringIO(file_content)
        reader = csv.DictReader(csv_file, delimiter=';')

        # Normalizar los nombres de las columnas (eliminar espacios y caracteres no válidos)
        reader.fieldnames = [name.strip().replace('\ufeff', '') for name in reader.fieldnames]

        # Verificar que el archivo CSV tenga las columnas correctas
        required_columns = {'Descripcion', 'Fecha de Inicio', 'Fecha de Fin', 'Estado', 'Pais de la Sede', 'Candidatos'}
        if not required_columns.issubset(reader.fieldnames):
            raise models.ValidationError(
                f"El archivo CSV debe contener las siguientes columnas: {', '.join(required_columns)}. "
                f"Columnas encontradas: {', '.join(reader.fieldnames)}"
            )

        # Procesar cada fila del archivo CSV
        for row in reader:
            # Obtener el ID del pais a partir del código
            country_code = row['Pais de la Sede'].strip().upper()
            country = self.env['res.country'].search([('code', '=', country_code)], limit=1)
            if not country:
                raise models.ValidationError(f"No se encontró el pais con código: {country_code}")

            # Crear el proceso de votación
            self.env['voting.process'].create({
                'name': row['Descripcion'],
                'start_date': row['Fecha de Inicio'],
                'end_date': row['Fecha de Fin'],
                'state': row['Estado'],
                'country_id': country.id,
                'candidate_ids': [(6, 0, self._get_candidate_ids(row['Candidatos']))],
            })

        return {
            'type': 'ir.actions.act_window_close',
        }

    def _get_candidate_ids(self, candidate_names):
        """Convierte los nombres de los candidatos en una lista de IDs."""
        candidate_ids = []
        for name in candidate_names.split(','):
            candidate = self.env['candidate.student'].search([('name', '=', name.strip())], limit=1)
            if candidate:
                candidate_ids.append(candidate.id)
        return candidate_ids


class ValidationCheckVote(models.Model):
    _name = 'validation.check.vote'
    _description = 'Validation Check Vote'
    _sql_constraints = [
        ('student_id_input_unique', 'UNIQUE(student_id_input)', 'El ID del estudiante ya ha sido registrado. No se permiten duplicados.')
    ]

    student_id_input = fields.Integer(string="ID del Estudiante", required=True)
    student_validated = fields.Boolean(string="Estudiante Validado", compute='_compute_check_student_id')
    selected_candidate_image = fields.Image(
        string='Imagen del Candidato',
        compute='_compute_selected_candidate_image'
    )
    selected_process_id = fields.Many2one(
        'voting.process',
        string='Proceso de Votación',
        domain="[('state', '=', 'in_progress')]", ondelete='cascade'
    )
    selected_candidate_id = fields.Many2one(
        'candidate.student',
        string='Selected Candidate',
        domain="[('id', 'in', candidates_filtered_ids)]"
    )
    is_available = fields.Boolean(
        string='Voting Available',
        compute='_compute_is_available'
    )
    selected_candidate_info = fields.Text(
        string='Información del Candidato',
        compute='_compute_selected_candidate_info'
    )
    candidate_ids = fields.Many2many(
        'candidate.student',
        string='Candidates',
        required=True,
        domain="[('id', 'in', candidates_filtered_ids)]"
    )
    candidates_filtered_ids = fields.Many2many(
        'candidate.student',
        compute='_compute_candidates_filtered',
        store=False
    )

    @api.constrains('student_id_input')
    def _check_student_id_input_unique(self):
        for record in self:
            if self.search_count([('student_id_input', '=', record.student_id_input)]) > 1:
                raise ValidationError('El ID del estudiante ya ha sido registrado. No se permiten duplicados.')

    @api.depends('selected_candidate_id')
    def _compute_selected_candidate_image(self):
        for record in self:
            if record.selected_candidate_id:
                record.selected_candidate_image = record.selected_candidate_id.image
            else:
                record.selected_candidate_image = False

    @api.depends('selected_process_id')
    def _compute_candidates_filtered(self):
        for record in self:
            if record.selected_process_id:
                candidates = record.selected_process_id.candidate_ids
                record.candidates_filtered_ids = candidates
            else:
                record.candidates_filtered_ids = self.env['candidate.student']

    def _compute_selected_candidate_info(self):
        for record in self:
            if record.selected_candidate_id:
                candidate = record.selected_candidate_id
                info = f"Nombre: {candidate.name}\nID: {candidate.num_id}"
                record.selected_candidate_info = info
            else:
                record.selected_candidate_info = ""

    def _compute_is_available(self):
        for record in self:
            result = record.check_voting_availability()
            record.is_available = result.get('is_available', False)

    def check_voting_availability(self):
        if not self.selected_process_id:
            return {
                'is_available': False,
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'Por favor, selecciona un proceso de votación válido.',
                    'type': 'danger',
                    'sticky': False,
                }
            }

        # Obtener la zona horaria del pais seleccionado
        country_code = self.selected_process_id.country_id.code
        try:
            process_tz = timezone(self.env['res.country'].search([('code', '=', country_code)], limit=1).timezone)
        except:
            process_tz = timezone('UTC')

        # Obtener la zona horaria local
        local_country_code = self.env.user.company_id.country_id.code
        try:
            local_tz = timezone(self.env['res.country'].search([('code', '=', local_country_code)], limit=1).timezone)
        except:
            local_tz = timezone('UTC')

        # Fechas en la zona horaria del proceso
        start_date_process = process_tz.localize(self.selected_process_id.start_date)
        end_date_process = process_tz.localize(self.selected_process_id.end_date)

        # Fechas en la zona horaria local
        current_time_local = UTC.localize(fields.Datetime.now()).astimezone(local_tz)
        current_time_process = current_time_local.astimezone(process_tz)

        # Validar si ambas zonas horarias están dentro del rango
        if start_date_process <= current_time_process <= end_date_process:
            return {
                'is_available': True,
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '¡Éxito!',
                    'message': f'El proceso de votación "{self.selected_process_id.name}" está activo y disponible en el pais.',
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            return {
                'is_available': False,
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': f'El proceso de votación "{self.selected_process_id.name}" no está disponible en tu zona horaria o la del proceso.',
                    'type': 'danger',
                    'sticky': False,
                }
            }

    def _compute_check_student_id(self):
        for record in self:
            result = record.check_student_id()
            record.student_validated = result.get('student_validated', False)

    def check_student_id(self):
        # Verificar si el ID del estudiante existe
        student = self.env['school.student'].search([('num_id', '=', self.student_id_input)], limit=1)
        if student:
            return {
                'student_validated' : True,
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Estudiante Validado',
                    'message': f'El estudiante con ID {self.student_id_input} ha sido validado.',
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            return {
                'student_validated': False,
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'El ID del estudiante no es válido.',
                    'type': 'danger',
                    'sticky': False,
                }
            }

    def vote_candidate(self):
        if not self.selected_candidate_id:
            raise exceptions.UserError('Debes seleccionar un candidato para votar.')

        if not self.selected_process_id:
            raise exceptions.UserError('Debes seleccionar un proceso de votación.')

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


# Modelo para la configuración del proceso de votación
class VotingProcess(models.Model):
    _name = 'voting.process'
    _description = 'Voting Process'

    name = fields.Char(string='Descripcion', required=True)
    start_date = fields.Datetime(string='Fecha de Inicio', required=True)
    end_date = fields.Datetime(string='Fecha de Fin', required=True)
    country_id = fields.Many2one('res.country', string='Pais de la Sede', required=True)
    candidate_ids = fields.Many2many('candidate.student', string='Candidatos')
    vote_count_ids = fields.One2many('voting.candidate.vote', 'voting_process_id', string='Votos')
    selected_country_id = fields.Many2one('res.country', string='Seleccione pais para votar')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed')
    ], string='Estado', default='draft')
    selected_candidate_id = fields.Many2one(
        'candidate.student',
        string='Selected Candidate',
        domain="[('id', 'in', candidates_filtered_ids)]"
    )


    def action_set_in_progress(self):
        """Cambia el estado a 'In Progress' en los registros seleccionados."""
        for record in self:
            if record.state == 'draft':
                record.state = 'in_progress'

    def action_set_closed(self):
        """Cambia el estado a 'Closed' en los registros seleccionados."""
        for record in self:
            if record.state in ['draft', 'in_progress']:
                record.state = 'closed'

    def action_open_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Wizard",
            "res_model": "download.voting.template.wizard",
            "view_mode": "form",
            "view_id": False,
            "target": "new",
        }


# Modelo para gestionar los candidatos al voto
class CandidateVote(models.Model):
    _name = "voting.candidate.vote"
    _description = "Candidate Vote"

    voting_process_id = fields.Many2one('voting.process', string='Voting Process', required=True, ondelete='cascade')
    candidate_id = fields.Many2one('candidate.student', string='Candidate', required=True)
    vote_count = fields.Integer(string='Vote Count', default=0)


# Modelo para gestionar los votos de los usuarios
class UserVote(models.Model):
    _name = "user.vote"
    _description = "User Vote"

    user_id = fields.Many2one('res.users', string="User", required=True, default=lambda self: self.env.user, readonly=True)
    candidate_id = fields.Many2one('candidate.student', string="Candidate", required=True, ondelete='cascade')
    vote_date = fields.Datetime(string="Vote Date", default=fields.Datetime.now, readonly=True)
    campus_name1 = fields.Many2one("school.campus", string='Campus', required=True,
                                   domain="[('country_id', '!=', False)]")

    @api.model
    def create(self, vals):

        voting_process = self.env['voting.process'].search([
            ('country_id', '=', vals.get('country_id')),
            ('state', '=', 'in_progress'),
            ('start_date', '<=', fields.Datetime.now()),
            ('end_date', '>=', fields.Datetime.now()),
        ], limit=1)

        if not voting_process:
            raise exceptions.UserError('No hay proceso activo para el proceso de seleccion escogido o esta fuera del rango de tiempo.')

        vals['voting_process_id'] = voting_process.id
        return super(UserVote, self).create(vals)


# Modelo para gestionar los campus
class Campus(models.Model):
    _name = "school.campus"
    _description = "Sede"

    country_id = fields.Many2one('res.country', string="Country", required=True)
    name = fields.Char(string="Nombre de la Sede", required=True)

    @api.model
    def name_get(self):
        result = []
        for record in self:
            display_name = record.country_id.name if record.country_id else record.name
            result.append((record.id, display_name))
        return result
    def action_continue_voting(self):
        """Acción para continuar con la votación desde el campus."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Votación',
            'res_model': 'user.vote',
            'view_mode': 'form',
            'target': 'new',
        }


# Modelo para estudiantes
class Student(models.Model):
    _name = "school.student"
    _description = "Estudiantes"

    name = fields.Char(string="Nombre", required=True)
    carrera = fields.Char(string="Carrera", required=True)
    num_id = fields.Integer(string="Numero de ID", required=True)
    campus_name1 = fields.Many2one("school.campus", string='Sede', required=True, domain="[('country_id', '!=', False)]")

    @api.model
    def create(self, vals):
        if self.search([('num_id', '=', vals['num_id'])]):
            raise exceptions.UserError('El numero de identificacion ya existe.')
        return super(Student, self).create(vals)


# Modelo para candidatos
class Candidate(models.Model):
    _name = "candidate.student"
    _description = "Candidate"

    name = fields.Char(string="Nombre", required=True)
    num_id = fields.Integer(string="Numero de ID", required=True)
    image = fields.Image(string="Foto")

    @api.model
    def create(self, vals):
        if self.search([('num_id', '=', vals['num_id'])]):
            raise exceptions.UserError('ID number already exists.')
        return super(Candidate, self).create(vals)

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name} (ID: {record.num_id})"
            result.append((record.id, name))
        return result

# Modelo para la votacion del candidato
class VotingCandidateVote(models.Model):
    _name = 'voting.candidate.vote'
    _description = 'Voting Candidate Vote'

    voting_process_id = fields.Many2one('voting.process', string='Voting Process', required=True, ondelete='cascade')
    candidate_id = fields.Many2one('candidate.student', string='Candidate', required=True)
    vote_count = fields.Integer(string='Votes', default=0)
    candidate_image = fields.Image(
        string='Imagen del Candidato',
        related='candidate_id.image'
    )
