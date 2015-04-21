# all the imports
import sqlite3,re,json
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from contextlib import closing

# configuration
DATABASE = '/home/flavorshare/mysite/flavorshare.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
CId=2
value=1
entries = []

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def main_page():
    error = None
    if not session.get('logged_in'):
        return render_template('login_or_register.html')
    else :
        return redirect(url_for('homePage'))


@app.route('/', methods=['POST'])
def login_or_register():
    error = None
    if request.method == 'POST':
        if request.form['login_register'] == "Login":
                pageFunctionName='loginPage'
        elif request.form['login_register'] == "Register":
                pageFunctionName='registerPage'
    return redirect(url_for(pageFunctionName))

@app.route('/register')
def registerPage():
    error = None
    return render_template('register.html')

EMAIL_REGEX = re.compile(r"[^@|\s]+@[^@]+\.[^@|\s]+")

@app.route('/register', methods=['POST'])
def register():
    error = None
    if request.method == 'POST':
        if request.form['register'] == "Register":
            if request.form['password'] == request.form['confirm_password'] and EMAIL_REGEX.match(request.form['email']) :
                g.db.execute('insert into users (name, email, password) values (?, ?, ?)',
                         [request.form['name'], request.form['email'], request.form['password']])
                g.db.commit()
                session['username'] = request.form['email']
                session['logged_in'] = True
                flash('Successfully Registered')
                return redirect(url_for('homePage'))
            else :
                flash('Incorrect Details')
                return redirect(url_for('register'))



@app.route('/login')
def loginPage():
    error = None
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['login'] == "Login":
            cur = g.db.execute('select email, password from users where email = \"' + request.form['username'] + '\" and password = \"' + request.form['password'] + '\"')
            user_detail = [row for row in cur.fetchall()]
            print user_detail
            if user_detail:
                print "here"
                flash('Successfully Logged In')
                session['username'] = request.form['username']
                session['logged_in'] = True
                print session['username']
                return redirect(url_for('homePage'))
            if not user_detail:
                flash('Invalid Log In')
                return render_template('login.html')

@app.route('/home')
def homePage():
    error = None
    print "HomePage"
    cur = g.db.execute('select name from users where email = \''+ session.get('username') + '\'')
    names = [row for row in cur.fetchall()]
    print "Homepage"
    print names
    name = names[0]
    print name
    display_name = name[0]
    return render_template('home.html',display_name=display_name)

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('logged_in', None)
    return redirect(url_for('main_page'))

@app.route('/group_listing')
def group_listingPage():
    error = None
    cur_users = g.db.execute('select mid from users where email = \''+ session.get('username') + '\'')
    mids = [row for row in cur_users.fetchall()]
    print mids
    mid=mids[0]
    print mid[0]
    cur_groups = g.db.execute('select name from groups where admin_id = \''+ str(mid[0]) + '\'')
    print cur_groups
    group_names = [row for row in cur_groups.fetchall()]
    print group_names
    return render_template('group_listing.html', group_names=group_names)

@app.route('/group_listing', methods=['POST'])
def group_listing():
    error = None
    if request.method == 'POST':
        if request.form['group_listing'] == "GroupListing":
            return redirect(url_for('add_groupPage'))

@app.route('/add_group')
def add_groupPage():
    error = None
    return render_template('add_group.html')

@app.route('/add_group', methods=['POST'])
def add_group():
    error = None
    if request.method == 'POST':
        if request.form['add_group'] == "next":
                cur = g.db.execute('select mid from users where email = \''+ session.get('username') + '\'')
                mids = [row for row in cur.fetchall()]
                mid=mids[0]
                g.db.execute('insert into groups (name,admin_id, description, venue, eventdate) values (?, %d,?, ?,?)'%mid,
                         [request.form['name'], request.form['description'], request.form['venue'], request.form['eventdate'] ])

                cur_group =  g.db.execute('select gid from groups where name = \'' + request.form['name'] + '\'')
                group_id = [row for row in cur_group.fetchall()]
                group_id = group_id[0]

                g.db.execute('insert into group_members values (' + group_id + '\, ' + mid + '\)')
                g.db.commit()

                session['gname']=request.form['name']
                return redirect(url_for('group_membersPage'))
        else:
                flash('Try Again')
                return redirect(url_for('add_groupPage'))

@app.route('/group_members')
def group_membersPage():
    error = None
    return render_template('group_members.html')

@app.route('/group_members', methods=['POST'])
def group_members():
    error = None
    if request.method == 'POST':
        if request.form['edit_group_members'] == "next":
			for i in range(1,6) :
				f = "email{0}".format(i)
				g.db.execute('insert into group_members(mid,gid) values ((select mid from users where email=\"' + request.form[f]+ '\") ,(select gid from groups where name=\"' + session['gname']+ '\"))')

			#g.db.execute('insert into group_members(mid,gid) values ((select mid from users where email=\"' + request.form['email']+ '\") ,(select gid from groups where name=\"' + session['gname']+ '\"))')
			g.db.commit()
			print "go to hell"
			flash('Successfully Created')
			return redirect(url_for('display_group_membersPage'))

