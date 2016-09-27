import web
import redis
import json

db = redis.StrictRedis(host='localhost', port=4747, db=0)

urls = (
    '/api', 'new_user',
    '/api/(.+)', 'api_access'
)

class EchoServer(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))

# For complete functionality, need to implement new user
class new_user:
    def POST(self):
        data = web.data()
        response = "{'test': 'hello'}"
        return response

class api_access:
    def POST(self, name):
        return format(name)

    def GET(self, name):
        if "lights/" in name:
            id = name.rsplit("/", 1)[-1]
            device = db.get("hue_" + str(id))
            state = db.get(device).lower()
            response = "{\"state\": {\"on\": " + state + ", \"bri\": 0, \"alert\": \"none\",\"effect\": \"none\"," + \
                       "\"reachable\": true }, \"type\": \"Dimmable light\",\"name\": \"" + device + "\"" + \
                       ",\"modelid\": \"LWB004\",\"swversion\": \"66012040\"}"
        else:
            web_sensor_lookup = {}
            sensor_id = 1

            sensors = db.lrange("sensors", 0, -1)
            for sensor in sensors:
                sensor = json.loads(sensor)
                if sensor["type"] in ["zwave", "wifi"] and sensor["function"] in ["switch", "dimmer"]:
                    web_sensor_lookup[str(sensor_id)] = sensor["name"]
                    db.set("hue_" + str(sensor_id), sensor["name"])
                    sensor_id += 1

            response = "{"
            for id, sensor in web_sensor_lookup.iteritems():
                response += "\"" + id + "\":{\"state\": {\"on\": false,\"bri\": 0,\"alert\":\"none\",\"effect\":" + \
                            "\"none\",\"reachable\": true},\"type\": \"Dimmable light\",\"name\":\"" + sensor + \
                            "\",\"modelid\": \"LWB004\", \"swversion\": \"66012040\" },"
            response = response[:-1]
            response += "}"
        return response

    def PUT(self, name):
        name = name[:-6]
        id = name.rsplit("/", 1)[-1]
        data = web.data()
        state = json.loads(data)["on"]
        db.lpush("sensor_changes", "{\"name\": \"" + db.get("hue_" + str(id)) + "\", \"state\": \"" + str(state) + "\"}")
        response = "[{\"success\":{\"/lights/" + str(id) + "/state/on\":" + str(state).lower() + "}}]"
        return response


if __name__ == "__main__":
    app = EchoServer(urls, globals())
    app.run()

