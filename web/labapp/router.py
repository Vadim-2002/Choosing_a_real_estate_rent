# Подключаем объект приложения Flask из __init__.py
from labapp import app
# Подключаем библиотеку для "рендеринга" html-шаблонов из папки templates
from flask import render_template, make_response, request, jsonify

import labapp.webservice as webservice   # подключаем модуль с реализацией бизнес-логики обработки запросов

"""
    Модуль регистрации обработчиков маршрутов, т.е. здесь реализуется обработка запросов
    при переходе пользователя на определенные адреса веб-приложения
"""

value_category = None
value_sort = ""
str_of_columns = "bedroom, localities.name, property_types.name, price, area, cities.name, categories.category"
str_join = "JOIN localities on localities.id = rent_real_estate.locality JOIN property_types on property_types.id = rent_real_estate.property_type JOIN cities on cities.id = rent_real_estate.city JOIN categories on categories.id = rent_real_estate.category"
str_col_names = 'bedroom, locality, property_type, price, area, city, category'
num_page = 0


def soring_by_price():
    global value_sort

    if request.form.get('sort') == 'price_decrease':
        value_sort = "DESC"
    elif request.form.get('sort') == 'price_increase':
        value_sort = "ASC"


def price_category():
    global value_category

    if request.form.get('price_category') == 'min_price':
        value_category = 1
    elif request.form.get('price_category') == 'average_price':
        value_category = 2
    elif request.form.get('price_category') == 'max_price':
        value_category = 3


def column_selection():
    global str_of_columns
    global str_join
    global str_col_names

    if request.form.get('but_cat') == 'Выбрать':
        str_of_columns = ""
        str_col_names = ""
        str_join = ""

        if request.form.get('cb_cat_1') == 'Bedroom':
            str_of_columns += 'bedroom, '
            str_col_names += 'bedroom, '
        if request.form.get('cb_cat_2') == 'Locality':
            str_of_columns += 'localities.name, '
            str_col_names += 'locality, '
            str_join += 'JOIN localities on localities.id = rent_real_estate.locality '

        if request.form.get('cb_cat_3') == 'Property_type':
            str_of_columns += 'property_types.name, '
            str_col_names += 'property, '
            str_join += 'JOIN property_types on property_types.id = rent_real_estate.property_type '
        str_of_columns += 'price, '
        str_col_names += 'price, '
        if request.form.get('cb_cat_4') == 'Area':
            str_of_columns += 'area, '
            str_col_names += 'area, '
        if request.form.get('cb_cat_5') == 'City':
            str_of_columns += 'cities.name, '
            str_col_names += 'city, '
            str_join += 'JOIN cities on cities.id = rent_real_estate.city '
        str_of_columns += 'categories.category'
        str_col_names += 'category, '
        str_join += 'JOIN categories on categories.id = rent_real_estate.category'


def changing_the_page():
    global num_page

    if request.form.get('page_last') == 'Предыдущая страница':
        if num_page > 0:
            num_page -= 1

    if request.form.get('page_next') == 'Следующая страница':
        if num_page < 3860:
            num_page += 1


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    """ Обработка запроса к индексной странице """
    # Пример вызова метода с выборкой данных из БД и вставка полученных данных в html-шаблон
    processed_files = webservice.get_sorting_files(str_of_columns, value_category, value_sort, str_join, num_page)

    if request.method == 'POST':
        price_category()

        column_selection()

        soring_by_price()

        changing_the_page()

        processed_files = webservice.get_sorting_files(str_of_columns, value_category, value_sort, str_join, num_page)

    return render_template('index.html',
                           title='Renta',
                           page_name='HOME',
                           navmenu=webservice.navmenu,
                           processed_files=processed_files,
                           num_page=num_page,
                           name_of_columns=str_col_names.split(","))


@app.route('/contact', methods=['GET'])
def contact():
    """ Обработка запроса к странице contact.html """
    return render_template('contact.html',
                           title='Contacts',
                           page_name='CONTACT US',
                           navmenu=webservice.navmenu)


@app.route('/about', methods=['GET'])
def about():
    """ Обработка запроса к странице about.html """
    return render_template('about.html',
                           title='About project',
                           page_name='about',
                           navmenu=webservice.navmenu)

@app.route('/data/<int:source_file_id>', methods=['GET'])
def get_data(source_file_id: int):
    """
        Вывод данных по идентификатору обработанного файла.
        Функция также пытается получить значение GET-параметра pageNum
        из запроса типа: http://127.0.0.1:8000/data/16?pageNum=2
    """
    processed_data = []
    pageNum = request.args.get('pageNum')
    if pageNum is not None:
        processed_data = webservice.get_processed_data(source_file=source_file_id, page_num=int(pageNum))
    else:
        processed_data = webservice.get_processed_data(source_file=source_file_id)
    return render_template('data.html',
                           title='MY BEST WEBSERVICE!!1',
                           page_name=f'DATA_FILE_{source_file_id}',
                           navmenu=webservice.navmenu,
                           processed_data=processed_data)


@app.route('/api/contactrequest', methods=['POST'])
def post_contact():
    """ Пример обработки POST-запроса для демонстрации подхода AJAX (см. formsend.js и ЛР№5 АВСиКС) """
    request_data = request.json     # получаeм json-данные из запроса
    # Если в запросе нет данных или неверный заголовок запроса (т.е. нет 'application/json'),
    # или в этом объекте, например, не заполнено обязательное поле 'firstname'
    if not request_data or request_data['firstname'] == '':
        # возвращаем стандартный код 400 HTTP-протокола (неверный запрос)
        return bad_request()
    # Иначе отправляем json-ответ с сообщением об успешном получении запроса
    else:
        msg = request_data['firstname'] + ", ваш запрос получен !"
        return jsonify({'message': msg})


@app.route('/notfound', methods=['GET'])
def not_found_html():
    """ Возврат html-страницы с кодом 404 (Не найдено) """
    return render_template('404.html', title='404', err={'error': 'Not found', 'code': 404})


def bad_request():
    """ Формирование json-ответа с ошибкой 400 протокола HTTP (Неверный запрос) """
    return make_response(jsonify({'message': 'Bad request !'}), 400)
