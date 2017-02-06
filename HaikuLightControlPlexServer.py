from flask import Flask, request, jsonify
from requests_toolbelt.multipart import decoder
import json
from pprint import pprint

#Import Haiku library
from sensemefan import SenseMeFan

app = Flask(__name__)

@app.route('/api/add_message/<uuid>', methods=['GET', 'POST'])
def add_message(uuid):

   #app.logger.debug("JSON received...")
   #app.logger.debug(request.json)

   # Gets the entire RAW data and prints it. JSON section is defined as "Content-Type: application/json"
   #content = request.get_data()

   # Start of semi-working code, this cuts off the event JSON value though
   payload = request.values.get('payload')
   # Converts the data back into JSON format to easily seperate out values
   json_data = json.loads(payload)
  
   # Breakout important data from the JSON
   username = json_data["Account"]["title"]
   server = json_data["Server"]["title"]
   player = json_data["Player"]["title"]
   player_uuid = json_data["Player"]["uuid"]
   
   print "Username: " + username
   print "Server: " + server
   print "Player: " + player
   print "Player UUID: " + player_uuid
   print "End!"
  
   if username == 'dcplaya':
    	# Statically assign the fan? Probably not, but you would do it this way:
    	# fan = SenseMeFan('192.168.1.112', 'Living Room Fan')
    	fan = SenseMeFan('10.10.1.117', 'Drew\'s Room Fan', 'FAN', 'LSERIES')

       	# Get Light level
    	light = fan.getlight()
   	print(light)
	print "Success!"

   return jsonify({"uuid":uuid})

if __name__ == '__main__':
    app.run(host= '0.0.0.0', port=8088, debug=True)
