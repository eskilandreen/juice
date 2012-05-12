import web
import json
import random
import uuid
import hashlib

urls = (
    '/generate', 'generate',
    '/get/(\w+)', 'get',
)
app = web.application(urls, globals())

lookup = {}

def generate_random_ingredients():
    all_ingr = [x.strip() for x in file('ingredients.juice')]
    ret = {}
    for k in range(10):
        fruit = random.choice(all_ingr)
        if fruit in ret:
            ret[fruit] += 100
        else:
            ret[fruit] = 100
    return sorted(ret.items())

class generate:
    def GET(self):
        ingr = generate_random_ingredients()
        id = hashlib.md5(repr(ingr)).hexdigest()
        lookup[id] = ingr
        return json.dumps({
            'id': id,
            'ingredients': dict(ingr)
        }, indent=4)

class get:
    def GET(self, id):
        try:
            ingr = lookup[id]
            return json.dumps({
                'id': id,
                'ingredients': dict(ingr)
            }, indent=4)
        except KeyError:
            raise web.notfound()


if __name__ == "__main__":
    app.run()
