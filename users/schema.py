from drf_spectacular.extensions import OpenApiAuthenticationExtension


class CustomJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "users.authentication.CustomJWTAuthentication"
    name = "customJwtAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "Authorize",
            "description": "JWT access token. Example: Bearer <access_token>",
        }
