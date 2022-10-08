from flask import *
from flask_mysqldb import MySQL
import random
import os
import dotenv
from twilio.rest import Client

app = Flask(__name__)

app.secret_key = 'qazwsxedcrfvtgbyhnujmiklop123456'

app.config['MYSQL_HOST'] = "bll6rxbmrx78s6i1xgr2-mysql.services.clever-cloud.com"
app.config['MYSQL_USER'] = 'unzcpyamk9tfvpfx'
app.config['MYSQL_PASSWORD'] = 'ug5QtkyFF113DmviwdcU'
app.config['MYSQL_DB'] = 'bll6rxbmrx78s6i1xgr2'
app.config['MYSQL_DATABASE_URI'] = "mysql://unzcpyamk9tfvpfx:ug5QtkyFF113DmviwdcU@bll6rxbmrx78s6i1xgr2-mysql.services.clever-cloud.com:3306/bll6rxbmrx78s6i1xgr2"


mysql = MySQL(app)

@app.route('/')
def home():

    cur = mysql.connection.cursor()
    cur.execute('''SELECT *  FROM police_stations_table''')
    ps_list = cur.fetchall()
    list1 = []
    uniques = []

    for i in range(len(ps_list)):
        count = list1.count(ps_list[i][4])
        if count == 0:
            uniques.append(ps_list[i][4])
            list1.append(ps_list[i][4])

    mysql.connection.commit()
    cur.close()

    return render_template("enter_number.html",uniques=uniques)


@app.route('/handle_data',methods=['POST'])
def handle_data():

    p_number = "+91" + request.form['phonenumber']
    val = getOtpApi(p_number)
    district = request.form["district"]
    session['district'] = district

    if val:
        return render_template("enter_otp.html")
    else:
        flash("There was error please try again")
        return redirect ("enter_number.html")

@app.route("/validate_otp",methods=["POST"])
def validate_otp():
    otp = request.form['Otp']
    if "response" in session:
        s = session['response']
        session.pop('response',None)
        if s == otp:
            return redirect("/load_police_stations")
        else:
            flash("Authentication not succesful")

            cur = mysql.connection.cursor()
            cur.execute('''SELECT *  FROM police_stations_table''')
            ps_list = cur.fetchall()
            list1 = []
            uniques = []

            for i in range(len(ps_list)):
                count = list1.count(ps_list[i][4])
                if count == 0:
                    uniques.append(ps_list[i][4])
                    list1.append(ps_list[i][4])

            mysql.connection.commit()
            cur.close()

            return render_template("enter_number.html",uniques=uniques)

@app.route('/resendOTP',methods = ['POST'])
def resendOTP():
    return redirect("/")

@app.route('/load_police_stations')
def load_police_stations():

    cur = mysql.connection.cursor()
    cur.execute('''SELECT *  FROM police_stations_table''')
    ps_list = cur.fetchall()
    list1 = []

    for i in range(len(ps_list)):
        if session["district"]==ps_list[i][4]:
            list1.append(ps_list[i][1])

    return render_template("user_form.html",list1=list1)

@app.route('/insert_user_feedback',methods=["POST"])
def insert_user_feedback():

    police_station_name = request.form.get("police_station_name")
    question_1 = request.form.get("question_1")
    question_2 = request.form.get("question_2")
    paragraph = request.form.get("paragraph")
    district = session["district"]

    list1 = paragraph.split(" ")
    if len(list1)>300:
        flash("Limit of 300 words exceeded!!")
        return redirect('/load_police_stations')

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO user_feedback_table(question_1, question_2,  "
                "paragraph, police_station_name, district) VALUES "
                "(%s, %s, %s, %s, %s)",
                (question_1, question_2, paragraph, police_station_name, district))

    mysql.connection.commit()
    cur.close()

    return render_template("done.html")


def generateOTP():
    return random.randrange(100000,999999)

def getOtpApi(p_number):
    account_sid = 'AC5b6de0bce3f5033b476efac822d6e4a1'
    auth_token = os.environ.get('AUTH_TOKEN')
    OTP = generateOTP()
    print(OTP)
    body = "Your otp is" + str(OTP)
    session['response'] = str(OTP)
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body = body,
        from_= '+12202205492',
        to=p_number)

    if message.sid:
        return True
    else:
        return False

if __name__ == '__main__':
    app.run(debug=True)
