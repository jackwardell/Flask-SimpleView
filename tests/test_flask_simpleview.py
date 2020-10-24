import flask
import pytest
import flask_simpleview

RULE = '/simple-view'
ENDPOINT = 'simple_view'
GET_RETURNS = "<html><head></head><body>hello</body></html>"
POST_RETURNS = {"goodbye": "world"}


class SimpleView(flask_simpleview.SimpleView):
    rule = RULE
    endpoint = ENDPOINT

    def get(self):
        return GET_RETURNS

    def post(self):
        return POST_RETURNS


def test_flask():
    app = flask_simpleview.Flask("test")
    app.add_view(SimpleView)

    with app.test_client() as client:
        assert client.get(RULE).data.decode() == GET_RETURNS
        assert client.post(RULE).json == POST_RETURNS


def test_blueprint():
    blueprint = flask_simpleview.Blueprint("test", __name__)
    blueprint.add_view(SimpleView)

    app = flask.Flask("test")
    app.register_blueprint(blueprint)

    with app.test_client() as client:
        assert client.get(RULE).data.decode() == GET_RETURNS
        assert client.post(RULE).json == POST_RETURNS


if __name__ == "__main__":
    pytest.main()
