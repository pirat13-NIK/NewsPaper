from django.utils.deprecation import MiddlewareMixin


class DeviceTemplateMiddleware(MiddlewareMixin):
    """Middleware для выбора версии шаблона в зависимости от устройства."""

    def process_template_response(self, request, response):
        if hasattr(response, 'template_name') and response.template_name:
            user_agent = request.META.get('HTTP_USER_AGENT', '').lower()

            is_mobile = any(device in user_agent for device in [
                'mobile', 'android', 'iphone', 'ipad', 'blackberry'
            ])

            if is_mobile:
                response.template_name = f'mobile/{response.template_name}'
            else:
                response.template_name = f'full/{response.template_name}'

        return response