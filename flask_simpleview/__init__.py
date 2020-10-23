import flask
import flask.views


class NoTemplate(Exception):
    pass


class SkeletonMixin:
    def add_url_rule(self, *args, **kwargs):
        raise NotImplementedError()

    def add_view(self, view):
        self.add_url_rule(view.rule, view_func=view.as_view(view.endpoint))

    def add_api(self, api):
        self.add_view(api)

    # def route(self, rule, **options):
    #     def decorator(func_or_cls):
    #         endpoint = (
    #                 options.pop("endpoint")
    #                 or getattr(func_or_cls, "endpoint", None)
    #                 or func_or_cls.__name__
    #         )
    #         if issubclass(func_or_cls, SimpleView):
    #             self.add_url_rule(rule, view_func=func_or_cls.as_view(endpoint))
    #         else:
    #             self.add_url_rule(rule, endpoint, func_or_cls, **options)
    #         return func_or_cls
    #
    #     return decorator


class Flask(flask.Flask, SkeletonMixin):
    pass


class Blueprint(flask.Blueprint, SkeletonMixin):
    pass


class SimpleView(flask.views.MethodView):
    @property
    def rule(self):
        raise NotImplementedError()

    @property
    def endpoint(self):
        raise NotImplementedError()

    def render_template(self, *optional_template_name_or_list, **context):
        if not hasattr(self, "template") or not optional_template_name_or_list:
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

Flask.route()
