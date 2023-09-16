#The main app
from flask import Flask, render_template, redirect, url_for

#Used to determine the post and get methods
from flask import request

#Local import for model
from model import db, User, Admin, Category, Product

#Instance relative config is very important
app = Flask(__name__, instance_relative_config=True)

#Path to database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"

#Why not instantiate app with db why not the other way around?
db.init_app(app)

#This creates the tables in the db
with app.app_context():
    db.create_all()

#First is the index route which gives a brief intro to website
#Along with the sign in option
@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == "POST":
        
        #Bad Authentication
        users = User.query.all()    
        for user in users:
            if request.form["username"] == user.username and request.form["password"] == user.password:
                return render_template("login.html", products = Product.query.all(), product_count_negative=False)

        return render_template("index.html", again = True)        

    return render_template("index.html", again = False)

#Register the user first
#Registration page has to be same for all?
@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == "POST":
        users = User.query.all()

        for user in users:
            if user.username == request.form["username"]:
                return render_template("register.html", again = True)
        
        db.session.add(User(username = request.form["username"], password = request.form["password"], fname = request.form["fname"].lower(), lname = request.form["lname"].lower()))
        db.session.commit()

        return render_template("login.html", products = Product.query.all(), product_count_negative=False)
    
    return render_template("register.html", again = False)

@app.route('/login', methods=["POST"])
def login():
    if request.method == "POST":
        products = Product.query.all()
        
        (total, cart) = (0, {})

        #Product count cannot become negative
        for product in products:
            if product.pcount != 0 and request.form[str(product.pid)] != "" and product.pcount-int(request.form[str(product.pid)])<0:
                return render_template("login.html", products = Product.query.all(), product_count_negative=True)
            if product.pcount != 0 and request.form[str(product.pid)] != "":
                cart[product.pid] = [product.pname, int(request.form[str(product.pid)])*product.pprice]
                total += cart[product.pid][1]
        
        return render_template("cart.html", items_bought = cart, total_cost = total)

@app.route('/admin', methods = ['GET', 'POST'])
def admin():
    if request.method == "POST":
        
        #Bad authentication
        admins = Admin.query.all()
        
        for admin in admins:
            if request.form["username"] == admin.username and request.form["password"] == admin.password:
                return render_template("adminlogin.html", products = Product.query.all(), categories = Category.query.all())

        return render_template("admin.html", again=True)

    return render_template("admin.html", again=False)

@app.route("/search", methods = ['GET', 'POST'])
def search():
    if request.method == "POST":
        if request.form["item"]=="product":
            products = Product.query.all()

            for product in products:
                if product.pname.lower() == request.form["itemname"].lower():
                    return render_template("found.html", is_product = True, product=True)

            return render_template("found.html", is_product = True, product=False)
        
        if request.form["item"]=="category":
            categories = Category.query.all()

            for category in categories:
                if category.cname.lower() == request.form["itemname"].lower():
                    return render_template("found.html", is_product = False, category=True)

            return render_template("found.html", is_product=False, category=False)
    
    return render_template("search.html")

@app.route("/category", methods = ['GET', 'POST'])
def category():
    if request.method == "POST":
        db.session.add(Category(cname = request.form["cname"]))
        db.session.commit()
    
    return render_template("category.html", categories = Category.query.all())

@app.route("/category/update/<int:category_id>", methods = ['GET', 'POST'])
def category_update(category_id):
    if request.method == "POST":

        #Create a new category
        new_cat = Category(cname = request.form["cname"])
        
        #Add the new category name
        db.session.add(new_cat)

        #Update products with the old category
        products = Product.query.all()

        for product in products:
            if product.pcid == category_id:
                db.session.add(Product(pname=product.pname, pcid=new_cat.cid, pcount=product.pcount))
                db.session.delete(product)

        #Delete the old category name
        db.session.delete(Category.query.filter_by(cid = category_id).first())

        #Do all the changes
        db.session.commit()

        return redirect(url_for("category"))

    return render_template("category_update.html", category = Category.query.filter_by(cid = category_id).first())

@app.route("/category/delete/<int:category_id>")
def category_delete(category_id):
    
    #Update products with the old category
    products = Product.query.all()

    for product in products:
        if product.pcid == category_id:
            db.session.add(Product(pname=product.pname, pcid=1, pcount=product.pcount, pprice=product.pprice))
            db.session.delete(product)

    db.session.delete(Category.query.filter_by(cid = category_id).first())
    db.session.commit()

    return redirect(url_for("category"))

