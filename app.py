from flask import Flask, render_template, request, Response, jsonify
import json
from flask.globals import _request_ctx_stack
import requests
import uuid

print("welcome to mobiquity..!!")

app = Flask(__name__, static_url_path='/static')


ATMS = list()
USERS = [{"username":"pavan", "passwd":"pavan"}]


@app.route('/data_invoke')
def load_data():
    atms = requests.get("https://www.ing.nl/api/locator/atms/").text
    #print(atms)
    fd = json.dumps(atms)
    atms_json = json.loads(fd)[6:]
    #data = json.loads(atms_json)
    print(type(atms_json))
    return atms_json

def get_data():
	# returns JSON object as
	# a dictionary
	f = open('data.json',)
	data = json.load(f)
	f.close()
	return data
	
def update_json(data):
	try:
		with open("data.json", "w") as outfile:
			json.dump(data, outfile)
		return True
	except:
		return False
		

@app.route('/')
def ld():
    data = get_data()
    print(data[0])
    return render_template("index.html", len = len(data), atms = data)


@app.route('/api/atm', methods=['POST','PATCH','DELETE'])
def atm():
	uname  = request.authorization["username"]
	pwd = request.authorization["password"]
	main_fileds=['address','distance','openingHours','functionality','type',]
	address_fileds=['street','housenumber','postalcode','city','geoLocation',]
	geoLocation=['lat','lng']
	openingHours=['dayOfWeek','hours']
	hours=['hourFrom','hourTo']
	sample_data=request.json
	
	print(sample_data)

	validate_mf= validate_fields(main_fileds,sample_data)
	validate_af= validate_fields(address_fileds,sample_data['address'])
	validate_gl= validate_fields(geoLocation,sample_data['address']['geoLocation'])
	for opening_hour in sample_data['openingHours']:
		validate_oh= validate_fields(openingHours,opening_hour)
		print(opening_hour)
		for hour in opening_hour['hours']:
			
			print(hour)
			validate_hs= validate_fields(hours,hour)
	error_fileds= set(validate_mf+validate_af+validate_gl+validate_oh+validate_hs)
	if error_fileds:
		return {'status': 'error','message': f'failed to validate {error_fileds}'}	
		
	if request.method in ['PATCH', 'DELETE']:
		if 'uid' not in sample_data:
			return {'status': 'error','message':f'uid is missing in raw data.'}

	if is_validate_user(uname,pwd):
		print("authenticated")
		data=get_data()
		if request.method == 'POST':
			print ('post')
			sample_data['uid']=str(uuid.uuid4())
			data.append(sample_data)
			operation='Added'
		elif request.method == 'PATCH':
			print ('patch')
			operation='Updated'
			data=find_and_remove(data, sample_data)
			data.append(sample_data)
					
		elif request.method == 'DELETE':
			operation='Deleted'
			data=find_and_remove(data, sample_data)
		
		if update_json(data):
			return {'status': 'success','message':f'{operation} successfully'}
		else:
			return {'status': 'failed','message':f'something went wrong.'}
	else:
		return {'status': 'failed','message':f'authorization failed.'}

def is_validate_user(uname,pwd):
	for user in USERS:
		if (user["username"] == uname) and (user["passwd"] == pwd):
			return True
	else:
		return False
	

def validate_fields(fields,data):
	error_fileds=[]
	for field in fields:
		if field not in data:
			error_fileds.append(field)
	return error_fileds
			 
def find_and_remove(data, input_data):
	for i in data:
		if 'uid' in i and i['uid'] == input_data['uid']:
			print('deleted')
			data.remove(i)
			break
	return data
		


if __name__ == '__main__':
    app.run(use_reloader = True, debug = True)
