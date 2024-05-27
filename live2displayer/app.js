const express = require("express");
const ejs = require('ejs');
const WebSocket = require('ws');
const app = express();
const { createProxyMiddleware } = require('http-proxy-middleware');

const config = {
  birespiEventExporterUrl: "http://localhost:8765",
  birespiBackendUrl: "http://localhost:8000",
}

app.listen(3000, () => {
  console.log("Application started and Listening on port 3000");
  console.log("请打开浏览器，访问 http://localhost:3000 ");
});
app.use(express.static(__dirname));

app.engine('html', ejs.__express);
app.set('view engine', 'html');

app.get("/", (req, res) => {
  res.render(__dirname + "/index");
});
app.use('/birespi-api', createProxyMiddleware({
  target: config.birespiBackendUrl,
  changeOrigin: true,
  pathRewrite: {
    '^/birespi-api': '', // 去掉 /birespi-api 前缀
  },
}));

app.get("/event-stream", (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  live2dPlayerMap[req.query.uuid] = res;

  req.on('close', () => {
    res.end();
    delete live2dPlayerMap[req.query.uuid];
  });
});

function connectBirespi() {
  console.log(`Connecting to ${config.birespiEventExporterUrl}`);
  const ws = new WebSocket(config.birespiEventExporterUrl);

  ws.on('open', function open() {
    console.log(`WebSocket(\'${config.birespiEventExporterUrl}\') connected`);
  });

  ws.on('message', function message(data) {
    data = JSON.parse(data);
    data.soundFullUrl = `${config.birespiBackendUrl}/sound/${data.sound}`;
    console.log(data);
    sendEventToAll(data);
  });

  ws.on('close', function close() {
    console.log(`WebSocket(\'${config.birespiEventExporterUrl}\') disconnected`);
    setTimeout(connectBirespi, 1000); // 等待1秒后重连
  });

  ws.on('error', function error(err) {
    console.error('WebSocket error:', err);
    ws.close();
  });
}

const live2dPlayerMap = {};

function sendEvent(res, data) {
  res.write(`data: ${JSON.stringify(data)}\n\n`);
}

function sendEventToAll(data) {
  for (let key in live2dPlayerMap) {
    sendEvent(live2dPlayerMap[key], data);
  }
}

connectBirespi();