@app.route("/product", methods = ["GET", "POST"])
def product():
    categories = Category.query.all()
    catd = {}
    for category in categories:
        catd[category.cid] = category.cname
    
    if request.method == "POST":
        #No negative product count and price
        product_count = int(request.form["pcount"])
        product_price = int(request.form["pprice"])

        if product_count<0 and product_price<0:
            return render_template("product.html", products = Product.query.all(), categorydict = catd, categories=Category.query.all(), was_price_negative=True, was_count_negative=True)

        if product_count < 0:
            return render_template("product.html", products = Product.query.all(), categorydict = catd, categories=Category.query.all(), was_price_negative=False, was_count_negative=True)

        if product_price < 0:
            return render_template("product.html", products = Product.query.all(), categorydict = catd, categories=Category.query.all(), was_price_negative=True, was_count_negative=False)

        db.session.add(Product(pname = request.form["pname"], pcid = request.form["pcid"], pcount = product_count, pprice = product_price))
        db.session.commit()

        return redirect(url_for("product"))
    
    return render_template("product.html", products = Product.query.all(), categorydict = catd, categories=Category.query.all(), was_price_negative=False, was_count_negative=False)

@app.route("/product/update/<int:product_id>", methods = ['GET', 'POST'])
def product_update(product_id):
    categories = Category.query.all()
    catd = {}
    for category in categories:
        catd[category.cid] = category.cname
    
    if request.method == "POST":

        update_product = Product.query.filter_by(pid = product_id).first()
        
        #ONLY UPDATE THE FIELDS THAT HAVE CHANGED
        if request.form["pname"] != "":
            update_product.pname = request.form["pname"]
        
        #Product price and count both are negative
        if request.form["pcount"] !="" and request.form["pprice"] != "" and int(request.form["pcount"]) < 0 and int(request.form["pprice"]) < 0:
            return render_template("product_update.html", product = Product.query.filter_by(pid=product_id).first(), categorydict = catd, categories=Category.query.all(), was_count_negative = True, was_price_negative = True, is_count_becoming_negative=False)

        #Also check if the count is positive
        if request.form["pcount"] !="":
            if int(request.form["pcount"]) > 0:
                if request.form["change_count"] == "add":
                    update_product.pcount += int(request.form["pcount"])
                elif (update_product.pcount-int(request.form["pcount"])) >= 0:
                    update_product.pcount -= int(request.form["pcount"])
                elif (update_product.pcount-int(request.form["pcount"])) < 0:
                    return render_template("product_update.html", product = Product.query.filter_by(pid=product_id).first(), categorydict = catd, categories=Category.query.all(), was_count_negative = False, was_price_negative = False, is_count_becoming_negative=True)
            else:
                return render_template("product_update.html", product = Product.query.filter_by(pid=product_id).first(), categorydict = catd, categories=Category.query.all(), was_count_negative = True, was_price_negative = False, is_count_becoming_negative=False)

        #Select option should be not "none"
        if update_product.pcid != request.form["change_category"] and request.form["change_category"] != "none":
            update_product.pcid = request.form["change_category"]

        #Also check if price is positive
        if request.form["pprice"] != "":
            if int(request.form["pprice"]) > 0:
                update_product.pprice = int(request.form["pprice"])
            else:            
                return render_template("product_update.html", product = Product.query.filter_by(pid=product_id).first(), categorydict = catd, categories=Category.query.all(), was_count_negative=False, was_price_negative=True, is_count_becoming_negative=False)

        db.session.commit()

        return redirect(url_for("product"))
    

    return render_template("product_update.html", product = Product.query.filter_by(pid=product_id).first(), categorydict = catd, categories=Category.query.all(), was_count_negative=False, was_price_negative=False, is_count_becoming_negative=False)

@app.route("/product/delete/<int:product_id>", methods = ["GET", "POST"])
def product_delete(product_id):
    db.session.delete(Product.query.filter_by(pid = product_id).first())
    db.session.commit()
    return redirect(url_for("product"))

@app.route("/sample")
def sample():
    #Categories
    sample = [Category(cname='Miscellaneous'), Category(cname='Dairy'), Category(cname='Stationary'), 
              Product(pname='Paneer', pcid=2, pcount=5, pprice= 60), Product(pname='Milk', pcid=2, pcount=2, pprice= 30), 
              Product(pname='Pen', pcid=3, pcount=6, pprice= 10), Product(pname='Notebook', pcid=3, pcount=5, pprice= 40),
              Product(pname='Eraser', pcid=3, pcount=0, pprice= 5),
              Admin(username='admin', password='1234'), 
              User(username='nomit', password='1234', fname = 'nomit')]

    for item in sample:
        db.session.add(item)
    
    db.session.commit()

    return redirect("/")

if __name__ == '__main__':
    app.run(debug = True)