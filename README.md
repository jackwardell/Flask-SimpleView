# Very simple wrapper around Flask

## Background
* I write a lot of flask applications
* Mature applications often come to look like:
```
@app.route('/some-location')
@some_decorator
@another_decorator
@a_third_decorator
def some_function():
    if request.method == "POST":
        ...
        return render_template('some_template.html')
    
    elif request.method == "GET":
        ...
        return render_template('some_template.html')
```
* Where you have multiple decorators and `if request.method == 'POST':` sections in the function call


## Interests
* To separate out the concerns of the different HTTP methods
* Simple decorator handling
* Simple registration

All of these things are provided by flask.views: https://flask.palletsprojects.com/en/1.1.x/views/

I just hated the registration handling:
`app.add_url_rule('/users/', view_func=ShowUsers.as_view('show_users'))`

So I made is simpler:
`app.add_view(ShowUsers)`


## Install
```
pip install flask_simpleview
```

## Use
An example for a simple view:
```
from flask_simpleview import Flask, Blueprint, SimpleView

# this works exactly the same as flask.Flask
# flask_simpleview.Flask is subclassed from flask.Flask
# the only difference is the addition of 2 methods: `add_view` and `add_api`
app = Flask(__name__)

# and the same blurb again:
# this works exactly the same as flask.Blueprint
# flask_simpleview.Blueprint is subclassed from flask.Blueprint
# the only difference is the addition of 2 methods: `add_view` and `add_api`
auth = Blueprint('auth', __name__)

# as Flask and Blueprint are the same as their parent classes
# this will obviously work
app.register_blueprint(auth)

# This works exactly the same as flask.views.MethodView
# flask_simpleview.SimpleView is subclassed from flask.views.MethodView
# the only difference is that you encapsulate the rule (route) and 
# the endpoint in the class
class SignUp(SimpleView):
    # this is how you add a route
    # the same as:
    # @app.route('/sign-up')
    rule = '/sign-up'

    # this is how you add an endpoint
    # the same as:
    # @app.route('/sign-up', endpoint='sign_up')
    # OR
    # @app.route('/sign-up')
    # def sign_up():
    #     ... 
    endpoint = 'sign_up'

    # setting the template at class level so it can rendered 
    # when using `self.render_template`
    template = 'sign_up.html'
    
    # this is how you add decorators to View classes
    # the same as:
    # @app.route('/hello')
    # @some_decorator
    # @another_decorator
    # def hello():
    #     return "hello" 
    decorators = (some_decorator, another_decorator)

    # this is the same as @app.route('/sign-up', methods=['GET'])
    def get(self):
        # just assuming a form for the demonstration
        form = SignUpForm()
        # you don't need to pass the template string, if registered above
        return self.render_template(form=form)

    def post(self):
        form = SignUpForm(request.form)
        if form.validate_on_submit():
            # do business logic here
            sign_up_user_from_form(form)
            # the SimpleView class has access to all flask functions
            # `return self.thing` is the same as `return flask.thing`
            return self.redirect(self.url_for('login'))
        else:
            return self.render_template(form=form)

# adding the view to the application
# essentially this is equivalent to:
# @app.route('/sign-up', methods=['GET', 'POST'])
# def sign_up():
#     ...
#     return render_template('sign_up.html')
       
          
app.add_view(SignUp)
auth.add_view(SignUp)
```

Another example with only a blueprint:
```
from flask_simpleview import Blueprint, SimpleView

auth = Blueprint('auth', __name__)

class Login(SimpleView):
    rule = '/login'
    endpoint = 'login'
    template = 'login.html'

    def get(self):
        return self.render_template()

    def post(self):
        try:
            login_user(request.form)
            return self.redirect(self.url_for('app.dashboard'))
        except LoginFailed as e:
            return self.render_template(errors=e)

auth.add_view(Login)
```

Or if you want to specify the template in `self.render_template`:
```
class SignUp(SimpleView):
    rule = '/sign-up'
    endpoint = 'sign_up'

    def get(self):
        return self.render_template('sign_up.html')
```

No need for views just to have templates:
```
class LegacyDashboardRedirect(SimpleView):
    rule = '/dashboard/v1/home'
    endpoint = 'v1_dashboard'

    def get(self):
        return self.redirect(self.url_for('v2_dashboard'))
```

Or for apis:
```
class UsersAPI(SimpleView):
    rule = '/api/users'
    endpoint = 'users'
    
    def get(self):
        user_id = request.args.get('id')
        if user_id:
            return self.jsonify(db.session.query(User).get(user_id).to_json())
        else:
            return self.jsonify([u.to_json() for u in db.session.query(User)]
```

You don't have to use `self` either, you can use flask of course:
```
from flask import redirect

class AnotherView(SimpleView):
    rule = '/another-view'
    endpoint = 'another_view'
    
    def get(self):
        return redirect('https://www.example.com')
```

There is also aliases for `SimpleView`: `View` and `API` (namespace saved for some future features) 

