Generate self-signed key:
```
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

And use with gunicorn:
```
gunicorn --certfile=cert.pem --keyfile=key.pem --bind 0.0.0.0:443 main:app
``` 

Put in ``/etc/supervisord.conf`` (see https://supervisord.org)
```
[program:gunicorn-issues]
command=gunicorn main:app
directory=/Code/ghi
user=nobody
autostart=true
autorestart=true
redirect_stderr=true
```