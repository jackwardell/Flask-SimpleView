import re

import flask
import flask.views


def camel_case_to_snake_case(word):
    """very simple mechanism for turning CamelCase words into snake_case"""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", word).lower()


def camel_case_to_slug_case(word):
    """very simple mechanism for turning CamelCase words into slug-case"""
    return re.sub(r"(?<!^)(?=[A-Z])", "-", word).lower()


class NoTemplate(Exception):
    """exception for when no template is passed"""
    pass


class SkeletonMixin:
    """Mixin for the flask Skeleton (shared methods between Flask and Blueprint)"""

    def add_url_rule(self, *args, **kwargs):
        raise NotImplementedError()

    def add_view(self, view):
        rule = view.make_rule()
        endpoint = view.make_endpoint()
        return self.add_url_rule(rule, view_func=view.as_view(endpoint))

    def add_api(self, api):
        return self.add_view(api)


class Flask(flask.Flask, SkeletonMixin):
    pass


class Blueprint(flask.Blueprint, SkeletonMixin):
    pass


class ViewConstructor:
    @classmethod
    def make_endpoint(cls):
        return getattr(cls, "endpoint", camel_case_to_snake_case(cls.__name__))

    @classmethod
    def make_rule(cls):
        return getattr(cls, "rule", "/" + camel_case_to_slug_case(cls.__name__))


class SimpleView(flask.views.MethodView, ViewConstructor):
    def render_template(self, *optional_template_name_or_list, **context):
        if not hasattr(self, "template") and not optional_template_name_or_list:
            raise NoTemplate("No template passed or found on the view")

        template_name_or_list = (
            optional_template_name_or_list[0]
            if optional_template_name_or_list
            else self.template
        )
        return flask.render_template(template_name_or_list, **context)

    def __getattr__(self, attr):
        return getattr(flask, attr)

    def __repr__(self):
        rv = '<{}(rule="{}", endpoint="{}", methods={})>'.format(
            self.__class__.__name__, self.rule, self.endpoint, self.methods
        )
        return rv


API = View = SimpleView
