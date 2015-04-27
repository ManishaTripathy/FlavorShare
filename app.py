# all the imports
import sqlite3,re,json,ast
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
    if not session.get('logged_in'):
        return render_template('register.html')
    else :
        return redirect(url_for('homePage'))

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
    if not session.get('logged_in'):
        return render_template('login.html')
    else :
        return redirect(url_for('homePage'))


@app.route('/login', methods=['POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['login'] == "Login":
            cur = g.db.execute('select email, password from users where email = \"' + request.form['username'] + '\" and password = \"' + request.form['password'] + '\"')
            user_detail = [row for row in cur.fetchall()]
            if user_detail:
                flash('Successfully Logged In')
                session['username'] = request.form['username']
                session['logged_in'] = True
                return redirect(url_for('homePage'))
            if not user_detail:
                flash('Invalid Log In')
                return render_template('login.html')

@app.route('/home')
def homePage():
    error = None
    if not session.get('logged_in'):
        return render_template('login_or_register.html')
    cur = g.db.execute('select name from users where email = \''+ session.get('username') + '\'')
    names = [row for row in cur.fetchall()]
    name = names[0]
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
    #print mids
    mid=mids[0]
    #print mid[0]
    cur_groups = g.db.execute('select name from groups where gid in ( select gid from group_members where mid = \''+ str(mid[0]) + '\')')
    #print cur_groups
    group_names = [row for row in cur_groups.fetchall()]
    #print group_names
    return render_template('group_listing.html', group_names=group_names)

@app.route('/group_listing', methods=['GET','POST'])
def group_listing():
	error = None
	if request.method == 'GET':
		cur_users = g.db.execute('select mid from users where email = \''+ session.get('username') + '\'')
		mids = [row for row in cur_users.fetchall()]
		#print mids
		mid=mids[0]
		#print mid[0]
		cur_groups = g.db.execute('select name from groups where admin_id = \''+ str(mid[0]) + '\'')
		#print cur_groups
		group_names = [row for row in cur_groups.fetchall()]
		#print group_names
		return render_template('group_listing.html', group_names=group_names)
	elif request.method == 'POST':
		if 'listing' in request.form:
			print request.form['listing']
		if 'listing' in request.form:
			if request.form['listing'] == "add_group":
				return redirect(url_for('add_group'))
			else:
				group = request.form['listing']
				cur = g.db.execute('select name from users where mid in (select mid from group_members where gid in (select gid from groups where name =\"' + group+ '\"))')
				g.db.commit()
				cur_details=g.db.execute('select description,venue,eventdate from groups where gid in (select gid from groups where name =\"' + group+ '\")')
				cur_details=g.db.execute('select description,venue,eventdate from groups where gid in (select gid from groups where name =\"' + group+ '\")')
				mids = [row for row in cur_details.fetchall()]
				mid=mids[0]
				groups = [dict(gname=group)]
				names = [dict(name=row[0]) for row in cur.fetchall()]
				desc=[dict(desc=row[0]) for row in mids]
				venue=[dict(venue=row[1]) for row in mids]
				eventdate=[dict(eventdate=row[2]) for row in mids]
				return redirect(url_for('group_summary_init',groups=group))
				#return render_template('group_summary.html',groups=groups,names=names,desc=desc,venue=venue,eventdate=eventdate)


@app.route('/add_group', methods=['GET','POST'])
def add_group():
	error = None
	if request.method == 'GET':
		return render_template('add_group.html')
	elif request.method == 'POST':
		if request.form['group_members'] == "Next":
			cur = g.db.execute('select mid from users where email = \''+ session.get('username') + '\'')
			mids = [row for row in cur.fetchall()]
			mid=mids[0]
			session['grpname']=request.form['name']
			print session['grpname']
			g.db.execute('insert into groups (name,admin_id, description, venue, eventdate) values (?,%d,?,?,?)'%mid,[ request.form['name'],request.form['description'],request.form['venue'],request.form['eventdate'] ])
			g.db.commit()
			#print gname
			flash('Successfully Created')
			return redirect(url_for('group_membersPage'))
		else:
			flash('Try Again')
			return redirect(url_for('add_group'))

@app.route('/group_members_summary')
def group_members_summaryPage():
    error = None
    print session['grpname']
    return render_template('group_members_summary.html')

@app.route('/group_members_summary', methods=['POST'])
def group_members_summary():
    error = None
    print "#@##@$@%@#%$^$^#$^%"+session['gname']
    if request.method == 'POST':
        if request.form['group_summary'] == "next":
			for i in range(1,6) :
				f = "email{0}".format(i)
				g.db.execute('insert into group_members(mid,gid) values ((select mid from users where email=\"' + request.form[f]+ '\") ,(select gid from groups where name=\"' + session['gname']+ '\"))')

			#g.db.execute('insert into group_members(mid,gid) values ((select mid from users where email=\"' + request.form['email']+ '\") ,(select gid from groups where name=\"' + session['gname']+ '\"))')
			g.db.commit()

			flash('Successfully Created')
			return redirect(url_for('group_summary_init',groups=session['gname']))

@app.route('/group_members')
def group_membersPage():
    error = None
    print session['grpname']
    g.db.execute('insert into group_members(mid,gid) values ((select mid from users where mid in (select admin_id from groups where gid in(select gid from groups where name=\"' + session['grpname']+ '\"))) ,(select gid from groups where name=\"' + session['grpname']+ '\"))')
    g.db.commit()
    return render_template('group_members.html')

@app.route('/group_members', methods=['POST'])
def group_members():
    error = None
    print session['grpname']
    if request.method == 'POST':
        if request.form['display_group_members'] == "next":
			for i in range(1,6) :
				f = "email{0}".format(i)
				g.db.execute('insert into group_members(mid,gid) values ((select mid from users where email=\"' + request.form[f]+ '\") ,(select gid from groups where name=\"' + session['grpname']+ '\"))')

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
		cur = g.db.execute('select name from users where mid in (select mid from group_members where gid in (select gid from groups where name =\"' + session['grpname']+ '\"))')
		#g.db.execute('insert into users (name, email, password) values ("tgif", "999", "abc")')
		g.db.commit()
		entries = [dict(name=row[0]) for row in cur.fetchall()]
    return render_template('display_group_members.html', entries=entries)

@app.route('/display_group_members', methods=['POST'])
def display_group_members():
    error = None
    if request.method == 'POST':
		if request.form['redirect_to'] == "add_more":
			pageFunctionName='group_members.html'
			return render_template(pageFunctionName)
		elif request.form['redirect_to'] == "next":
			pageFunctionName='group_config.html'
			return redirect(url_for('group_configPage'))

@app.route('/group_summary')
def group_summary_init():
	error = None
	group = request.args['groups']
	print group
	session['gname'] = group
	cur = g.db.execute('select name from users where mid in (select mid from group_members where gid in (select gid from groups where name =\"' + group+ '\"))')
	g.db.commit()
	cur_details=g.db.execute('select description,venue,eventdate from groups where gid in (select gid from groups where name =\"' + group+ '\")')
	mids = [row for row in cur_details.fetchall()]
	mid=mids[0]
	groups = [dict(gname=group)]
	names = [dict(name=row[0]) for row in cur.fetchall()]
	desc=[dict(desc=row[0]) for row in mids]
	venue=[dict(venue=row[1]) for row in mids]
	eventdate=[dict(eventdate=row[2]) for row in mids]
	return render_template('group_summary.html',groups=groups,names=names,desc=desc,venue=venue,eventdate=eventdate)

@app.route('/group_summary', methods=['POST'])
def group_summary():
    error = None
    if request.method == 'POST':
		if 'member' in request.form:
			print request.form['member']
			memberName = request.form['member']
			g.db.execute('delete from group_members where mid in ((select mid from users where name=\"' + memberName+ '\"))')
			g.db.commit()
			return redirect(url_for('group_summary_init',groups=session['gname']))
		elif 'edit' in request.form:
			return redirect(url_for('group_members_summaryPage'))
		elif 'done' in request.form:
			return redirect(url_for('group_listingPage'))
		elif 'addrecipe' in request.form:
			#category = "Main Course"
			list = ['1','2']
			category = [dict(name="Main Course")]
			recipe=[dict(rname=row[0]) for row in list]
			#desc=[dict(desc=row[0]) for row in mids]
			#category = [dict(name=session['grpname'])]
			return render_template('add_recipe.html',recipe=recipe,category=category)
			#return redirect(url_for('add_recipePage'),recipe=recipe,category=category)


@app.route('/group_config')
def group_configPage():
    error = None
    if request.method == 'GET':
        groups = [dict(gname=session['grpname'])]
        print groups
    return render_template('group_config.html',groups=groups)

@app.route('/group_config', methods=['POST'])
def group_config():
    error = None
    if request.method == 'POST':
        if request.form['finish_group'] == "save":
            for i in range(1,11) :
                f = "category{0}".format(i)
                g.db.execute('insert into group_category(gid,cid,no_of_items) values ((select gid from groups where name=\"' + session['grpname']+ '\"),'+str(i)+', '+request.form[f]+')')
                g.db.commit()
            return redirect(url_for('homePage'))

@app.route('/saved_recipes')
def savedRecipesPage():
    error = None
    cur = g.db.execute('select mid from users where email = \''+ session.get('username') + '\'')
    mids = [row for row in cur.fetchall()]
    mid=mids[0]
    cur_recipe = g.db.execute('select name from recipes where rid in (select rid from group_category_recipes where mid =\'' + str(mid[0])+ '\')')
    recipe_names = [row for row in cur_recipe.fetchall()]
    return render_template('saved_recipes.html', recipe_names = recipe_names)

@app.route('/recipe/<recipe_name>')
def recipe(recipe_name):
    error = None
    print "In recipe/ page"
    cur = g.db.execute('select * from recipes where name = \''+ recipe_name + '\'')
    recipe_details = [row for row in cur.fetchall()]
    recipe_details = recipe_details[0]
    rid = recipe_details[0]
    cid = recipe_details[1]
    rating = recipe_details[4]
    cook_time = recipe_details[5]
    servings = recipe_details[6]

    instructions = recipe_details[3]
    cur_ingredients = g.db.execute('select name,quantity from ingredients,recipe_ingredients where rid = ' + str(rid) + ' and recipe_ingredients.iid = ingredients.iid')
    ingredient_list = [row for row in cur_ingredients.fetchall()]

    return render_template('recipe.html',recipe_name = recipe_name, rating=rating, cook_time=cook_time, servings=servings, instructions=instructions,ingredient_list=ingredient_list)

@app.route('/recipe/<recipe_name>', methods=['POST'])
def recipePost(recipe_name):
    error = None
    print "In post of recipe"
    if request.method == 'POST':
        value = request.form.getlist('ingredients')
        print "checkbox values"
        print value
        cur_users = g.db.execute('select mid from users where email = \''+ session.get('username') + '\'')
        mids = [row for row in cur_users.fetchall()]
        print mids
        mid=mids[0]
        print mid[0]
        cur_recipe = g.db.execute('select rid from recipes where name =\'' + recipe_name+ '\'')
        print cur_recipe
        rids = [row for row in cur_recipe.fetchall()]
        print rids
        rid=rids[0]

        if request.form['save_or_share'] == "Save":
            print "In Save of recipe"
            print "recipe id"
            print rid[0]

            for i in value:
                g.db.execute('insert into my_saved_bag(mid,rid,ingredient) values('+str(mid[0])+','+str(rid[0])+ ',' +'\"'+i+'\")')
            g.db.commit()

            return redirect(url_for('showBag'))
        elif request.form['save_or_share'] == "Share":
            print "In Share of recipe"

            cur_group_names = g.db.execute('select name from groups where gid in(select gid from group_members where mid = ' + str(mid[0])+')')
            group_names = [row for row in cur_group_names.fetchall()]
            print group_names

            group_list = {}
            for name in group_names:
                print name[0]
                cur_group_members =  g.db.execute('select name from users where mid != ' + str(mid[0]) + ' and mid in(select mid from group_members where gid =(select gid from groups where name=\''+str(name[0])+'\'))' )
                member_name = [row for row in cur_group_members.fetchall()]
                print member_name
                member_names=[ member[0] for member in member_name]
                group_list[name[0]]=member_names
            print group_list
            jsonGroupList = json.dumps(group_list)

            return render_template('share_ingredients.html', ingredients = value, group_list=group_list, jsonGroupList = jsonGroupList, recipe_name=recipe_name )

@app.route('/share', methods=['POST'])
def share():
    error = None
    print 'In share'
    print request.form
    ingredient_list = request.form['ingredients']
    group_name = request.form['select-group']
    group_member =  request.form['select-members']
    recipe_name = request.form['recipe_name']
    print ingredient_list
    print group_name
    print group_member

    ingredients_list1=ast.literal_eval(ingredient_list)
    ingredients_list1 = [i.strip() for i in ingredients_list1]
    print ingredients_list1

    cur_users = g.db.execute('select mid from users where email = \''+ session.get('username') + '\'')
    mids = [row for row in cur_users.fetchall()]
    print mids
    mid=mids[0]
    print mid[0]

    cur_recipe = g.db.execute('select rid from recipes where name =\'' + recipe_name+ '\'')
    print cur_recipe
    rids = [row for row in cur_recipe.fetchall()]
    print rids
    rid=rids[0]
    print "recipe id"
    print rid[0]

    cur_group = g.db.execute('select gid from groups where name = \''+ group_name + '\'')
    gids = [row for row in cur_group.fetchall()]
    print gids
    gid=gids[0]
    print "group id"
    print gid[0]

    cur_users1 = g.db.execute('select mid from users where name = \''+ group_member + '\'')
    mids1 = [row for row in cur_users1.fetchall()]
    print mids1
    mid_assignee=mids1[0]
    print "assignee"
    print mid_assignee[0]

    for i in ingredients_list1:
        print i
        g.db.execute('insert into my_shared_bag(mid_assignee,mid_assignor,rid,gid,ingredient) values('+str(mid_assignee[0])+','+str(mid[0])+','+str(rid[0])+',' + str(gid[0])+ ',' +'\"'+i+'\")')
    g.db.commit()
    return redirect(url_for('showBag'))

@app.route('/showBag')
def showBag():
    error = None

    cur_users = g.db.execute('select mid from users where email = \''+ session.get('username') + '\'')
    mids = [row for row in cur_users.fetchall()]
    mid=mids[0]

    cur_saved_bag = g.db.execute('select  ingredient from my_saved_bag where mid = ' + str(mid[0]))
    saved_bag = [row[0] for row in cur_saved_bag.fetchall()]

    cur_shared_bag = g.db.execute('select mid_assignor,gid,ingredient from my_shared_bag where mid_assignee =' + str(mid[0]))
    temp_shared_bag = [row for row in cur_shared_bag.fetchall()]

    shared_bag = []
    for row in temp_shared_bag:
        print row
        cur_group_name = g.db.execute('select name from groups where gid = ' + str(row[1]))
        group_name = [row1[0] for row1 in cur_group_name.fetchall() ]
        group_name = group_name[0]
        print group_name

        cur_member_name = g.db.execute('select name from users where mid = ' + str(row[0]))
        member_name = [row2[0] for row2 in cur_member_name.fetchall() ]
        member_name = member_name[0]
        print member_name

        shared_bag.append((row[2], group_name, member_name))

    return render_template('showBag.html', saved_bag = saved_bag,shared_bag = shared_bag)

'''@app.route('/showBag', methods=['POST'])
def showBag():
    error = None
    if request.method == 'POST':
        if request.form['showBag'] == "finish":
			g.db.execute('insert into my_bag (mid_assignee,mid_assignor,iid) values (1, 1, 1)')
			g.db.commit()
			g.db.execute('select mid_assignee, mid_assignor, gid from my_bag as m where session["mid"]')
			flash('Successfully Created')
			return redirect(url_for('showBag'))'''

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
