import web
import json
import random
import uuid
import hashlib

urls = (
    '/', 'select',
    '/(\w+)', 'get',
    '/(\w+)/ratings', 'ratings',
)

app = web.application(urls, globals())

MAX_ACTIVE_JUICES = 10

active = {}
discarded = {}

class Recipe(object):

    def __init__(self, id, ingredients):
        self.id = id
        self.ingredients = ingredients
        self.ratings = {}
        self.seen_by = set()

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
    recipe = Recipe(id, dict(ingr))
    active[id] = recipe
    return recipe

def select_unseen_recipe(juicer):
    return random.choice([x for x in active.values() if not juicer in x.seen_by])

class Base(object):
    def __init__(self):
        web.header('Content-type', 'application/json')

class select(Base):
    def GET(self):
        juicer = web.input()['juicer']
        if not active:
            recipe = generate_recipe()
        elif all(juicer in x.seen_by for x in active.values()):
            recipe = generate_recipe()
        elif len(active) < MAX_ACTIVE_JUICES and random.random() < 0.5:
            recipe = generate_recipe()
        else:
            recipe = select_unseen_recipe(juicer)

        recipe.seen_by.add(juicer)
        return json.dumps(recipe.to_dict(), indent=4)

class get(Base):
    def GET(self, id):
        try:
            recipe = active[id]
            return json.dumps(recipe.to_dict(), indent=4)
        except KeyError:
            raise web.notfound()

class ratings(Base):

    def get_recipe(self, recipe_id):
        try:
            return active[recipe_id]
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
        juicer = data.get('juicer')
        if not juicer:
            raise web.badrequest()
        rating = data['rating']
        recipe.ratings[juicer] = int(rating)
        return json.dumps({})


if __name__ == "__main__":
    app.run()
