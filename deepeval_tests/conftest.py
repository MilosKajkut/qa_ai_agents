import sys
import os
from dotenv import load_dotenv

# Make sure project root is importable from tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()
