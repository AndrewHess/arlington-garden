from flask import Flask, render_template, request, session, redirect, url_for, flash
import os, csv, mysql.connector, hashlib, uuid
import connector as c
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(32)

#---------HOME PAGE--------------
@app.route('/')
def root():
    qr_id = request.args.get('qr_id')
    if qr_id is None:
        qr_id = '0'
    session['qr_id'] = qr_id
        
    # if 'username' in session:
    #     return redirect(url_for('dashboard')
    return render_template('survey.html')



#------------LOGIN----------------
class Admin_Login:
    username = 'admin'
    pass_key  = '2b8dbbd065f8f91a3852557d3cf32bed9f1802dad369f3589eceb2e571d20ee7:daf84f22f8f24759ac990d897024a740' 

    def hash_password(self, p, key):
        return hashlib.sha256(key.encode() + p.encode()).hexdigest()

    # Used this to create the pass_key above
    def create_pass_key_pair(password):
        key = uuid.uuid4().hex
        self.hash_password(password, key) + ':' + key
    
    def check_password(self, input_password):
        password,key = self.pass_key.split(':')
        return password == self.hash_password(input_password, key)

    def check_username(self, input_username):
        return input_username == self.username

# For now, only have one admin account so make the password "admin"

@app.route('/authenticate', methods = ['POST'])
def authenticate():
    input_username = request.form['username']
    input_password = request.form['password']
    this_admin = Admin_Login()

    if (this_admin.check_password(input_password) and
        this_admin.check_username(input_username)):
        flash('Login Successful')
        session['username'] = input_username
        #return redirect(url_for('dashboard'))

    else:
        flash('Invalid Login Information')
    return redirect('/')


#----------------SUBMITTING THE FORM--------
@app.route('/data', methods = ['POST'])
def data():
    conn = c.Connector()

    # fetching form data
    first_time = request.form['first_time']
    attend_reason = ' '.join(request.form.getlist('attend_reason'))
    stood_out = request.form['stood_out']
    disap = request.form['disappointing']
    rating = request.form['rating']
    water = request.form['water_conserving']
    knew_about = request.form['knew_about']
    heard_about = ' '.join(request.form.getlist('how_heard_about'))
    post_social = request.form['post_social']
    platform_social = request.form['social_platform']
    topic_interests = request.form['topic_interests']
    get_involved = ' '.join(request.form.getlist('get_involved'))
    gender = request.form['gender']
    adult_ages = request.form['adult_ages']
    child_ages = request.form['child_ages']
    zip_code = request.form['zip']
    income = request.form['income']
    ethnicity = ' '.join(request.form.getlist('ethnicity'))
    qr_id = session['qr_id']
    
    
    all_data = (first_time, attend_reason, stood_out,
                disap, rating, water, knew_about, heard_about,
                post_social, platform_social, topic_interests, get_involved, gender,
                adult_ages, child_ages, zip_code,
                income, ethnicity, qr_id)

    conn.insert_row("visitor_info_v2", all_data)
    
    
    return redirect('/')
    
    
    



#--------------RUNNING APP--------------
if __name__ == '__main__':
    app.debug = True
    app.run()


