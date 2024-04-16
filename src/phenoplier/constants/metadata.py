from importlib.metadata import distribution

dist = distribution("phenoplier")
APP_NAME = dist.metadata["name"]
APP_VERSION = dist.version
