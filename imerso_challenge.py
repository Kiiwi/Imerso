'''
Simple backend and API using Flask
'''

from flask import Flask
from flask_restplus import Api, Resource, fields

app = Flask(__name__)
api = Api(app, title='Imerso Software Challenge', description='Simple backend and API using Flask')

ns = api.namespace('Imerso Software Challenge', description='Simple API using Flask')


scan = api.model('Scan', {
    'id': fields.Integer(readOnly=True,
    description='The scan unique identifier'),
    'points': fields.List(fields.String, required=True,
    description='The points are represented as an array of arrays where each sub array contains the x, y, z coordinates of each point',
    example='[5.0, 7.0, -3.4],' + 
            '[8.0, 5.0 ,2.2],' + 
            '[10.0, 12.0, 6],' +
            '[15.1, 9.2, 2.2],' +
            '[9.3, 10.2, 3.1]'),
    'bounding_box': fields.List(fields.String, readOnly=True,
    description='The bounding box is a box surrounding the points and is represented by the distances between the faces of the box in the x, y and z direction',
    example='[10.1, 7.0, 9.4]'
    ),
    "center": fields.List(fields.String, readOnly=True,
    description='The center point of the bounding box',
    example='[10.05, 8.5, 1.3]')
})


class ScanObject(object):
    def __init__(self):
        self.counter = 0
        self.scans = []


    def get(self, id):
        for scan in self.scans:
            if scan['id'] == id:
                return scan
        api.abort(404, "Scan {} doesn't exist".format(id))

    def create(self, data):
        scan = data
        scan['id'] = self.counter = self.counter + 1
         
        def bounding_box(data):
            x_values = []
            y_values = []
            z_values = []
            for i in range(len(data['points'])):
                x_values.append(data['points'][i][0])
                y_values.append(data['points'][i][1])
                z_values.append(data['points'][i][2])
            bounding_box_x = max(x_values) - min(x_values)
            bounding_box_y = max(y_values) - min(y_values)
            bounding_box_z = max(z_values) - min(z_values)

            center_x = min(x_values) + (bounding_box_x / 2.0)
            center_y = min(y_values) + (bounding_box_y / 2.0)
            center_z = min(z_values) + (bounding_box_z / 2.0)
            return [bounding_box_x, bounding_box_y, bounding_box_z], [center_x, center_y, center_z]
        
        scan['bounding_box'], scan['center'] = bounding_box(scan)
 
        self.scans.append(scan)
        return scan#, bounding_box(scan)

    def update(self, id, data):
        scan = self.get(id)
        scan.update(data)
        return scan

Scans = ScanObject()

# Test Data
Scans.create({
    "points": [
  [5.0, 7.0, -3.4],
  [8.0, 5.0 ,2.2],
  [10.0, 12.0, 6],
  [15.1, 9.2, 2.2],
  [9.3, 10.2, 3.1]]
})
Scans.create({
    "points": [
  [-5.0, -7.0, 3.4],
  [-8.0, -5.0 ,-2.2],
  [-10.0, -12.0, -6],
  [-15.1, -9.2, -2.2],
  [-9.3, -10.2, -3.1]]
})
Scans.create({
    "points": [
  [1.4, 5.6, -2.1],
  [9.5, 5.0 ,2.2],
  [10.0, 21.3, 6],
  [15.1, 9.2, 2.2],
  [9.3, 10.2, 11.8]]
})




@ns.route('/scans')
class ScanList(Resource):
    '''Shows a list of all scans, and lets you POST to add new scans'''
    @ns.doc('list_scans')
    @ns.marshal_with(scan)
    def get(self):
        '''List all scans'''
        return Scans.scans

    @ns.doc('create_scan')
    @ns.expect(scan)
    @ns.marshal_with(scan, code=201)
    def post(self):
        '''Create a new scan'''
        return Scans.create(api.payload), 201


@ns.route('/scans/<int:id>')
@ns.response(404, 'Scan not found')
@ns.param('id', 'The scan identifier')
class Scan(Resource):
    '''Show a single scan item'''
    @ns.doc('get_scan')
    @ns.marshal_with(scan)
    def get(self, id):
        '''Get a single scan given its identifier'''
        return Scans.get(id)


    @ns.expect(scan)
    @ns.marshal_with(scan)
    def put(self, id):
        '''Update a scan given its identifier'''
        return Scans.update(id, api.payload)


@ns.route('/scans/<int:id>/boundingbox')
@ns.response(404, 'Scan not found')
@ns.param('id', 'The scan identifier')
class BoundingBox(Resource):
    '''Show a single bounding box'''
    @ns.doc('get_bounding_box')
    @ns.marshal_with(scan, mask='bounding_box, center')
    def get(self, id):
        ''''Get bounding box given the scan identifier'''
        return Scans.get(id)

if __name__ == '__main__':
    app.run(debug=True)