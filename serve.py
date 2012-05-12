import web
import json
import random
import uuid
import hashlib

urls = (
    '/', 'generate',
    '/(\w+)', 'get',
    '/(\w+)/ratings', 'ratings',
)

app = web.application(urls, globals())

lookup = {}

class Recipe(object):

    def __init__(self, id, ingredients):
        self.id = id
        self.ingredients = ingredients
        self.ratings = {}

    def to_dict(self):
        return {
            'id': self.id,
            'ingredients': self.ingredients
        }

def generate_recipe():
    all_ingr = [x.strip() for x in file('ingredients.juice')]
    ret = {}
    for k in range(10):
        fruit = random.choice(all_ingr)
        if fruit in ret:
            ret[fruit] += 100
        else:
            ret[fruit] = 100
    ingr = sorted(ret.items())
    id = hashlib.md5(repr(ingr)).hexdigest()
    return Recipe(id, dict(ingr))

class generate:
    def GET(self):
        recipe = generate_recipe()
        lookup[recipe.id] = recipe
        return json.dumps(recipe.to_dict(), indent=4)

class get:
    def GET(self, id):
        try:
            recipe = lookup[id]
            return json.dumps(recipe.to_dict(), indent=4)
        except KeyError:
            raise web.notfound()

class ratings:

    def get_recipe(self, recipe_id):
        try:
            return lookup[recipe_id]
        except KeyError:
            raise web.notfound()

    def GET(self, recipe_id):
        recipe = self.get_recipe(recipe_id)
        return json.dumps({
            'id': recipe.id,
            'ratings': recipe.ratings
        })

    def POST(self, recipe_id):
        recipe = self.get_recipe(recipe_id)
        data = json.loads(web.data())
        user = data.get('user')
        if not user:
            raise web.badrequest()
        rating = data['rating']
        recipe.ratings[user] = int(rating)


if __name__ == "__main__":
    app.run()
