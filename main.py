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
		return f"Video(name = {self.name}, date = {self.date}, location = {self.location}, capacity = {self.capacity}, currentCapacity = {self.currentCapacity})"

db.create_all()

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

resource_fields = {
	'id': fields.Integer,
	'name': fields.String,
	'date': fields.Integer,
	'location': fields.String,
	'capacity': fields.Integer,
	'currentCapacity': fields.Integer

}




class Video(Resource):
    
	@auth.login_required
	@marshal_with(resource_fields)
	def get(self, video_id):
		result = VideoModel.query.filter_by(id=video_id).first()
		if not result:
			abort(404, message="Could not find event with that id")
		return result

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

	@auth.login_required
	def delete(self, video_id):
		result = VideoModel.query.filter_by(id=video_id).first()
		if not result:
			abort(404, message="Video doesn't exist, cannot delete")
		db.session.delete(result)
		db.session.commit()
		return '', 204


api.add_resource(Video, "/video/<int:video_id>")

if __name__ == "__main__":
	app.run(debug=True)