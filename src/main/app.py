from flask import Flask, jsonify

from flask_graphql import GraphQLView
from src.schema import schema_with_mysql, schema_with_neo4j, schemas
from src.model import neo4j_model


def create_mysql_app(path="/graphql", **kwargs):
    app = Flask(__name__)
    app.debug = True
    app.add_url_rule(
        path, view_func=GraphQLView.as_view(
            "graphql",
            schema=schema_with_mysql.schema,
            get_context=lambda: {'session': schema_with_mysql.Session()},
            **kwargs
        )
    )
    return app


def create_neo4j_app(path="/graphql", **kwargs):
    app = Flask(__name__)
    app.debug = True
    app.add_url_rule(
        path, view_func=GraphQLView.as_view(
            "graphql",
            schema=schema_with_neo4j.schema,
            **kwargs
        )
    )

    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify(
            {'message': 'The requested URL was not found on the server.'}), 404
    return app


if __name__ == "__main__":
    app = create_neo4j_app(graphiql=True)
    app.run(host="0.0.0.0", port='8000')
