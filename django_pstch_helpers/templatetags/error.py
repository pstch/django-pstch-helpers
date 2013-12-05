from django import template
from django.conf import settings
register = template.Library()

@register.tag
def raise(parser, token): 
    return RaiseExNode()

class RaiseExNode(template.Node): 
    def render(self, context): 
        raise
