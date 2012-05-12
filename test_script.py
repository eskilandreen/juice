from paste.fixture import TestApp, AppError
import serve
import json
import random

def main():
    i_user = 0 
    while(True):
        name = 'applelover' + str(i_user)
        recepie = _select_juice(name)
        print "Got recepie: " + str(recepie)
        should_rate = random.choice([1,0])
        if [x for x in recepie['ingredients'].keys() if x.startswith('Apple')]:
            _rate(recepie['id'], name,  1)
        else:
            _rate(recepie['id'], name, -1)
        i_user = (i_user+1)%20

def _select_juice(juicer):
    res = _get('/', params={'juicer': juicer})
    return json.loads(res.body)

def _rate(recipe_id, juicer, rating, status='*'):
    data = json.dumps({'juicer': juicer, 'rating': rating})
    _post('/%s/ratings' % recipe_id, data, status=status)

def _get_ratings(recipe_id):
    ret = _get('/%s/ratings' % recipe_id)
    return json.loads(ret.body)

def _get_recipe(recipe_id):
    res = _get('/%s' % recipe_id)
    return json.loads(res.body)

def _get(path, **kwargs):
    middleware = []
    testApp = TestApp(serve.app.wsgifunc(*middleware))
    r = testApp.get(path, headers={'Content-Type': 'text/plain'}, **kwargs)
    return r

def _post(path, data, status='*'):
    middleware = []
    testApp = TestApp(serve.app.wsgifunc(*middleware))
    r = testApp.post(path, data, status=status)
    return r


if __name__ == '__main__':
    main()
