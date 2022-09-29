from django import template

register = template.Library()

@register.filter()
def to_percent(value):
	new = value * 100
	return str(new) + "%"