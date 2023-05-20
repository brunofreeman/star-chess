const http = require("http");
const fs = require("fs");

let server = http.createServer(function(req, res) {
  if (req.method != "POST") {
    res.writeHead(400, {"Content-Type": "application/json"});
    res.end(JSON.stringify({
      "msg": `Expected POST, got ${req.method}.`,
      "req": JSON.parse(body),
      "err": ""
    }));
    return;
  }

  if (req.headers["Content-Type"] != "application/json") {
    res.writeHead(400, {"Content-Type": "application/json"});
    res.end(JSON.stringify({
      "msg": `Expected 'application/json', got ${req.headers["Content-Type"]}.`,
      "req": JSON.parse(body),
      "err": ""
    }));
    return;
  }

  let body = "";

  req.on("data", chunk => body += chunk);

  req.on("end", () => {
    try {
      let json = JSON.parse(body);

      let action = json["action"];

      switch (action) {
        case "submit": {
          let username = json["username"];
          let move = json["move"];
          let key = json["key"];

          let moveLogPath = `move-log-${username}.json`;

          let existed = fs.existsSync(moveLogPath);

          let fd = fs.openSync(moveLogPath, "w");

          if (!existed) {
            fs.writeSync(fd, JSON.stringify({}));
          }

          let moveLog = JOSN.parse(fs.readFileSync(moveLogPath));

          moveLog[key] = move;

          fs.writeSync(fd, JSON.stringify(moveLog));

          res.writeHead(200, {"Content-Type": "application/json"});
          res.end(JSON.stringify({
            "msg": `Move from '${username}' with key '${key}' successfully recorded.`
          }));
        } break;

        case "query": {
          let opponentUsername = json["opponentUsername"];
          let key = json["key"];

          let moveLogPath = `move-log-${opponentUsername}.json`;

          if (!fs.existsSync(moveLogPath)) {
            res.writeHead(400, {"Content-Type": "application/json"});
            res.end(JSON.stringify({
                "msg": `No move log found for '${opponentUsername}'.`,
                "req": JSON.parse(body),
                "err": ""
            }));
            return;
          }

          let moveLog = JOSN.parse(fs.readFileSync(moveLogPath));

          let move = moveLog[key];

          res.writeHead(200, {"Content-Type": "application/json"});
          res.end(JSON.stringify({
            "msg": `Move from '${opponentUsername}' with key '${key}' successfully found.`,
            "move": move
          }));
        } break;

        default: {
          res.writeHead(400, {"Content-Type": "application/json"});
          res.end(JSON.stringify({
            "msg": `Unknown action: ${action}.`,
            "req": JSON.parse(body),
            "err": ""
          }));
        } break;
      }
    } catch (err) {
      res.writeHead(400, {"Content-Type": "application/json"});
      res.end(JSON.stringify({
        "msg": "Server received and processed POST request!",
        "req": JSON.parse(body),
        "err": err.toString()
      }));
    }
  });  
});

server.listen();
