from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
import datetime
from flask import Flask, render_template, request, redirect, url_for
import sqlite3 as sql
from random import randint
from flask_mobility import Mobility

#привет, прочти файл readme.txt в корне

application = Flask(__name__)
Mobility(application)

# объявляю переменные на будущее чтоб не ругался
dbdic = {'login': 'password'}
payment = ''
instagram = ''
price = ''
select_2 = ''
select_4 = ''
select_6 = ''
sort_by = 'c_r_date'
sort_by_check = {
    'c_id': '',
    'c_name': '',
    'c_instagram': '',
    'c_phone': '',
    'c_email': '',
    'product': '',
    'c_r_date': 'checked',
    'period': '',
    'price': '',
    'c_p_time': '',
    'verify': '',
    'c_endtime': '',
}
#                   BEGIN НА БУДУЩЕЕ
# config

application.config.update(
    SECRET_KEY='***'
)

# flask-login
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'admin'


# simple user model
class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = 'user' + str(id)
        self.password = self.name + '_secret'

    def __repr__(self):
        return '%d/%s/%s' % (self.id, self.name, self.password)


# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    return User(userid)
#                   END НА БУДУЩЕЕ


# id_generator, генерим id записи, проверяем есть ли он в базе, если есть, генерим снова, рекурсия, по идее не упадёт
def id_gen():
    c_id = randint(0, 1000000)
    with sql.connect('book.db') as con:
        cur = con.cursor()
        cur.execute(f'SELECT * FROM book2 WHERE c_id = {c_id}')
        rows = cur.fetchall()
    if rows:
        id_gen()
    else:
        return c_id


# ЛОГИН. Проверяем, логин ли, если логин, отправляем в менагер, если нет, начинай сначала
@application.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        try:
            some_login = request.form.get('login')
            some_password = request.form.get('password')
            if dbdic[some_login] == some_password:
                return render_template('manager.html')
        except:
            return render_template('login.html')
    return render_template('login.html')


# выводим менагер с логина
@application.route('/manager', methods=['POST', 'GET'])
@login_required
def manager():
    return render_template('manager.html')


# рут, если с мобилы - мобильная версия, если нет, десктопная, и чтоб в ссылке /studio была
@application.route('/studio', methods=['POST', 'GET'])
def studio():
    if request.MOBILE:
        index_m()
        return render_template('index_m.html')
    else:
        index_d()
        return render_template('index_d.html')


@application.route('/', methods=['POST', 'GET'])
def index():
    return redirect(url_for('studio'))


@application.route('/book', methods=['POST', 'GET'])  # СТРАНИЧКА С УЧЕТОМ
def book():
    if request.method == 'POST':
        try:
            c_id = id_gen()  # присваиваем случайный ID от 0 до 1000000
            c_name = request.form['c_name']  # обязательное
            c_instagram = request.form['c_instagram']  # обязательное
            c_phone = request.form['c_phone']  # обязательное
            c_email = request.form['c_email']  # обязательное
            product = request.form['product']  # обязательное
            c_r_date = str(request.form['c_r_date'])  # обязательное
            period = request.form['period']  # обязательное
            price = request.form['price']  # обязательное

            try:
                c_p_time = request.form['c_p_time']  # не обязательное
                c_p_verify = request.form['c_p_verify']  # не обязательное
                if c_p_verify == 'on':
                    c_p_verify = 'checked'
                c_endtime = str(request.form['c_endtime'])  # не обязательное
            except:
                c_p_time = ''
                c_p_verify = ''
                c_endtime = ''

            # if с_p_verify == 'Да' and ((c_p_time == '') or (c_endtime == '')):
            #     c_p_verify = 'Нет'
            # if с_p_verify == 'Yes':
            #     c_p_verify = 'Да'

            with sql.connect('book.db') as con:
                cur = con.cursor()
                cur.execute(
                    'INSERT INTO book2 (c_id,c_name,c_instagram,c_phone,c_email,product,c_r_date,period,price,c_p_time,verify,c_endtime) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                    (
                        c_id, c_name, c_instagram, c_phone, c_email, product, c_r_date, period, price, c_p_time,
                        c_p_verify,
                        c_endtime))
                con.commit()
        except:
            con.rollback()

        finally:
            return render_template('book.html')

    else:
        return render_template('book.html')


