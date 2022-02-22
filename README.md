# Rent-it

A house rent advertisement board.

Live demo - https://rent-it-ru.herokuapp.com

## Install

0. Install `python3`
1. Install dependencies: `pip install -r requirements.txt`
2. Run `pre-commit install` and `pre-commit install --hook-type pre-push`
3. Rename `.env.template` to `.env` in `config` directory and fill it
4. Run `python manage.py makemigrations rentitapp accounts payments subscriptions`
5. Run `python manage.py migrate`
6. Run `python manage.py runserver`
7. Go to http://127.0.0.1:8000

To use payments:
1. Setup [ngrok](https://ngrok.com/) and start it `ngrok http 8000`
2. Put your ngrok forwarding domain to `DOMAIN_NAME` field in `.env`.
3. Make a test account on [Yookassa](https://yookassa.ru/developers) and fill `.env` fields with your credentials.

###Tests
Run `pytest`

## Author

[Bulent Ozcan](https://github.com/air17)
