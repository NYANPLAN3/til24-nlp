"""Main app."""

from dotenv import load_dotenv

load_dotenv()

import logging
import os
import sys

from fastapi import FastAPI

from .NLPManager import NLPManager
from .structs import ExtractRequest
from .values import PLACEHOLDER

__all__ = ["create_app"]

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
    async def extract(req: ExtractRequest):
        """Performs QA extraction given a context string.

        returns a dictionary with fields:

        {
            "heading": str,
            "target": str,
            "tool": str,
        }
        """
        preds = []
        for instance in req.instances:
            in_text = instance.transcript
            # out_data = PLACEHOLDER
            out_data = await nlp.extract(in_text)
            preds.append(out_data)

        return {"predictions": preds}

    return app
