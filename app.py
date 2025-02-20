from flask import Flask, render_template, request, session, redirect, url_for, flash
import os, csv, mysql.connector, hashlib, uuid, json
import connector as c
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(32)

table_name = 'visitor_info'

#---------HOME PAGE--------------
@app.route('/')
def root():
    qr_id = request.args.get('qr_id')
    if qr_id is None:
        qr_id = '0'
    session['qr_id'] = qr_id

    if 'username' in session:
        return render_template('survey.html', login=True )
    return render_template('survey.html', login=False)

#----------LOG OUT----------------
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    session.pop('username')
    return redirect(url_for('root'))
    
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

@app.route('/authenticate', methods = ['POST'])
def authenticate():
    input_username = request.form['username']
    input_password = request.form['password']
    this_admin = Admin_Login()

    if (this_admin.check_password(input_password) and
        this_admin.check_username(input_username)):
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

    stood_out = request.form['stood_out']
    first_time = request.form['first_time']
    attend_reason = ' '.join(request.form.getlist('attend_reason'))
    disap = request.form['disappointing']
    rating = request.form['rating']
    water = request.form['water_conserving']
    knew_about = request.form['knew_about']
    heard_about = ' '.join(request.form.getlist('heard_about'))
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

    cols = ('FirstTime', 'Reason', 'StoodOut', 'Disappointing', 'Rating',
            'AppreciationIncrease', 'KnewAbout', 'HowHeardAbout',
            'SocialMediaPosted', 'SocialMediaPlatform', 'TopicInterests',
            'GetInvolved', 'Gender', 'AdultAges', 'ChildAges', 'Zip',
            'Income', 'Ethnicity', 'QRCode')

    conn.insert_row(table_name, cols, all_data)
    
    return redirect(url_for('root'))

@app.route('/get_data_selection', methods = ['GET', 'POST'])
def get_data_selection():
  days = float(request.form['time_number'])
  timeframe = request.form['time_type']

  if timeframe == 'weeks':
    days *= 7
  elif timeframe == 'months':
    days *= 30
  elif timeframe == 'years':
    days *= 365

  # Filter the day with this timeframe. This filter assumes that the timestamp
  # field in the database is named 'timestamp'.
  time_filter = f'timestamp >= DATE(NOW()) - INTERVAL {days} DAY'

  return dashboard(suffix=time_filter)
    
    
#---------------DASHBOARD----------
def collect(conn, options, query):
    '''
        options = list of options from survey form that pertain to query
        query = string
    '''
    count = {}
    for o in options:
        count[o] = conn.select_count(table_name, query, o)
    return count
    

@app.route('/dashboard', methods = ['GET', 'POST'])
def dashboard(suffix=None):
    if 'username' not in session:
        return redirect(url_for('root'))

    conn = c.Connector()
    conn.add_suffix(suffix)

    # Selecting all text responses 
    social_media_plat = conn.select_column('SocialMediaPlatform', table_name)
    print("\n\n")
    print(social_media_plat)
    stoodout = conn.select_column('StoodOut', table_name)
    disappointing = conn.select_column('Disappointing', table_name)
    topic_interests = conn.select_column('TopicInterests', table_name)
    adult_ages = conn.select_column('AdultAges', table_name)
    child_ages = conn.select_column('ChildAges', table_name)
    zip_code = conn.select_column('Zip', table_name)

    # Selecting radio button, checkboxes, or dropdown responses 
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
    week_day = ['Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday',
                'Sunday'];

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
    week_day_count = collect(conn, week_day, 'DAYNAME(Timestamp)');

    questions = json.dumps({'FirstTime': first_time_count,
                            'Reason': attend_reason_count,
                            'Rating': rating_count,
                            'AppreciationIncrease': water_conserving_count,
                            'KnewAbout': knew_about_count,
                            'HowHeardAbout': how_heard_about_count,
                            'SocialMediaPosted': post_social_count,
                            'GetInvolved': get_involved_count,
                            'Gender': gender_count,
                            'Income': income_count,
                            'Ethnicity': ethn_count,
                            'SubmissionDay': week_day_count,
                            'StoodOut': stoodout,
                            'Disappointing': disappointing,
                            'SocialMediaPlatform': social_media_plat,
                            'AdultAges': adult_ages,
                            'ChildAges': child_ages,
                            'Zip': zip_code,
                            'TopicInterests': topic_interests});
    
    response_count = conn.select_num_rows(table_name)
    others = json.dumps(conn.select_other_responses(table_name, ['GetInvolved', 'Reason',
                                                 'HowHeardAbout',
                                                 'Ethnicity']))

    return render_template('dashboard.html', questions = questions,
                           others = others, response_count = response_count)






#--------------RUNNING APP--------------
if __name__ == '__main__':
    app.debug = True
    app.run()


