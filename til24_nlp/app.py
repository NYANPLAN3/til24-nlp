"""Main app."""

from dotenv import load_dotenv

load_dotenv()

import asyncio
import logging
import os
import sys

from fastapi import FastAPI, Request

from .log import setup_logging
from .NLPManager import NLPManager
from .values import PLACEHOLDER

__all__ = ["create_app"]


setup_logging()
log = logging.getLogger(__name__)


def create_app():
    """App factory."""
    app = FastAPI()

    nlp = NLPManager()

    @app.get("/hello")
    async def hello():
        """J-H: I added this to dump useful info for debugging.

        Returns:
            dict: JSON message.
        """
        debug = {}
        debug["py_version"] = sys.version
        debug["task"] = "NLP"
        debug["env"] = dict(os.environ)

        try:
            import torch  # type: ignore

            debug["torch_version"] = torch.__version__
            debug["cuda_device"] = str(torch.zeros([10, 10], device="cuda").device)
        except ImportError:
            pass

        return debug

    @app.get("/health")
    async def health():
        """Competition admin needs this."""
        return {"message": "health ok"}

    @app.post("/extract")
    async def extract(req: Request):
        """Performs QA extraction given a context string.

        returns a dictionary with fields:

        {
            "heading": str,
            "target": str,
            "tool": str,
        }
        """
        # NOTE: This is just in case the server is giving non-compliant requests for some reason.
        data = await req.json()

        preds = []
        for instance in data["instances"]:
            # out_data = PLACEHOLDER
            out_data = nlp.extract(instance["transcript"])
            preds.append(out_data)
            await asyncio.sleep(0)  # Allow other requests to run.

        return {"predictions": preds}

    return app
