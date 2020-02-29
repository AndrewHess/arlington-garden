from flask import Flask, render_template, request, session, redirect, url_for, flash
import os, csv, mysql.connector, hashlib, uuid, json
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
        return redirect(url_for('dashboard'))

    else:
        flash('Invalid Login Information')
        return redirect('/')


#----------------SUBMITTING THE FORM--------
@app.route('/data', methods = ['GET', 'POST'])
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

    conn.insert_row('visitor_info_v2', all_data)
    
    
    return redirect('/')
    
    
#---------------DASHBOARD----------
def collect(conn, options, query):
    '''
        options = list of options from survey form that pertain to query
        query = string
    '''
    count = {}
    for o in options:
        count[o] = conn.select_count('visitor_info_v2', query, o)
    return count
    

@app.route('/dashboard', methods = ['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect('/')

    conn = c.Connector()
    
    first_time = ['yes', 'no'];
    attend_reason = ['learning about plants',
                     'saw an ad',
                     'rest/relax',
                     'children away from screens',
                     'entertainment',
                     'picnic',
                     'connect with nature',
                     'bird watching',
                     'from out of town',
                     'free community resource',
                     'famliy activity',
                     'photography',
                     'bring a child',
                     'friend brought me',
                     'other'];
    rating = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    water_conserving = ['none', 'some', 'high'];
    knew_about = ['yes', 'no'];
    how_heard_about = ['website',
                       'online',
                       'newspaper',
                       'magazine',
                       'drove_by',
                       'word_of_mouth',
                       'social_media',
                       'always_knew_about',
                       'other'];
    post_social = ['yes', 'no'];
    get_involved = ['newsletter',
                    'donation',
                    'photography_permit',
                    'volunteer',
                    'marmalade',
                    'facebook',
                    'other']
    gender = ['male', 'female', 'no answer'];
    income = ['below 20',
              '20-40',
              '40-60',
              '60-75',
              '75-100',
              'above 100',
              'no answer'];
    ethnicities = ['caucasian',
                   'african-american',
                   'asian/pacific islander',
                   'hispanic/latino/chicano',
                   'native-american/alaskan native',
                   'other'];
    
    # Count the number of occurances of values in the table. The third
    # argument to collect() must match the row name of the database being
    # queried.
    first_time_count = collect(conn, first_time, 'FirstTime');
    attend_reason_count = collect(conn, attend_reason, 'Reason');
    rating_count = collect(conn, rating, 'Rating');
    water_conserving_count = collect(conn, water_conserving, 'AppreciationIncrease');
    knew_about_count = collect(conn, knew_about, 'KnewAbout');
    how_heard_about_count = collect(conn, how_heard_about, 'HowHeardAbout');
    post_social_count = collect(conn, post_social, 'SocialMediaPosted');
    get_involved_count = collect(conn, get_involved, 'GetInvolved');
    gender_count = collect(conn, gender, 'Gender');
    income_count = collect(conn, income, 'Income');
    ethn_count = collect(conn, ethnicities, 'Ethnicity');

    questions = json.dumps({'first_time': first_time_count,
                            'attend_reason': attend_reason_count,
                            'rating': rating_count,
                            'water_conserving': water_conserving_count,
                            'knew_about': knew_about_count,
                            'how_heard_about': how_heard_about_count,
                            'post_social': post_social_count,
                            'get_involved': get_involved_count,
                            'gender': gender_count,
                            'income': income_count,
                            'ethnicity': ethn_count});
    print(ethn_count)
    return render_template('dashboard.html', questions = questions)





#--------------RUNNING APP--------------
if __name__ == '__main__':
    app.debug = True
    app.run()


