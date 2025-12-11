from src.lindorm_mcp_server import server
from importlib.metadata import PackageNotFoundError, version
def main():
    """Main entry point for the package."""
    server.main()

# Optionally expose other important items at package level
__all__ = ['main', 'server']
try:
    __version = version("lindorm-mcp-server")
except PackageNotFoundError:
    # package is not installed
    pass
