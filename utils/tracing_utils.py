"""Shared OpenAI client and LangSmith tracing utilities.""" # Module docstring

from functools import lru_cache # Cache decorator

from langsmith import traceable # Tracing decorator
from langsmith.wrappers import wrap_openai # OpenAI wrapper
from openai import OpenAI # OpenAI SDK

from utils.config import required_env # Env var helper


@lru_cache(maxsize=1) # Cache instance
def get_openai_client() -> OpenAI: # Client factory
    """
    Create one reusable OpenAI client.

    wrap_openai adds LangSmith instrumentation to supported
    OpenAI calls made through this client.
    """
    api_key = required_env("OPENAI_API_KEY") # Fetch API key

    # Construct the standard OpenAI SDK client.
    base_client = OpenAI(api_key=api_key) # Init OpenAI client

    # Instrument the client for LangSmith tracing.
    return wrap_openai(base_client) # Return wrapped client


def traced_function(name: str): # Decorator factory
    """
    Create a named LangSmith trace decorator.

    Keeping this helper makes the trace names consistent
    throughout the application.
    """
    return traceable( # Return decorator
        name=name, # Set trace name
        run_type="chain", # Set run type
    ) # End decorator