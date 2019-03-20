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
command=bash -c "source /home/ihb/anaconda3/bin/activate flaskwebview && gunicorn -b 0.0.0.0:4000 main:app"
directory=/home/ihb/Code/ghi
user=ihb
autostart=true
autorestart=true
redirect_stderr=false
stdout_logfile=/tmp/super_stdout
```

0. Install supervisor with apt
1. Make a sample conf file with echo_supervisord_conf (see http://supervisord.org/installing.html#creating-a-configuration-file)
2. Append above chunk, copy to ``/etc/supervisord.conf``
3. ``sudo service supervisor restart``
4. Tail ``/tmp/supervisord.log`` to see what happened with supervisor, also check ``stdout_logfile`` for more information
