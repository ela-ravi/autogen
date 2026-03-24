import os
import sys

# Add the project root (where modules/ lives) to sys.path
# In Docker, modules/ is mounted at /app/modules/
# This ensures `import modules.transcription` etc. works
_modules_parent = "/app"
if _modules_parent not in sys.path:
    sys.path.insert(0, _modules_parent)

# Also support local development (where modules/ is a sibling of backend/)
_local_parent = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
if _local_parent not in sys.path:
    sys.path.insert(0, _local_parent)
