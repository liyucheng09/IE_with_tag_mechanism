import grouper
import dltk
import sys
from grouper import formatter
import tensorflow
import pandas as pd
from graphviz import Digraph
import streamlit as st
import os
os.environ["PATH"] += os.pathsep + r'C:\Program Files\Graphviz\bin'

st.write('# 中文信息抽取')

model_file='./model/model.pb'
map_file='./model/maps.pkl'


@st.cache(hash_funcs={'_thread.RLock' : lambda _: None,
                '_thread.lock' : lambda _: None,
                'builtins.PyCapsule': lambda _: None,
                '_io.TextIOWrapper' : lambda _: None,
                'builtins.weakref': lambda _: None,
                'builtins.dict' : lambda _:None})
def get_model():
    return dltk.load_model(map_file=map_file,model_file=model_file)


def predict(sentences, model):
    tags = model.predict(sentences)

    tags = [formatter(tag) for tag in tags]

    return tags


model=get_model()

st.write('## 请输入文本：单句、多句（需要使用`|`分隔每个输入句子）。')

output_type=st.radio("输出形式“",("表格", "json"))

text_input=st.text_input("INPUT", value='乔布斯于1979年创立了苹果公司。|苹果公司是市值最高的公司。')
if '|' in text_input:
    sentences = text_input.split('|')
else:
    setences=[text_input]

tags=predict(sentences, model)
result=[]
grouper.extract(sentences,tags,result)
result_=[]
for i in result:
    result_.extend(i)

st.write('## 输出')
if output_type == 'json':
    st.json(result)
elif output_type == '表格':

    st.table(
        pd.DataFrame(result_)
    )

st.write('## 生成知识图谱')

edges=[]
for i in result_:
    if i['object'] != '_' and i['subject'] != '_' :
        edges.append(
            ('-'.join(i['subject']), '-'.join(i['object']), i['predicate'])
        )
g=Digraph()
g.attr('node', fontname="Fangsong")
g.attr('edge', fontname="Fangsong")
for edge in edges:
    print(edge)
    g.edge(*edge)
# g.view()
st.graphviz_chart(g)