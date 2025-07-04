import sys
from jinja2 import Template
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

var=sys.argv
res=[]
if len(var)!=3:
    validity=0
elif var[1]!='-c' and var[1]!='-s':
    validity=0
else:
    df=pd.read_csv("data.csv")
    df.columns=list(map(lambda x: str.strip(x),df.columns))
    val=df.values
    res=[]
    if var[1]=='-s':
        sid=int(var[2])
        if sid not in list(df['Student id']):
            validity=0
        else:
            validity=1
            tot=0
            res.append(['Student id','Course id','Marks'])
            for v in val:
                if sid==v[0]:
                    res.append(list(v))
                    tot+=int(v[-1])
            res.append(['Total Marks','',tot])
    elif var[1]=='-c':
        cid=int(var[2])
        res=[]
        if cid not in list(df['Course id']):
            validity=0
        else:
            validity=-1
            marks=[]
            for v in val:
                if v[1]==cid:
                    marks.append(v[2])
            m=max(marks)
            avg=np.average(marks)

            res.extend([['Average Marks','Maximum Marks'],[avg,m]])
            plt.hist(marks)
            plt.xlabel('Marks')
            plt.ylabel('Frequency')
            plt.savefig('hist.png', bbox_inches='tight')
            
                    
            

TEMPLATE="""
<!DOCTYPE html>
<html>
    <head>
        <title>
            {% if validity==1 %}
                Student Data
            {% elif validity==-1 %}
                Course Data
            {% else %}
                Something went wrong
            {% endif %}
        </title>
    </head>

    <body>
        <h1>
            {% if validity==1 %}
                Student Details
            {% elif validity==-1 %}
                Course Details
            {% else %}
                Wrong Inputs
            {% endif %}
        </h1>
        {% if validity==1 %}
            <table border='solid'>
                <tr>
                    <th>{{res[0][0]}}</th>
                    <th>{{res[0][1]}}</th>
                    <th>{{res[0][2]}}</th>
                </tr>
                {% for r in range(1,len(res)-1) %}
                    <tr>
                        <td>{{res[r][0]}}</td>
                        <td>{{res[r][1]}}</td>
                        <td>{{res[r][2]}}</td>
                    </tr>
                {% endfor %}
                <tr>
                    <td colspan='2'>{{res[-1][0]}}</td>
                    <td>{{res[-1][-1]}}</td>
                </tr>
            </table>
        {% elif validity==-1 %}
            <table border='solid'>
                <tr>
                    <th>{{res[0][0]}}</th>
                    <th>{{res[0][1]}}</th>
                </tr>
                <tr>
                    <td>{{res[1][0]}}</th>
                    <td>{{res[1][1]}}</th>
                </tr>
            </table>
            <img src='hist.png' alt='Histogram of marks'>
        {% else %}
            <p>Something went wrong</p>
        {% endif %}
    </body>
</html>
"""

t=Template(TEMPLATE)

with open("output.html", "w", encoding="utf-8") as f:
    f.write(t.render(var=var,res=res,validity=validity,len=len))