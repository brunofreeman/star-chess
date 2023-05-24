const http = require("http");
const fs = require("fs");

function reqJSON(req) {
  return {
    "method": req.method,
    "headers": req.headers
  }
}

function logPath(username) {
  return `move-log-${username}.json`;
}

let server = http.createServer(function(req, res) {
  if (req.method != "POST") {
    res.writeHead(400, {"content-type": "application/json"});
    res.end(JSON.stringify({
      "msg": `Expected 'POST', got '${req.method}'.`,
      "req": reqJSON(req)
    }));
    return;
  }

  if (req.headers["content-type"] != "application/json") {
    res.writeHead(400, {"content-type": "application/json"});
    res.end(JSON.stringify({
      "msg": `Expected 'application/json', got '${req.headers["content-type"]}'.`,
      "req": reqJSON(req)
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

          let moveLogPath = logPath(username);

          let existed = fs.existsSync(moveLogPath);

          if (!existed) {
            fs.writeFileSync(moveLogPath, JSON.stringify({}));
          }

          let moveLog = JSON.parse(fs.readFileSync(moveLogPath));

          moveLog[key] = move;

          fs.writeFileSync(moveLogPath, JSON.stringify(moveLog));

          res.writeHead(200, {"content-type": "application/json"});
          res.end(JSON.stringify({
            "msg": `Move from '${username}' with key '${key}' successfully recorded.`
          }));
        } break;

        case "query": {
          let username = json["username"];
          let key = json["key"];

          let moveLogPath = logPath(username);

          if (!fs.existsSync(moveLogPath)) {
            res.writeHead(404, {"content-type": "application/json"});
            res.end(JSON.stringify({
                "msg": `No move log found for '${username}'.`,
                "req": reqJSON(req),
                "body": json
            }));
            return;
          }

          let moveLog = JSON.parse(fs.readFileSync(moveLogPath));

          if (!moveLog.hasOwnProperty(key)) {
            res.writeHead(404, {"content-type": "application/json"});
            res.end(JSON.stringify({
                "msg": `Move from '${username}' with key '${key}' not found in log.`,
                "req": reqJSON(req),
                "body": json
            }));
            return;
          }

          let move = moveLog[key];

          res.writeHead(200, {"content-type": "application/json"});
          res.end(JSON.stringify({
            "msg": `Move from '${username}' with key '${key}' successfully found.`,
            "move": move
          }));
        } break;

        case "clear": {
          let username = json["username"];

          let moveLogPath = logPath(username);

          if (fs.existsSync(moveLogPath)) {
            fs.unlinkSync(moveLogPath);
          }
  
          res.writeHead(200, {"content-type": "application/json"});
          res.end(JSON.stringify({
            "msg": `Move log for '${username}' successfully cleared.`
          }));
        } break;

        case "save": {
          let username = json["username"];
          let moveLogPath = logPath(username);

          if (fs.existsSync(moveLogPath)) {
            let savedLogsDir = "saved-logs";
            if (!fs.existsSync(savedLogsDir)) {
              fs.mkdirSync(savedLogsDir);
            }
            
            fs.copyFileSync(
              moveLogPath, `${savedLogsDir}/${Date.now()}-${moveLogPath}`);

            res.writeHead(200, {"content-type": "application/json"});
            res.end(JSON.stringify({
              "msg": `Move log for '${username}' successfully saved.`
            }));
          } else {
            res.writeHead(404, {"content-type": "application/json"});
            res.end(JSON.stringify({
                "msg": `No log found for '${username}' to save.`,
                "req": reqJSON(req),
                "body": json
            }));
          }
        } break;

        default: {
          res.writeHead(400, {"content-type": "application/json"});
          res.end(JSON.stringify({
            "msg": `Unknown action: '${action}'.`,
            "req": reqJSON(req),
            "body": json,
            "err": ""
          }));
        } break;
      }
    } catch (err) {
      res.writeHead(400, {"content-type": "application/json"});
      res.end(JSON.stringify({
        "msg": "Server error encountered when processing POST request.",
        "req": reqJSON(req),
        "body": body,
        "err": err.toString()
      }));
    }
  });  
});

server.listen();
