from datetime import datetime
import glob
import shutil
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import chdir, listdir, makedirs, path, urandom
from zoneinfo import ZoneInfo
from flask_login.utils import login_required, current_user, login_user, logout_user
import logging

import qrcode
from bs4 import BeautifulSoup as bs
from flask import redirect, render_template, request, session, url_for, send_file
from flask.helpers import flash
from flask_babel import _, gettext
from flask_wtf.csrf import CSRFError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from src import app, babel, db, login_manager
from src.forms import (AcceptShimentForm, CreateShipmentForm,
                       DeleteShipmentForm, SignShipmentDocsForm, TokenForm, LoginForm)
from src.models import Car, Driver, Shipment, User, Company


def get_file_auth_token(shipment_id):
    shipment_auth_token = ''

    try:
        shipment_auth_token_file = open(
            f'sms/static/shipments/{shipment_id}/auth_token.txt', 'rt')
        shipment_auth_token = shipment_auth_token_file.readline(30)
        return shipment_auth_token
    except FileNotFoundError as e:
        print('shipment ERROR: ' + str(e))
        return

# ts = datetime.now(tz=ZoneInfo('Europe/Moscow'))
# time_str = f"{str(ts.day)}_{str(ts.month)}_{str(ts.year)}_{str(ts.hour)}_{str(ts.minute)}_{str(ts.second)}"
# logging.basicConfig(filename=f'sms/logs/log_{time_str}.txt')


def send_email(email, psw, FROM, TO, msg):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(f'{email}', f'{psw}')
    server.sendmail(FROM, TO, msg.as_string())
    server.close()


@app.route('/', methods=['POST', 'GET'])
def index():

    title = gettext('Homepage')
    # id = request.args.get('identification', default=0, type=int)
    # name = request.args.get('name', default='zxc', type=str)

    return render_template("pages/index.html", title=title)

@app.route('/shipment/<shipment_id>/download')
def downloadFile(shipment_id=None):
    file = request.args.get('file')
    mimetype = request.args.get('mimetype')
    return send_file(file, mimetype=mimetype)


@app.route('/shipment/<shipment_id>/<token>')
def showShipment(shipment_id=None, token=None):
    form = DeleteShipmentForm()
    title = _('Shipment №{id}').format(id=shipment_id)
    shipment_auth_token = get_file_auth_token(shipment_id)
    shipment = ''
    company = ''
    driver = ''
    car = ''
    qrdownload = f'static/shipments/{shipment_id}/shipmentQR.jpg'
    # sign = f'static/shipments/{shipment_id}/eSign.txt'
    docs = []
    chdir('sms')
    for doc in glob.glob(f'static/shipments/{shipment_id}/*.pdf'):
        print(doc)
        docs.append(doc)
    chdir('..')
    try:
        if token == shipment_auth_token:
            shipment = Shipment.query.get(shipment_id)
            driver = shipment.driver
            company = driver.company
            car = shipment.car
            qrurl = f'/static/shipments/{shipment_id}/shipmentQR.jpg'
        else:
            return redirect(url_for('shipmentLogin', shipment_id=shipment_id))
    except AttributeError as e:
        print('shipment ERROR: ' + str(e))
        return redirect(url_for('index'))

    return render_template('pages/shipment.html', title=title, qrurl=qrurl, shipment_id=shipment_id, shipment=shipment, driver=driver, car=car, company=company, docs=docs, form=form, token=shipment_auth_token, sign='', qrdownload=qrdownload)


@app.route('/shipment-login/<shipment_id>', methods=['POST', "GET"])
def shipmentLogin(shipment_id):
    title = _("Auth token")

    form = TokenForm()

    url_auth_token = request.args.get('token', default='', type=str)
    shipment_auth_token = get_file_auth_token(shipment_id)

    if url_auth_token == shipment_auth_token:
        return redirect(url_for('showShipment', shipment_id=shipment_id, token=shipment_auth_token))

    if form.validate_on_submit():
        form_auth_token = form.token.data
        if form_auth_token == shipment_auth_token:
            return redirect(url_for('showShipment', shipment_id=shipment_id, token=shipment_auth_token))
        else:
            flash(_('Invalid authentication token'), 'error')
            return redirect(url_for('index'))

    return render_template('pages/shipment-login.html', title=title, token_form=form)


