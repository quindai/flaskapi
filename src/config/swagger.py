template = {
  "swagger": "2.0",
  "info": {
    "title": "My API",
    "description": "API for my data",
    "contact": {
      "responsibleOrganization": "ORION",
      "responsibleDeveloper": "Randy Quindai",
      "email": "randy.quindai@laccan.ufal.br",
      "url": "www.orion.edu.br",
    },
    "termsOfService": "http://me.com/terms",
    "version": "0.0.1"
  },
  "host": "mysite.com",  # overrides localhost:500
  "basePath": "/api",  # base bash for blueprint registration
  "schemes": [
    "http",
    "https"
  ],
  "securityDefinitions"={
    "Bearer": {
      "type": "apiKey",
      "name": "Authorization",
        "in": "header",
        "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization",

  },
  "operationId": "getmyData"
}}

swagger = Swagger(app, template=template)
