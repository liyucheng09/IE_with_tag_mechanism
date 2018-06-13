import json
from flask import Flask,request,jsonify
from flask_script import Manager
from grouper import formatter,grouper
from predict import predict


app=Flask(__name__)
app.config['JSON_AS_ASCII']=False
manager=Manager(app)
g=grouper()

@app.route('/')
def index():
	return '<h1>hello world!</h1>'

@app.route('/ie'):
def ie():
	sentence = request.args.get('sentence')

	i=get_ie(sentence)

	if len(i)!=0:
		return jsonify(i)

def get_ie(sentence):

	tag=predict([sentence])

	g.sentence=sentence
	g.tag=tag[0]

	g.group()
	r , _ =g.output()

	return r

if __name__ == '__main__':

	manager.run()