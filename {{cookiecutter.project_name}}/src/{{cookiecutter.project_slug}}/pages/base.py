from importlib import import_module

from wagtail.core.models import Page

from ..mixins import EnhancedEditHandlerMixin, SeoMixin


class BasePage(EnhancedEditHandlerMixin, SeoMixin, Page):
    # Basepage is not anything creatable in admin
    is_creatable = False
    show_in_menus_default = True

    extra_panels = []

    def __init__(self, *args, **kwargs):
        self.template = "pages/react.html"
        self.component_name = self.__class__.__name__
        super().__init__(*args, **kwargs)

    def serve(self, request, *args, **kwargs):
        if self.should_serve_json(request):
            from django.http import JsonResponse

            json = self.to_dict({"request": request})
            return JsonResponse(json)

        return super().serve(request, *args, **kwargs)

    @staticmethod
    def should_serve_json(request):
        return (
            request.GET.get("format", None) == "json"
            or request.content_type == "application/json"
        )

    def to_dict(self, context={}):
        serializer_cls = self.get_serializer_class()
        serializer = serializer_cls(self, context={"request": context["request"]})

        return {
            "component_name": self.component_name,
            "component_props": serializer.data,
        }

    def get_serializer_class(self):
        """
        Locates and loads page serializer based on page name.
        Override this method if you would like to supply your own serializer.
        """
        class_name = self.__class__.__name__
        base_name = class_name.lower().replace("page", "")

        base_class_module = self.__module__.split(".")[0]
        module_path = ".{}_serializer".format(base_name)
        serializer_name = "{}Serializer".format(class_name)

        module = import_module(
            module_path, package="{}.pages".format(base_class_module)
        )

        serializer = getattr(module, serializer_name)

        return serializer
