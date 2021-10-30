import datetime as dt
from fastapi import FastAPI, HTTPException, Query

from database import engine, Session, Base, City, User, Picnic, PicnicRegistration
from external_requests import CityList
from models import RegisterUserRequest, UserModel, PicnicRegistrationModal, PicnicModal
from fastapi import FastAPI
import logging
import sys

# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)
# fileHandler = logging.FileHandler('/logs/logs.log')
# fileHandler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
# logger.addHandler(fileHandler)
# streamHandler = logging.StreamHandler(stream=sys.stdout)
# streamHandler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
# logger.addHandler(streamHandler)
# logging.debug('Error')
# logging.info('Information message')
# logging.warning('Warning')

app = FastAPI()


@app.post('/cities/', summary='Create City', description='Создание города по его названию')
def create_city(city: str = Query(description="Название города", default=None)):
    if city is None:
        raise HTTPException(status_code=400, detail='Параметр city должен быть указан')
    check = CityList()
    if not check.check_existing(city):
        raise HTTPException(status_code=400, detail='Параметр city должен быть существующим городом')

    city_object = Session().query(City).filter(City.name == city.capitalize()).first()
    if city_object is None:
        city_object = City(name=city.capitalize())
        s = Session()
        s.add(city_object)
        s.commit()

    return {'id': city_object.id, 'name': city_object.name, 'weather': city_object.weather}


@app.get('/cities/', summary='Get Cities')
def cities_list(query: str = Query(description="Название города", default=None)):
    """
    Получение списка городов
    Фильтр реализован только лишь по точному совпадению (((
    переделать, желательно поиск по части без регистра
    """

    if query:
        cities = Session().query(City).filter(City.name == query).all()
    else:
        cities = Session().query(City).all()

    return [{'id': city.id, 'name': city.name, 'weather': city.weather} for city in cities]


@app.get('/users/', summary='')
def users_list(min_age: int = Query(description="Минимальный возраст", default=1, gt=0, le=1000),
               max_age: int = Query(description="Максимальный возраст", default=1000, gt=0, le=1000)):
    """
    Список пользователей
    Добавлена возможность выбора диапозона возраста
    """
    users = Session().query(User).filter(User.age >= min_age, User.age <= max_age).all()
    return [{
        'id': user.id,
        'name': user.name,
        'surname': user.surname,
        'age': user.age,
    } for user in users]


@app.post('/users/', summary='CreateUser', response_model=UserModel)
def register_user(user: RegisterUserRequest):
    """
    Регистрация пользователя
    """
    user_object = User(**user.dict())
    s = Session()
    s.add(user_object)
    s.commit()

    return UserModel.from_orm(user_object)


def filter_set(pic_id, list_in):
    list_out = []
    for record in list_in:
        if record.picnic_id == pic_id:
            list_out.append(record)

    return list_out


@app.get('/picnic/', summary='All Picnics', tags=['picnic'])
def all_picnics(datetime: dt.datetime = Query(default=None, description='Время пикника (по умолчанию не задано)'),
                past: bool = Query(default=True, description='Включая уже прошедшие пикники')):
    """
    Список всех пикников
    """
    # picnics = picnics.join(Picnic, Picnic.city_id == City.id)
    # picnics = picnics.join(PicnicRegistration, PicnicRegistration.picnic_id == Picnic.id)
    # picnics = Session().query(Picnic) \
    #     .filter(Picnic.time > datetime) \
    #     .options(joinedload(Picnic.registrations).joinedload(PicnicRegistration.user), joinedload(Picnic.city)) \
    #     .all()
    picnicregistr = Session().query(PicnicRegistration).all()
    picnics = Session().query(Picnic).all()
    if datetime is not None:
        picnics = Session().query(Picnic).filter(Picnic.time == datetime).all()
    if not past:
        picnics = Session().query(Picnic).filter(Picnic.time >= dt.datetime.now()).all()
    return [{
        'id': pic.id,
        'city': pic.city.name,
        'time': pic.time,
        'users': [
            {
                'id': pr.user.id,
                'name': pr.user.name,
                'surname': pr.user.surname,
                'age': pr.user.age,
            }
            for pr in filter_set(pic.id, picnicregistr)],
    } for pic in picnics]


@app.post('/picnic/', summary='Picnic Add', tags=['picnic'])
def picnic_add(picnic: PicnicModal):
    picnic_object = Picnic(**picnic.dict())
    s = Session()
    s.add(picnic_object)
    s.commit()

    return PicnicModal.from_orm(picnic_object)


@app.post('/picnic/register/', summary='Picnic Registration', tags=['picnic'])
def register_to_picnic(picnic: PicnicRegistrationModal):
    """
    Регистрация пользователя на пикник
    (Этот эндпойнт необходимо реализовать в процессе выполнения тестового задания)
    """
    # TODO: Сделать логику
    picnic_registr_object = PicnicRegistration(**picnic.dict())
    s = Session()
    s.add(picnic_registr_object)
    s.commit()

    return PicnicRegistrationModal.from_orm(picnic_registr_object)
