import os
import secrets
from PIL import Image
from flask import url_for

from blog_webapp import app, mail
from blog_webapp.utils.onetime_token_util import get_onetime_token, get_data_from_onetime_token
from flask_mail import Message


def update_user_profile_picture(current_profile_image_file, form_image):
    """
    save profile picture inside static/profile_pictures
    :param current_profile_image_file: name of current profile image
    :param form_image: image input from form
    :return: saved profile picture unique filename
    """

    # delete profile picture if exists
    curr_profile_image_path = os.path.join(app.root_path,
                                           f'static/profile_pics/{current_profile_image_file}')
    if os.path.exists(curr_profile_image_path) \
            and current_profile_image_file != 'default_profile_image.png':
        os.remove(curr_profile_image_path)

    # create unique image file name
    rand_str = secrets.token_hex(8)  # 8 byte hex code
    _, file_ext = os.path.splitext(form_image.filename)  # get the uploaded file extension
    profile_picture_filename = rand_str + file_ext
    profile_picture_path = os.path.join(app.root_path,
                                        f'static/profile_pics',
                                        profile_picture_filename)
    # resize image 125x125
    resize_img_size = (125, 125)
    form_image = Image.open(form_image)
    form_image.thumbnail(resize_img_size)

    # save image
    form_image.save(profile_picture_path)

    return profile_picture_filename


def send_reset_password_email_to_user(user):
    token = get_onetime_token({'user_id': user.id})
    email_msg = Message('Password Reset Request',
                        sender='noreply@demo.com',
                        recipients=[user.email])
    email_msg.body = f'''To reset your password click on the link below:
{url_for('users.reset_password', token=token, _external=True)}
    
If you did not make this request please ignore this email. Thank you.
    '''

    # send the email
    mail.send(email_msg)
