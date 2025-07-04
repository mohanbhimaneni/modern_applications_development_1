from flask import Flask, render_template, request
import matplotlib.pyplot as plt

app=Flask(__name__,template_folder='templates/')

@app.route('/',methods=['GET','POST'])
def home():

    if request.method == 'GET':
        return render_template("index.html")
    
    elif request.method == 'POST':

        # start taking input from data.csv
        v=[]
        with open('data.csv','r') as f:
            v=list(f)
        values=[]
        for val in v:
            tempList=val.split(',')
            for i in range(len(tempList)):
                tempList[i]=str(tempList[i]).strip()
                try:
                    tempList[i]=int(tempList[i])
                except:
                    pass
            values.append(tempList)
        # end taking input from data.csv
        # result is stored in "values"

        # Start handling form requests
        iD=request.form['ID']
        iD_value=request.form['id_value']

        # Start checking for constraints
        if iD not in ['student_id','course_id']:
            return render_template('error.html')
        else:
            valid=False
            if iD=='student_id':
                for val in values:
                    if int(iD_value)==val[0]:
                        valid=True
                if not valid:
                    return render_template('error.html')
            else:
                for val in values:
                    if int(iD_value)==val[1]:
                        valid=True
                if not valid:
                    return render_template('error.html')
        # End checking for constraints

        # Start generating results and redirecting corresponding results
        result=[]
        if iD=='student_id':
            total=0
            for val in values:
                if val[0]==int(iD_value):
                    result.append(val)
                    total+=val[-1]
            return render_template('student_data.html',res=result,total=total,len=len)
        else:
            s=0
            saved_values=[]
            for val in values:
                if val[1]==int(iD_value):
                    saved_values.append(val[-1])
                    s+=val[-1]
            avg=round(s/len(saved_values),1)
            plt.hist(saved_values)
            plt.xlabel('Marks')
            plt.ylabel('Frequency')
            plt.savefig('static/hist.png', bbox_inches='tight')
            plt.close()
            return render_template('course_data.html',average_marks=avg,maximum_marks=max(saved_values),image='static/hist.png')
        # End generating results and redirecting corresponding results

        # End handling form requests
    
if __name__=='__main__':
    app.run()