# ВЫВОДИТ БАЗУ НА СТРАНИЦЕ УЧЕТА TODO ПРИКРУТИТЬ СЮДА ТОКЕН ПАРОЛЯ ЕСЛИ ЗАПЛАТЯТ
@application.route('/lister', methods=['POST', 'GET'])
def lister():
    con = sql.connect('book.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute(f'SELECT * FROM book2 ORDER BY c_r_date;')
    rows = cur.fetchall()

    if request.method == 'POST':
        try:
            con = sql.connect('book.db')
            cur = con.cursor()
            cur.execute('SELECT * FROM book2')
            db_list = cur.fetchall()
            for i in db_list:
                try:
                    c_id = request.form[f'c_id_{i[0]}']  # не обязательное
                    c_name = request.form[f'c_name_{i[0]}']  # не обязательное
                    c_instagram = request.form[f'c_instagram_{i[0]}']  # не обязательное
                    c_phone = request.form[f'c_phone_{i[0]}']  # не обязательное
                    c_email = request.form[f'c_email_{i[0]}']  # не обязательное
                    product = request.form[f'product_{i[0]}']  # не обязательное
                    c_r_date = request.form[f'c_r_date_{i[0]}']  # не обязательное
                    period = request.form[f'period_{i[0]}']  # не обязательное
                    price = request.form[f'price_{i[0]}']  # не обязательное
                    try:
                        global sort_by
                        sort_by = str(request.form['sort'])
                        global sort_by_check
                        if sort_by_check[sort_by] == '':
                            for key in sort_by_check:
                                sort_by_check[key] = ''
                            sort_by_check[sort_by] = 'checked'
                    except:
                        pass
                    try:
                        c_p_time = request.form[f'c_p_time_{i[0]}']  # не обязательное
                        c_p_verify = request.form[f'verify_{i[0]}']  # не обязательное
                        if c_p_verify == 'on':
                            c_p_verify = 'checked'
                        c_endtime = request.form[f'c_endtime_{i[0]}']  # не обязательное
                    except:
                        c_p_time = ''
                        c_p_verify = 'off'
                        c_endtime = ''
                    try:
                        # c_id, c_name, c_instagram, c_phone, c_email, product, c_r_date, period, price, c_p_time, c_p_verify, c_endtime
                        with sql.connect('book.db') as con:
                            cur = con.cursor()
                            cur.execute(
                                'UPDATE book2 SET c_name=?, c_instagram=?, c_phone=?, c_email=?, product=?, c_r_date=?, period=?, price=?, c_p_time=?, verify=?, c_endtime=? WHERE c_id=?',
                                (c_name, c_instagram, c_phone, c_email, product, c_r_date, period, price, c_p_time,
                                 c_p_verify, c_endtime, int(c_id)))
                            con.commit()
                    except:
                        con.rollback()
                except:
                    con.rollback()
        except:
            con.rollback()
        finally:
            con = sql.connect('book.db')
            con.row_factory = sql.Row
            cur = con.cursor()
            try:
                # global sort_by
                cur.execute(f'SELECT * FROM book2 ORDER BY {sort_by}')
            except:
                cur.execute(f'SELECT * FROM book2 ORDER BY c_r_date')
            rows = cur.fetchall()
            return render_template('lister.html', rows=rows, chk=sort_by_check)
    return render_template('lister.html', rows=rows, chk=sort_by_check)


# подстраничник удаления записи
@application.route('/delid', methods=['POST', 'GET'])
def delid():
    if request.method == 'POST':
        try:
            c_id = request.form['del_c_id']
            con = sql.connect('book.db')
            cur = con.cursor()
            cur.execute('DELETE FROM book2 WHERE c_id=?', (c_id,))
            con.commit()
        except:
            pass
        finally:
            return render_template('delid.html')

    else:
        return render_template('delid.html')


@application.route('/index_m', methods=['POST', 'GET'])  # ВЫВОДИТ МОБИЛЬНУЮ ВЕРСИЮ САЙТА
def index_m():
    if request.method == 'POST':
        try:
            c_id = id_gen()
            c_name = request.form['name']
            c_instagram = request.form['instagram']
            global instagram
            instagram = c_instagram
            c_phone = request.form['phone']
            c_email = request.form['email']
            product = request.form['product']
            c_r_date = datetime.date.today()
            period = request.form['period']
            global price
            if int(period) == 4:
                price = 2000
            elif int(period) == 8:
                price = 4000
            elif int(period) == 12:
                price = 6000
            else:
                price = ''
            c_p_time = ''
            c_p_verify = ''
            c_endtime = ''
            with sql.connect('book.db') as con:
                cur = con.cursor()
                cur.execute(
                    'INSERT INTO book2 (c_id,c_name,c_instagram,c_phone,c_email,product,c_r_date,period,price,c_p_time,verify,c_endtime) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                    (
                        c_id, c_name, c_instagram, c_phone, c_email, product, c_r_date, period, price, c_p_time,
                        c_p_verify,
                        c_endtime))
                con.commit()
            global payment
            payment = str(request.form['payment'])
            return render_template('index_m.html')
        except:
            pass


