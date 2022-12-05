import boto3
from flask import Flask, render_template, request
from pymysql import connections
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'student'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddStd.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.google.com')


@app.route("/addstd", methods=['POST'])
def AddStd():
    studentid = request.form['studentid']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    bloodgroup = request.form['bloodgroup']
    age = request.form['age']
    major = request.form['major']
    email = request.form['email']
    phone = request.form['phone']
    image = request.files['emp_image_file']

    insert_sql = "INSERT INTO STUDENT VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if image.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (studentid, firstname, lastname, bloodgroup, age, major, email, phone))
        db_conn.commit()
        std_name = "" + firstname + " " + lastname

        emp_image_file_name_in_s3 = "studentid" + str(studentid) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=image)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddStdOutput.html', name=std_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
