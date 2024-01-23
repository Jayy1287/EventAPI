from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

USER_DATA = {
    "admin": "NicePassword"
}

@auth.verify_password
def verify(username, password):
	if not (username and password):
		return False
	return USER_DATA.get(username) == password

class VideoModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	date = db.Column(db.Integer, nullable=False)
	location = db.Column(db.String(100), nullable=False)
	capacity = db.Column(db.Integer, nullable=False)
	currentCapacity = db.Column(db.Integer, nullable=False)

	def __repr__(self):
		return f"Event(name = {self.name}, date = {self.date}, location = {self.location}, capacity = {self.capacity}, currentCapacity = {self.currentCapacity})"

class AttendeeModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	event = db.Column(db.Integer, nullable=True)

	def __repr__(self):
		return f"Attendee(name = {self.name}, event = {self.event})"


# db.create_all()

video_put_args = reqparse.RequestParser()
video_put_args.add_argument("name", type=str, help="Name of the video is required", required=True)
video_put_args.add_argument("date", type=int, help="Date of the event is required", required=True)
video_put_args.add_argument("location", type=str, help="Location of the event is required", required=True)
video_put_args.add_argument("capacity", type=int, help="Capacity of the event is required", required=True)
video_put_args.add_argument("currentCapacity", type=int, help="Current capacity of the event is required", required=True)

video_update_args = reqparse.RequestParser()
video_update_args.add_argument("name", type=str, help="Name of the event is required")
video_update_args.add_argument("date", type=int, help="Date of the event")
video_update_args.add_argument("location", type=str, help="Location of the event is required")
video_update_args.add_argument("capacity", type=int, help="Capacity of the event is required")
video_update_args.add_argument("currentCapacity", type=int, help="Current capacity of the event is required")

attendee_put_args = reqparse.RequestParser()
attendee_put_args.add_argument("name", type=str, help="Name of the attendee is required", required=True)
attendee_put_args.add_argument("event", type=int, help="Date of the event is required", required=False)

attendee_update_args = reqparse.RequestParser()
attendee_update_args.add_argument("name", type=str, help="Name of the attendee is required", required=True)
attendee_update_args.add_argument("event", type=int, help="Date of the event is required", required=False)


resource_fields = {
	'id': fields.Integer,
	'name': fields.String,
	'date': fields.Integer,
	'location': fields.String,
	'capacity': fields.Integer,
	'currentCapacity': fields.Integer

}

resource_fields_attendee = {
	'id': fields.Integer,
	'name': fields.String,
	'event': fields.Integer

}



######################################## event ########################################
class Video(Resource):
    
	#register an event
	@auth.login_required
	@marshal_with(resource_fields)
	def get(self, video_id):
		result = VideoModel.query.filter_by(id=video_id).first()
		if not result:
			abort(404, message="Could not find event with that id")
		return result

	#update an event
	@auth.login_required
	@marshal_with(resource_fields)
	def put(self, video_id):
		args = video_put_args.parse_args()
		result = VideoModel.query.filter_by(id=video_id).first()
		if result:
			abort(409, message="Event id taken...")

		video = VideoModel(id=video_id, name=args['name'], date=args['date'], location=args['location'], capacity=args['capacity'], currentCapacity=args['currentCapacity'])
		db.session.add(video)
		db.session.commit()
		return video, 201

	#update an event, updatind capacity and currentCapacity happens here
	@auth.login_required
	@marshal_with(resource_fields)
	def patch(self, video_id):
		args = video_update_args.parse_args()
		result = VideoModel.query.filter_by(id=video_id).first()
		if not result:
			abort(404, message="Event doesn't exist, cannot update")

		if args['name']:
			result.name = args['name']
		if args['date']:
			result.date = args['date']
		if args['location']:
			result.location = args['location']
		if args['capacity']:
			result.capacity = args['capacity']
		if args['currentCapacity']:
			if args['currentCapacity'] > result.capacity:
				abort(409, message="Event is full...")
			result.currentCapacity = args['currentCapacity']

		db.session.commit()

		return result

	#delete an event
	@auth.login_required
	@marshal_with(resource_fields)
	def delete(self, video_id):
		result = VideoModel.query.filter_by(id=video_id).first()
		if not result:
			abort(404, message="Video doesn't exist, cannot delete")
		db.session.delete(result)
		db.session.commit()
		return '', 204



