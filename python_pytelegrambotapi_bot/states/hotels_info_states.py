from telebot.handler_backends import State, StatesGroup


class UserStates(StatesGroup):
    CityInfo = State()
    DateInput = State()
    PriceRange = State()
    Distance = State()
    HotelsAmount = State()
    PhotosState = State()
    FinalState = State()
