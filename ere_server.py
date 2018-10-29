from flask import Flask, request, jsonify
import predict
import grouper

app = Flask(__name__)
app.config['JSON_AS_ASCII']=False


HOST = "0.0.0.0"
PORT = 8010
DEBUG = False

def get_result_list(s,post):
    result=[]
    if post:
        sentences=s.split('\n')
        tags=predict.predict(sentences)
    #    print(tags)
        grouper.extract(sentences,tags,result)
    else:
        sentences=s.split('|')
    #    print(sentences)
        tags=predict.predict(sentences)
    #    print(tags)
        grouper.extract(sentences,tags,result)

    return result

@app.route('/')
def index():
    return '<h1>It works!!</h1>'

@app.route('/ie', methods=['GET', 'POST'])
def ment2ent_api():
    if request.method == 'POST':
        sentence=request.form.get('s')
        sentence=str(sentence).encode('utf-8')
        result=get_result_list(sentence,True)
    else:
        sentence=request.args.get('s')
        result=get_result_list(sentence,False)

    return jsonify(result)


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)