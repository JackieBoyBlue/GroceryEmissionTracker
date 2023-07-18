
# GroceryEmissionTracker

### Before running, please ensure that the following environment variables are set:
- CLIENT_ID
- CLIENT_SECRET

You may also wish to set:
- SECRET_KEY
- ADMIN_NAME
- ADMIN_EMAIL
- ADMIN_PASSWORD

All admin fields default to "admin".

---

## Installation with pipenv

- Make sure you have pipenv installed:
```
pip install pipenv --user
```

- Then run the following in the base directory:
```
pipenv install
pipenv shell
python wsgi.py
```
