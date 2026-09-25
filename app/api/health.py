from flask_restx import Namespace, Resource


health_ns = Namespace(
    "health",
    description="Health check operations",
)


@health_ns.route("")
class Health(Resource):

    def get(self):
        """
        Check whether the API is running.
        """

        return {
            "success": True,
            "message": "API is healthy",
        }, 200