@app.route('/display_group_members')
def display_group_membersPage():
    error = None
    if request.method == 'GET':
		#g.db.execute('insert into users (name, email, password) values ("tgif", "6", "abc")')
		#g.db.commit()
		cur = g.db.execute('select name from users where mid in (select mid from group_members where gid in (select gid from groups where name =\"' + session['gname']+ '\"))')
		#g.db.execute('insert into users (name, email, password) values ("tgif", "999", "abc")')
		#g.db.commit()
		entries = [dict(name=row[0]) for row in cur.fetchall()]
		#g.db.execute('insert into users (name, email, password) values ("tgif", "100", "abc")')
		#g.db.commit()
    return render_template('display_group_members.html', entries=entries)

@app.route('/display_group_members', methods=['POST'])
def display_group_members():
    error = None
    if request.method == 'POST':
		if request.form['delete'] == "delete":
			#g.db.execute('delete from group_members where mid in ((select mid from users where name=\"' + request.form["member"]+ '\"))')
			#return render_template('display_group_members.html')
			memberName = request.form['member']
			g.db.execute('delete from group_members where mid in ((select mid from users where name=\"' + memberName + '\"))')
			db.commit()
			cur = g.db.execute('select name from users where mid in (select mid from group_members where gid in (select gid from groups where name =\"' + session['gname']+ '\"))')
			entries = [dict(name=row[0]) for row in cur.fetchall()]
			pageFunctionName='display_group_members.html'
			return redirect(url_for('showBag'))
			#return render_template('display_group_members.html', entries=entries)
		elif request.form['add_more'] == "add_more":
			pageFunctionName='group_members.html'
		elif request.form['finish'] == "finish":
			pageFunctionName='group_summary.html'
    return render_template(pageFunctionName)

@app.route('/group_summary')
def group_summary_init():
    error = None
    return render_template('group_summary.html')

@app.route('/group_summary', methods=['POST'])
def group_summary():
    error = None
    if request.method == 'POST':
		if request.form['next'] == "next":
			return render_template('home.html')


@app.route('/showBag')
def showBag_init():
    error = None
    return render_template('showBag.html')

@app.route('/showBag', methods=['POST'])
def showBag():
    error = None
    if request.method == 'POST':
        if request.form['showBag'] == "finish":
			g.db.execute('insert into my_bag (mid_assignee,mid_assignor,iid) values (1, 1, 1)')
			g.db.commit()
			g.db.execute('select mid_assignee, mid_assignor, gid from my_bag as m where session["mid"]')
			flash('Successfully Created')
			return redirect(url_for('showBag'))

@app.route('/saved_recipes')
def savedRecipesPage():
    error = None
    print "In saved recipes page"
    cur = g.db.execute('select mid from users where email = \''+ session.get('username') + '\'')
    mids = [row for row in cur.fetchall()]
    mid=mids[0]
    print mid
    cur_recipe = g.db.execute('select name from recipes where rid in (select rid from group_category_recipes where mid =\'' + str(mid[0])+ '\')')
    recipe_names = [row for row in cur_recipe.fetchall()]
    print "In Saved Recipes Page"
    return render_template('saved_recipes.html', recipe_names = recipe_names)

@app.route('/recipe/')
@app.route('/recipe/<recipe_name>')
def recipe(recipe_name):
    print "In recipe"
    print recipe_name
    error = None
    cur = g.db.execute('select * from recipes where name = \''+ recipe_name + '\'')
    recipe_details = [row for row in cur.fetchall()]
    recipe_details = recipe_details[0]
    print recipe_details
    rid = recipe_details[0]
    cid = recipe_details[1]
    rating = recipe_details[4]
    cook_time = recipe_details[5]
    servings = recipe_details[6]

    print rid
    print cid
    print rating
    print cook_time
    print servings

    instructions = recipe_details[3]
    print instructions

    cur_ingredients = g.db.execute('select name,quantity from ingredients,recipe_ingredients where rid = ' + str(rid) + ' and recipe_ingredients.iid = ingredients.iid')
    ingredient_list = [row for row in cur_ingredients.fetchall()]
    print ingredient_list

    cur_users = g.db.execute('select mid from users where email = \''+ session.get('username') + '\'')
    mids = [row for row in cur_users.fetchall()]
    print mids
    mid=mids[0]
    print mid[0]
    cur_group_names = g.db.execute('select name from groups where gid in(select gid from group_members where mid = ' + str(mid[0])+')')
    group_names = [row for row in cur_group_names.fetchall()]
    print group_names

    group_list = {}
    for name in group_names:
        print name[0]
        cur_group_members =  g.db.execute('select name from users where mid in(select mid from group_members where gid =(select gid from groups where name=\''+str(name[0])+'\'))' )
        member_name = [row for row in cur_group_members.fetchall()]
        print member_name
        member_names=[ member[0] for member in member_name]
        group_list[name[0]]=member_names
    print group_list
    jsonGroupList = json.dumps(group_list)
    return render_template('recipe.html',recipe_name = recipe_name, rating=rating, cook_time=cook_time, servings=servings, instructions=instructions,ingredient_list=ingredient_list,group_list=group_list, jsonGroupList=jsonGroupList)


@app.route('/save/')
@app.route('/save/<recipe_name>')
def save(recipe_name):
    error = None
    print 'In save'
    return redirect(url_for('recipe',recipe_name=recipe_name))

@app.route('/share/')
@app.route('/share/<recipe_name>')
def share(recipe_name):
    error = None
    print 'In share'
    return redirect(url_for('recipe', recipe_name=recipe_name))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