@app.route('/search-shipment', methods=['POST', 'GET'])
def searchShipment():
    if request.method == "POST":
        shipment_id = request.form['shipment_id']
        try:
            shipment = Shipment.query.get(shipment_id)
            if not shipment.id:
                raise BaseException
        except BaseException:
            flash(_('Invalid shipment id'), 'error')
            return redirect(url_for('index'))
        return redirect(url_for('showShipment', shipment_id=shipment_id, token='0'))
    return redirect(url_for('index'))


@app.route('/login/<to>', methods=['POST', "GET"])
def login(to=None):
    title = _("Login")
    if current_user.is_authenticated:
        if to == 'create':
            return redirect(url_for('createShipment'))
        elif to == 'list':
            return redirect(url_for('shipmentsList'))  
        elif to == 'index':
            return redirect(url_for('index'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        psw = login_form.psw.data
        rm = login_form.stay_box.data
        try:
            user = User.query.first()
            user.psw = app.config['LOGIN_KEY']
            db.session.add(user)
            db.session.flush()
            db.session.commit()
        except BaseException as e:
            db.session.rollback()
            print("login ERROR: "+str(e))
        if check_password_hash(generate_password_hash(user.psw), psw):
            login_user(user, remember=rm)
            flash(_('Successfully logged in'), 'success')
            if to == 'create':
                return redirect(url_for('createShipment'))
            elif to == 'list':
                return redirect(url_for('shipmentsList'))  
            elif to == 'index':
                return redirect(url_for('index'))
        flash(_('Incorrect password'), 'text-red')
    return render_template('pages/login.html', title=title, form=login_form, red_from=to)


@app.route('/logout', methods=['POST', "GET"])
def logout():
    logout_user()
    flash(_('Successfully logged out'), 'success')
    return redirect(url_for('index'))


@app.route('/create-shipment', methods=['POST', 'GET'])
@login_required
def createShipment():
    title = _("Create")
    cars = Car.query.order_by(Car.reg_num).all()
    drivers = Driver.query.order_by(Driver.fio).all()
    create_form = CreateShipmentForm()
    create_form.car.choices = [(car.id, car.reg_num) for car in cars]
    create_form.driver.choices = [(driver.id, driver.fio)
                                  for driver in drivers]
    if create_form.validate_on_submit():
        for doc in create_form.docs.data:
            docname = doc.filename
            list_docname = docname.split('.')
            for ext in app.config['ALLOWED_EXTENSIONS']:
                if str(ext) not in list_docname:
                    flash(_('Incorrect file extension, use .pdf'), 'error')
                    return redirect(url_for('createShipment'))
        auth_token = urandom(15).hex()
        try:
            shipment = Shipment(car_id=create_form.car.data, arrival_date=create_form.arrival_date.data,
                                driver_id=create_form.driver.data, auth_token=auth_token)
            db.session.add(shipment)
            shipment = Shipment.query.filter(
                Shipment.auth_token == auth_token)
            shipment_folder = f'sms/static/shipments/{shipment[0].id}'
            if not path.isdir(shipment_folder):
                makedirs(shipment_folder)
            docs = create_form.docs.data
            for file in docs:
                filename = secure_filename(file.filename)
                folder = path.join(shipment_folder, filename)
                file.save(folder)
            shipment[0].docs_url = shipment_folder
            db.session.flush()
            auth_token_file = open(
                f'{shipment_folder}/auth_token.txt', 'wt')
            print(auth_token, file=auth_token_file)
            db.session.commit()
            return redirect(url_for('showQR', shipment_id=shipment[0].id))
            # return redirect(url_for('signDocs', shipment_id=shipment[0].id))
        except TypeError as e:
            db.session.rollback()
            print("create-shipment ERROR: "+str(e))

    return render_template('pages/create-shipment.html', title=title, cars=cars, drivers=drivers, form=create_form)

# @app.route('/create-shipment/signing-<shipment_id>', methods=['POST', 'GET'])
# @login_required
# def signDocs(shipment_id):
#     title = _('Sign Docs')
#     signForm = SignShipmentDocsForm()
#     docs = []
#     for doc in glob.glob(f'sms/static/shipments/{shipment_id}/*.pdf'):
#         doc_filename = doc.split('/')
#         docs.append(doc_filename[4])
#     if signForm.validate_on_submit():
#         if signForm.confirm.data:
#             for key in signForm.sign.data:
#                 key_filename = key.filename
#                 list_docname = key_filename.split('.')
#                 for ext in app.config['ALLOWED_EXTENSIONS_KEY']:
#                     if str(ext) not in list_docname:
#                         flash(_('Incorrect file extension, use .txt'), 'error')
#                         return redirect(url_for('createShipment'))
#             shipment = Shipment.query.filter(Shipment.id == shipment_id)
#             try:
#                 key = signForm.sign.data[0]
#                 filename = 'eSign.txt'
#                 folder = path.join(shipment[0].docs_url, filename)
#                 key.save(folder)
#                 return redirect(url_for('showQR', shipment_id=shipment[0].id))
#             except FileNotFoundError as e:
#                 print("SIGN ERROR: "+str(e))
#         else:
#             flash(_("You must confirm your upload"), 'error')
#             return redirect(url_for('createShipment'))

#     return render_template('pages/sign-docs.html', title=title, docs=docs, form=signForm, shipment_id=shipment_id)



@app.route('/create-shipment/show-qr-<shipment_id>')
def showQR(shipment_id):
    title = _("QR code")
    qrurl = ''
    current_auth_token = ''
    try:
        shipment = Shipment.query.filter(Shipment.id == shipment_id)
        shipment_folder = f'sms/static/shipments/{shipment[0].id}'
        auth_token_file = open(f'{shipment_folder}/auth_token.txt', 'rt')
        current_auth_token = auth_token_file.read(30)
        qr = qrcode.make(
            f'https://clowixoff.pythonanywhere.com/shipment-login/{shipment[0].id}?token={current_auth_token}')
        qr.save(f'{shipment_folder}/shipmentQR.jpg')
        qrurl = f'/static/shipments/{shipment_id}/shipmentQR.jpg'

        # ** send email
        server_email = app.config['EMAIL_HOST_USER']
        server_psw = app.config['EMAIL_HOST_PASSWORD']
        driver_email = shipment[0].driver.email
        msg = MIMEMultipart('alternative')
        msg['From'] = server_email
        msg['To'] = driver_email
        msg['Subject'] = f'QR-Code for shipment id{shipment_id}'
        qr_to_send = [
            'shipmentQR.jpg'
        ]
        arrival_date_for_msg = shipment[0].arrival_date
        html = f"""
        From: {msg['From']}<br>
        To: {msg['To']}<br>
        Subject: {msg['Subject']}<br>
        <b>This message was automatically generated, you don't have to reply to it</b> <br>
        authentication token - <b>{current_auth_token}</b>
        <hr width=100%>
        RU: <br>
        На ваше имя сгенерирована доставка с <b>id{shipment_id}</b>, если вас <b>не</b> предупредили об этом, или это письмо было отправлено вам по ошибке, отправьте сообщение на <b>clowixoff@gmail.com</b>, помогите нам разобраться в этом <br>
        
        Дата прибытия:<b>{arrival_date_for_msg}</b> <br>
        ENG: <br>
        The shipment has been generated in your name with <b>id{shipment_id}</b>, if you were <b>not</b> warned about this, or this letter was sent to you by mistake, send a message to <b>clowixoff@gmail.com</b>, help us figure it out <br>

        Arrival date: <b>{arrival_date_for_msg}</b> <br>
        """
        # text = bs(html, 'html.parser').text
        # text_part = MIMEText(text, 'plain')
        # msg.attach(text_part)
        html_part = MIMEText(html, 'html')
        msg.attach(html_part)
        for qr in qr_to_send:
            with open(f'{shipment_folder}/shipmentQR.jpg', 'rb') as f:
                data = f.read()
                qr_part = MIMEBase('application', 'octet-stream')
                qr_part.set_payload(data)
            encoders.encode_base64(qr_part)
            qr_part.add_header('Content-Disposition',
                               f'attachment; filename={qr}')
            msg.attach(qr_part)
        send_email(server_email, server_psw, server_email, driver_email, msg)

    except FileNotFoundError as e:
        print('show-qr ERROR: '+str(e))

    return render_template('pages/show-qr.html', title=title, shipment_id=shipment_id, qrurl=qrurl, token=current_auth_token)


@app.route('/delete-shipment/<shipment_id>', methods=['POST', 'GET'])
def deleteShipment(shipment_id):
    form = DeleteShipmentForm()
    login_key_hash = generate_password_hash(app.config['LOGIN_KEY'])
    if form.validate_on_submit():
        secret_code = form.secret_code.data
        confirm_checkbox = form.confirm.data
        if check_password_hash(login_key_hash, secret_code) and confirm_checkbox:
            try:
                delete_shipment = Shipment.query.get(shipment_id)
                db.session.delete(delete_shipment)
                db.session.commit()
                shutil.rmtree(
                    f'sms/static/shipments/{shipment_id}', ignore_errors=True)
                flash(_('Shipment was deleted successfully'), 'success')
            except BaseException as e:
                db.session.rollback()
                print('delete-shipment ERROR: '+str(e))

    return redirect(url_for('index'))


@app.route('/accept-shipment/<shipment_id>/<token>', methods=['POST', 'GET'])
def acceptShipment(shipment_id=None, token=None):
    form = AcceptShimentForm()
    if form.validate_on_submit():
        accept_checkbox = form.confirm.data
        try:
            shipment = Shipment.query.get(shipment_id)
            if accept_checkbox:
                shipment.accepted = True
                db.session.flush()
                db.session.commit()
                flash(_('Shipment was accepted successfully'), 'success')
                return redirect(url_for('showShipment', shipment_id=shipment_id, token=token))
        except BaseException as e:
            db.session.rollback()
            print('delete-shipment ERROR: '+str(e))

    return redirect(url_for('index'))


@app.route('/shipments-list')
@login_required
def shipmentsList():
    title = _("Shipments list")

    accepted_shipments = Shipment.query.order_by(
        Shipment.create_date).filter(Shipment.accepted == True).all()
    transit_shipments = Shipment.query.order_by(
        Shipment.create_date).filter(Shipment.accepted == False).all()
    return render_template('pages/shipment-list.html', title=title, accepted_shipments=accepted_shipments, transit_shipments=transit_shipments)


@app.route('/send-mail', methods=['POST', 'GET'])
def sendMail():
    if request.method == 'POST':
        subject = request.form['subject']
        return redirect(f'mailto:clowixoff@gmail.com?subject={subject}')


@app.errorhandler(404)
def page_404(e):
    return(render_template('pages/page404.html'))

@app.errorhandler(CSRFError)
def page_with_csrf_error(e):
    return redirect(url_for('index'))


# ** LANGUAGE CHANGER

language = 'ru'


@app.route('/lang-change/<lang>', methods=['POST', 'GET'])
def lang_change(lang=None):
    global language
    if lang == 'ru':
        language = 'ru'
    elif lang == 'en':
        language = 'en'
    return redirect(url_for('index'))


@babel.localeselector
def get_locale():
    global language
    return f'{language}'