################################### attendee ####################################
class Attendee(Resource):
    
    #get an attendee
	@auth.login_required
	@marshal_with(resource_fields_attendee)
	def get(self, attendee_id):
		result = AttendeeModel.query.filter_by(id=attendee_id).first()
		if not result:
			abort(404, message="Could not find attendee with that id")
		return result

	#register an attendee
	@auth.login_required
	@marshal_with(resource_fields_attendee)
	def put(self, attendee_id):
		args = attendee_put_args.parse_args()
		result = AttendeeModel.query.filter_by(id=attendee_id).first()
		if result:
			abort(409, message="Attendee id taken...")
		if args['event']:
			check = VideoModel.query.filter_by(id=args['event']).first()
			if check.currentCapacity == check.capacity:
				abort(409, message="Event is full...")
			check.currentCapacity = check.currentCapacity + 1
		attendee = AttendeeModel(id=attendee_id, name=args['name'], event=args['event'])
		db.session.add(attendee)
		db.session.commit()
		return attendee, 201

	#update an attendee, register or unregister happens here. Leave event empty to unregister.
	@auth.login_required
	@marshal_with(resource_fields_attendee)
	def patch(self, attendee_id):
		args = attendee_update_args.parse_args()
		result = AttendeeModel.query.filter_by(id=attendee_id).first()
		if not result:
			abort(404, message="Attendee doesn't exist, cannot update")

		if args['name']:
			result.name = args['name']
		if args['event']:
			if result.event != 0:
				
				check = VideoModel.query.filter_by(id=args['event']).first()
				if not check:
					abort(404, message="Event doesn't exist, cannot update...")
				if check.currentCapacity == check.capacity:
					abort(409, message="Event is full...")
				check.currentCapacity = check.currentCapacity + 1

				check2 = VideoModel.query.filter_by(id=result.event).first()
				if check2:
					check2.currentCapacity = check2.currentCapacity - 1
    
				result.event = args['event']
			else:
				abort(409, message="Attendee is already registered for an event...")
	
		if args['event'] == None:
			if result.event != 0:
				check = VideoModel.query.filter_by(id=result.event).first()
				if not check:
					abort(404, message="Event doesn't exist, cannot update.")	
				check.currentCapacity = check.currentCapacity - 1
				result.event = None
			else:
				abort(409, message="Attendee is not registered for an event...")
		

		db.session.commit()

		return result

	#delete an attendee
	@auth.login_required
	@marshal_with(resource_fields_attendee)
	def delete(self, attendee_id):
		result = AttendeeModel.query.filter_by(id=attendee_id).first()
		if not result:
			abort(404, message="Attendee doesn't exist, cannot delete")
		check = VideoModel.query.filter_by(id=result.event).first()
		if check:	
			check.currentCapacity = check.currentCapacity - 1
		db.session.delete(result)
		db.session.commit()
		return '', 204


################################################
##Find all attendees of a given event
class FindAttendees(Resource):
    
	@auth.login_required
	@marshal_with(resource_fields_attendee)
	def get(self, event_id):
		result = AttendeeModel.query.filter_by(event=event_id).all()
		if not result:
			abort(404, message="Could not find attendees in that event")
		return result


#################################################################
##List all events 
class ListEvents(Resource):
    
	@auth.login_required
	@marshal_with(resource_fields_attendee)
	def get(self):
		result = VideoModel.query.all()
		if not result:
			abort(404, message="There are no events")
		return result

############################################
##List all attendees 
class ListAttendees(Resource):
    
	@auth.login_required
	@marshal_with(resource_fields_attendee)
	def get(self):
		result = AttendeeModel.query.all()
		if not result:
			abort(404, message="There are no attendees")
		return result
##########################################


api.add_resource(Video, "/video/<int:video_id>")
api.add_resource(Attendee, "/attendee/<int:attendee_id>")
api.add_resource(FindAttendees, "/findAttendees/<int:event_id>")
api.add_resource(ListEvents, "/listEvents")
api.add_resource(ListAttendees, "/listAttendees")



if __name__ == "__main__":
	app.run(debug=True)