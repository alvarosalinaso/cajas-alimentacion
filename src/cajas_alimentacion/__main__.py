"""Permite ejecutar ``python -m cajas_alimentacion``."""

import sys

from cajas_alimentacion.pipeline import main

if __name__ == "__main__":
    sys.exit(main())
