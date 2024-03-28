# sesam2

Working Draft of Sesam2, door opener

## Config

Aus .env oder anderswoher. Sollte so ausehen. die secret_keys können zbsp per `uuidgen` gemacht werden.
Die Werte hier sind Beispiele.

.env
```sh
export sesam2_database_url=sqlite:///db.sqlite3
export sesam2_secret_key=4e02e55f-c091-42cc-8168-3c0e2c07669c
export sesam2_jwt_secret_key=ace61533-7d03-45b5-b26a-3082ec21f460
```


## Testing

Testing is only done to give a frame in development. `sesam2/sesam2-backend $ pytest-watch test_from_the_front.py -- -x` to failfast `-x`
