from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import login_user, login_required, current_user, logout_user
from .models import User, Album, Song, Playlist
from werkzeug.security import generate_password_hash, check_password_hash
import os
from . import db
import re

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email = email).first()

        if user:
            if user.role == "user" or user.role == "creator":
                if check_password_hash(user.password, password):
                    login_user(user, remember=True)
                    return redirect(url_for('views.dashboard'))
                else:
                    print('Incorrect Password')
            else:
                print("This id does not belong to a user")
        else:
            print('Email Doesnt exist. Please SignUp')

    return render_template('login.html', user = current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        
        name = request.form.get('name')
        db_name = name.lower()
        email = request.form.get('email')
        password = request.form.get('password1')
        confirm_password = request.form.get('password2')
      
        image = request.files['image']
        db_image_path = '/static/user_placeholder.png'
        if image.filename != '':
            image.save(os.path.join('website/static', image.filename).replace('\\', '/'))
            db_image_path = os.path.join('/static', image.filename).replace('\\', '/')

        creator = request.form.get('creator')

        user = User.query.filter_by(email = email).first()
        if user:
            print("User already exist. Please login")
        elif (not name or not email or not password or not confirm_password or not creator):
            print('All fields are required')
        elif not(password == confirm_password):
            print('Password and confirm Password should be same')
        elif name.len() <= '8':
            print('Minimum 8 character required')
        
        else:
            if(creator == 'creator1'):
                role = 'creator'
            elif(creator == 'creator0'):
                role = 'user'
            new_user = User(email = email, name = db_name, password = generate_password_hash(password, method='pbkdf2:sha256'), role = role, image = db_image_path)
            try:
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                print('Account Created Successfully')
                return redirect(url_for('views.dashboard'))
            except:
                db.session.rollback()

    return render_template('signup.html')

@auth.route('/admin/login', methods = ['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email = email).first()

        if user:
            if user.role == "admin":
                if check_password_hash(user.password, password):
                    login_user(user, remember=True)
                    
                    return redirect(url_for('views.admin_dashboard'))
                
                else:
                    print('Incorrect Password')
            else:
                print("Not an Admin")
        else:
            print('Email Doesnt exist. Please SignUp')

    return render_template('adminLogin.html', user=current_user)

@auth.route('/admin/signup', methods = ['GET', 'POST'])
def adminsignup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password1')
        confirm_password = request.form.get('password2')
        secret_key = request.form.get('secret_key')

        
        image = request.files['image']
        db_image_path = '/static/user_placeholder.png'
        if image.filename != '':
            image.save(os.path.join('website/static', image.filename).replace('\\', '/'))
            db_image_path = os.path.join('/static', image.filename).replace('\\', '/')

        user = User.query.filter_by(email = email).first()

        if user:
            print("User already exist. Please login")
        elif (not name or not email or not password or not confirm_password or not secret_key):
            print('All fields are required')
        elif not(password == confirm_password):
            print('Password and confirm Password should be same')
        elif not(secret_key == 'abhishek'):
            print('wrong secret key. please try again')
        else:
            new_user = User(email = email, name = name, password = generate_password_hash(password, method='pbkdf2:sha256'), role = 'admin', image = db_image_path)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            print('Account Created Successfully')
            return redirect(url_for('views.admin_dashboard'))

    return render_template('adminSignup.html')


@auth.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = current_user  

    if request.method == 'POST':
        new_name = request.form.get('name')
        new_email = request.form.get('email')
        old_password = request.form.get('old_password')
        new_image = request.files['image']
        new_password = request.form.get('password')

        if check_password_hash(user.password, old_password):
            user.name = new_name
            user.email = new_email
            if new_password:
                user.password = generate_password_hash(new_password, method='pbkdf2:sha256') 
            if new_image:
                 if new_image.filename != '':
                    new_image.save(os.path.join('website/static', new_image.filename).replace('\\', '/'))
                    db_image_path = os.path.join('/static', new_image.filename).replace('\\', '/')
                    user.image  = db_image_path
                    
            new_creator = request.form.get('creator')

            if(new_creator == 'creator1'):
                new_role = 'creator'
            elif(new_creator == 'creator0'):
                new_role = 'user'
            if(user.role == 'creator' or user.role == 'user'):
                user.role = new_role
            try:
                db.session.commit()
                print('Profile updated successfully!', 'success')
                return redirect(url_for('auth.edit_profile'))
            except Exception as e:
                db.session.rollback()
                print(f'Failed to update profile: {str(e)}', 'error')
        else:
            print('Wrong Password')

    return render_template('edit_profile.html', user=user)
