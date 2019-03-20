Generate self-signed key:
```
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

And use with gunicorn:
```
gunicorn --certfile=cert.pem --keyfile=key.pem --bind 0.0.0.0:443 main:app
``` 

Chunk for ``/etc/supervisord.conf`` (see https://supervisord.org)
```
[program:gunicorn-issues]
command=bash -c "source activate flaskwebview && gunicorn -b 0.0.0.0:4000 main:app"
directory=Code/ghi
user=ihb
autostart=true
autorestart=true
redirect_stderr=true
```

0. Install supervisor with apt
1. Make a sample conf file with echo_supervisord_conf (see http://supervisord.org/installing.html#creating-a-configuration-file)
2. Append above chunk, copy to ``/etc/supervisord.conf``
3. ``supervisorctl restart all``
4. Tail ``/tmp/supervisord.log`` to see what happened
