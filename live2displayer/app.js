import express from 'express';
import ejs from 'ejs';
import { fileURLToPath } from 'url';
import path from 'path';
import { WebSocket } from 'ws';
import { createProxyMiddleware } from 'http-proxy-middleware';
import open from 'open';
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const config = {
  port: 3000,
  birespiEventExporterUrl: "http://localhost:8765",
  birespiBackendUrl: "http://localhost:8000",
}

app.listen(
  config.port
  , () => {
    console.log("服务已启动，监听端口：" + config.port);
    console.log("请打开浏览器访问：http://localhost:" + config.port);
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
app.get('/proxy', async (req, res) => {
  console.log("req.query");
  console.log(req.query.url);

  const imageUrl = req.query.url;
  console.log(`Proxying image: ${imageUrl}`);
  if (!imageUrl) {
    return res.status(400).send('Missing url parameter');
  }

  try {
    const response = await fetch(imageUrl);

    if (!response.ok) {
      console.log(`Failed to fetch image: ${response.statusText}`);
      throw new Error(`Failed to fetch image: ${response.statusText}`);
    }

    const contentType = response.headers.get('content-type');
    res.set('Content-Type', contentType);
    console.log(`Content-Type: ${contentType}`);

    const arrayBuffer = await response.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    res.send(buffer);

  } catch (error) {
    console.log(`Error fetching image: ${error.message}`);
    res.status(500).send(`Error fetching image: ${error.message}`);
  }
});
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

setTimeout(() => {
  // 打开浏览器打开页面
  open('http://localhost:' + config.port);
}, 1000);