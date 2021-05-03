from flask import Flask,render_template,request,url_for,redirect,jsonify   #Importing required modules
from flask_sqlalchemy import SQLAlchemy   #importing SQLAlchemy database
from datetime import datetime
import json


app=Flask(__name__)                                            #defining app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'   #app configuration with SQLAlchemy database
db=SQLAlchemy(app)

class BlogPost(db.Model):                                      #BlogPost class
    id=db.Column(db.Integer,primary_key=True)                  #Defining attributes and constraints for database
    title=db.Column(db.String(100),nullable=False)
    content=db.Column(db.Text,nullable=False)
    author=db.Column(db.String(20),nullable=False,default='N/A')
    date_posted=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)

    def __repr__(self):
        return "Blog post "+str(self.id)

@app.errorhandler(404)                 #If the requested url is not found, then it displays 404 error message
def errorhandler(error):
    return (jsonify({'message':'Not Found','code':404})) #displaying error in the form of JSON


@app.route('/')                                 #defining route for /  , it allows only GET method.
def index():
    return render_template('index.html')        #if URL is localhost:5000/ then index.html page will be displayed.

@app.route('/posts',methods=['POST','GET'])     # route = /posts, it allows POST and Get methods
def posts():
  try:
    if request.method =='POST':
        post_title=request.form['title']      #collecting all information from the html input fields and stores it-
        post_content=request.form['content']  # -in database table as new Blog post
        post_author=request.form['author']
        new_post = BlogPost(title=post_title,content=post_content,author=post_author)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts')             #after adding new row to the database, redirect to /posts page
    
    else:
        all_posts=BlogPost.query.order_by(BlogPost.date_posted).all()
        return render_template('posts.html')  #if method is not POST , then it renders posts.html page,which contains- 
                                                                                     # -html form to create new post
  except Exception as err:
      return f"{err}"
      

@app.route('/posts/delete/', methods=['POST','DELETE'])
def delete():                                               # deleting a post from the database
  try:
    if request.method == 'POST':
        all_posts=BlogPost.query.order_by(BlogPost.date_posted).all() # collecting all rows(all posts) from the database.
        id=request.form['del']               # collecting id of the post from the html input field,which is to be deleted.
        post=BlogPost.query.get(id)          # Checking whether the post with given id is exists in database.
        if post:                             # if it exists, then delete that post from database
            db.session.delete(post)
            db.session.commit()              # without commiting,no changes will going to apply!
            delpost=BlogPost.query.get(id)   # After deleting,again we are checking the existance of that post.
            if not delpost:                  # If that post is Successfully deleted, then display the below message
                return '''<h1 style="text-align:center; font-family:Arial, Helvetica, sans-serif; margin-top:200px;">Successfully deleted. <a href="/posts/normalview"> VIEW</a> all posts to see changes</h1>
                        
                        '''
        if not post:      # If the post with given id not exist in database, then display the error message in JSON format.
            return jsonify({'message':'Invalid Post ID'})
  except Exception as err:
      return f"{err}"

  
        
        
@app.route('/posts/edit/<int:id>', methods=['GET','POST'])  # route for editing Blog posts. It takes id of the post (integer)
def edit(id):
    post=BlogPost.query.get_or_404(id)                      # get the post by using supplied post id.
    if request.method == 'POST':
        
        post.title=request.form['title']                    #take new title for the post,specified in html input field and apply changes to-
        post.author=request.form['author']                                       #- the original post
        post.content=request.form['content']
        db.session.commit()
        return redirect('/posts')

    else:
        return render_template('edit.html',post=post)

@app.route('/posts/normalview',methods=['GET'])
def normalview():
    all_posts=BlogPost.query.order_by(BlogPost.date_posted).all()  # Getting all the blog posts from the database
    
    return render_template('normalview.html',posts=all_posts)      # displaying all posts in normalview.html page bypassing
                                                                                  #- posts object.
@app.route('/posts/jsonview',methods=['GET'])
def jsonview():                                                     #JSON view of all posts
    all_posts=BlogPost.query.order_by(BlogPost.date_posted).all()   # Getting all the blog posts from the database
    
    output=[]                                                       # new output list,to store dictionary
    for post in all_posts:
            data={}                                                 #new dictionary to store data of each post.
            data['id']=post.id
            data['title']=post.title
            data['content']=post.content
            data['author']=post.author
            output.append(data)                                     #appending each dictionary to output list.
    
    
    return jsonify(output)                                          # displaying all posts in JSON format
             
    
    
if __name__=='__main__':
    app.run(debug=True)                     # running our app. Automatically changes will be saved because of debug=True.