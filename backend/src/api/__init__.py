from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from src.api.routes import router
from src.config import settings
from src.utils import logger


def create_app() -> FastAPI:
  """
  Create and configure FastAPI application.

  Returns:
      FastAPI application
  """
  app = FastAPI(
    title='Solana AI Trader',
    description='Automated Solana trading system powered by LLM analysis',
    version='0.1.0'
  )

  # Include API routes
  app.include_router(router)

  # Serve static files (frontend)
  frontend_dir = Path(__file__).parent.parent.parent / 'frontend'
  if frontend_dir.exists():
    app.mount('/static', StaticFiles(directory=str(frontend_dir)), name='static')

    @app.get('/')
    async def read_root():
      index_file = frontend_dir / 'index.html'
      if index_file.exists():
        return FileResponse(str(index_file))
      return {'message': 'Solana AI Trader API'}

  @app.on_event('startup')
  async def startup_event():
    """Run on application startup."""
    logger.info('Starting Solana AI Trader API...')

  @app.on_event('shutdown')
  async def shutdown_event():
    """Run on application shutdown."""
    logger.info('Shutting down Solana AI Trader API...')

  return app


# Create app instance
app = create_app()