@application.route('/index_d', methods=['GET', 'POST'])  # ВЫВОДИТ ДЕСКТОПНУЮ ВЕРСИЮ САЙТА
def index_d():
    if request.method == 'POST':
        try:
            c_id = id_gen()
            c_name = request.form['name']
            c_instagram = request.form['instagram']
            global instagram
            instagram = c_instagram
            c_phone = request.form['phone']
            c_email = request.form['email']
            product = request.form['product']
            c_r_date = datetime.date.today()
            period = request.form['period']
            global price
            if int(period) == 4:
                price = 2000
            elif int(period) == 8:
                price = 4000
            elif int(period) == 12:
                price = 6000
            else:
                price = ''
            c_p_time = ''
            c_p_verify = ''
            c_endtime = ''
            with sql.connect('book.db') as con:
                cur = con.cursor()
                cur.execute(
                    'INSERT INTO book2 (c_id,c_name,c_instagram,c_phone,c_email,product,c_r_date,period,price,c_p_time,verify,c_endtime) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                    (
                        c_id, c_name, c_instagram, c_phone, c_email, product, c_r_date, period, price, c_p_time,
                        c_p_verify,
                        c_endtime))
                con.commit()
            global payment
            payment = str(request.form['payment'])
            return render_template('index_d.html')
        except:
            pass


@application.route('/yoomoney', methods=['POST', 'GET'])  # ЮМАНИ
def yoomoney():
    return render_template('yoomoney.html', instagram=instagram, price=price)


@application.route('/paypal', methods=['POST', 'GET'])  # paypal
def paypal():
    return render_template('paypal.html', instagram=str(instagram), price=price, select_2=select_2, select_4=select_4, select_6=select_6)


@application.route('/payment', methods=['POST', 'GET'])  # юмани или пайпал будут платить
def payment_what():
    if payment == 'yoo':
        yoomoney()
        return render_template('yoomoney.html', instagram=instagram, price=price)
    elif payment == 'pal':
        return redirect(url_for('https://www.paypal.com/paypalme/polinamatei', _external=True))


@application.route('/recieve', methods=['POST', 'GET'])  # получатель данных с глагне
def recieve():
    if request.method == 'POST':
        try:
            c_id = id_gen()
            c_name = request.form['name']
            c_instagram = request.form['instagram']
            global instagram
            instagram = c_instagram
            c_phone = request.form['phone']
            c_email = request.form['email']
            product = request.form['product']
            c_r_date = datetime.date.today()
            period = request.form['period']
            global price
            if int(period) == 4:
                price = 2000
            elif int(period) == 8:
                price = 4000
            elif int(period) == 12:
                price = 6000
            else:
                price = ''
            c_p_time = ''
            c_p_verify = ''
            c_endtime = ''
            with sql.connect('book.db') as con:
                cur = con.cursor()
                cur.execute(
                    'INSERT INTO book2 (c_id,c_name,c_instagram,c_phone,c_email,product,c_r_date,period,price,c_p_time,verify,c_endtime) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                    (
                        c_id, c_name, c_instagram, c_phone, c_email, product, c_r_date, period, price, c_p_time,
                        c_p_verify,
                        c_endtime))
                con.commit()
            global payment
            payment = str(request.form['payment'])
            if payment == 'yoo':
                yoomoney()
                return render_template('yoomoney.html', instagram=instagram, price=price)
            elif payment == 'pal':
                select_2 = ''
                select_4 = ''
                select_6 = ''
                if int(price) == 2000:
                    select_2 = 'selected'
                elif int(price) == 4000:
                    select_4 = 'selected'
                elif int(price) == 6000:
                    select_6 = 'selected'
                else:
                    return render_template('paypal.html', instagram=str(instagram), price=price, select_2=select_2, select_4=select_4, select_6=select_6)
            return redirect('/')
        except:
            return redirect('/')


# чтоб работало
if __name__ == '__main__':
    application.run(host='0.0.0.0')
