from flask import current_app
from flask_restx import Resource, fields, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
import json

from . import api_turnos

from .google_calendar_helpers import *

logger = logging.getLogger(__name__)

upload_parser = api_turnos.parser()
upload_parser.add_argument(
    "hospitalId", type=int, location="form", required=True, help="ID del hospital"
)
upload_parser.add_argument(
    "calendarId",
    type=str,
    location="form",
    required=True,
    help="ID del calendar asociado al medico",
)
upload_parser.add_argument(
    "turnoId", type=str, location="form", required=True, help="ID del turno"
)
upload_parser.add_argument(
    "eventText", type=str, location="form", required=True, help="eventText"
)


cancelar_turno = api_turnos.model(
    "CancelarTurno",
    {
        "hospitalId": fields.Integer(required=True, description="ID del hospital"),
        "calendarId": fields.String(
            required=True, description="ID del calendar asignado a un medico y su sede"
        ),
        "turnoId": fields.String(
            required=True, description="ID del evento para cancelar"
        ),
        "eventText": fields.String(
            required=True,
            description="Texto con para el header del evento en Google Calendar",
        ),
    },
)

turnos_medico = api_turnos.model(
    "TurnosDisponiblesMedico",
    {
        "hospitalId": fields.Integer(required=True, description="ID del hospital"),
        "calendarId": fields.String(
            required=True, description="ID del calendar asignado a un medico y su sede"
        ),
    },
)

turnos_paciente = api_turnos.model(
    "TurnosPaciente",
    {
        "hospitalId": fields.Integer(required=True, description="ID del hospital"),
        "email": fields.String(
            required=True, description="Correo electrónico del usuario"
        ),
    },
)

check_available = api_turnos.model(
    "CheckAvailable",
    {
        "hospitalId": fields.Integer(required=True, description="ID del hospital"),
        "calendarId": fields.String(
            required=True, description="ID del calendar asignado a un medico y su sede"
        ),
        "turnoId": fields.String(
            required=True, description="ID del evento para cancelar"
        ),
    },
)


@api_turnos.route("/schedules/", methods=["PUT"])
class Schedules(Resource):
    @api_turnos.expect(turnos_medico)
    @api_turnos.doc(body=turnos_medico, security="apikey")
    @jwt_required
    def put(self):
        """
        GET AVAILABLE APPOINTMENTS BY CALENDAR ID
        """
        # verify user
        hospitalId = api_turnos.payload.get("hospitalId")
        calendarId = api_turnos.payload.get("calendarId")
        return get_dates(calendarId, hospitalId)


@api_turnos.route("/cancel/", methods=["POST"])
class Cancel(Resource):
    @api_turnos.doc("cancel_turno", security="apikey")
    @api_turnos.expect(upload_parser)
    @jwt_required
    def post(self):
        """
        CANCEL APPOINTMENT
        """
        args = upload_parser.parse_args()
        calendarId = args.get("calendarId")
        hospitalId = args.get("hospitalId")
        eventText = args.get("eventText")
        turnoId = args.get("turnoId")
        cancel_appointment(calendarId, turnoId, hospitalId, eventText)
        return 200


@api_turnos.route("/booking/", methods=["POST", "PUT"])
class Booking(Resource):
    @api_turnos.doc("book an appointment", security="apikey")
    @api_turnos.expect(upload_parser)
    @jwt_required
    def post(self):
        """
        BOOK AN APPOINTMENT
        """
        args = upload_parser.parse_args()
        calendarId = args.get("calendarId")
        hospitalId = args.get("hospitalId")
        eventText = args.get("eventText")
        turnoId = args.get("turnoId")
        book_event(calendarId, turnoId, eventText, hospitalId)
        return 200

    @api_turnos.doc("check availability", security="apikey")
    @api_turnos.expect(check_available)
    @jwt_required
    def put(self):
        """
        CHECK AVAILABILITY
        """
        calendarId = api_turnos.payload.get("calendarId")
        hospitalId = api_turnos.payload.get("hospitalId")
        turnoId = api_turnos.payload.get("turnoId")
        return check_availability(calendarId, turnoId, hospitalId)


@api_turnos.route("/patients/", methods=["PUT"])
class Patients(Resource):
    @api_turnos.doc("get available appointments", security="apikey")
    @api_turnos.expect(turnos_paciente)
    @jwt_required
    def put(self):
        """
        GET MY APPOINTMENTS
        """
        email = api_turnos.payload.get("email")
        hospitalId = api_turnos.payload.get("hospitalId")
        return find_my_appointments(email, hospitalId)
