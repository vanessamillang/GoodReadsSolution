from functools import cached_property
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlparse
import redis

# Configuración
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000

class WebRequestHandler(BaseHTTPRequestHandler):
    @cached_property
    def url(self):
        return urlparse(self.path)

    @cached_property
    def query_data(self):
        return dict(parse_qsl(self.url.query))

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        books = None
        search_query = self.query_data.get('q', '')  # Obtener la palabra buscada (si se proporcionó)
        if search_query:
            books = self.search_books(search_query.split(' '))
        self.wfile.write(self.get_response(search_query, books).encode("utf-8"))

    def search_books(self, keywords):
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        return r.sinter(keywords)

    def get_response(self, search_query, books):
        response_html = """
        <h1> Hola Web </h1>
        <form action="/" method="get">
              <label for="q"> Búsqueda </label>
              <input type="text" name="q" required value="{}"/> <!-- Mostrar la palabra buscada -->
              <input type="submit" value="Buscar"/>
        </form>

        <p> Resultado de la búsqueda para "{}": {} </p>
        """.format(search_query, search_query, books if books else "No se encontraron resultados")

        return response_html

if __name__ == "__main__":
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        r.ping()  # Comprobar la conexión a Redis
    except redis.ConnectionError:
        print("Error: No se puede conectar a Redis. Asegúrate de que esté en ejecución en {}:{}".format(REDIS_HOST, REDIS_PORT))
    else:
        print(f"Server starting on {SERVER_HOST}:{SERVER_PORT}...")
        server = HTTPServer((SERVER_HOST, SERVER_PORT), WebRequestHandler)
        server.serve_forever()
