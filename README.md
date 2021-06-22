# python-wlog

internal logging package

:warning: This package is public but not open.

## install

```console
$ pip install git+https://github.com/wacul/python-wlog@0.1.0
```

## features

- structued logging (JSON logging)
- even unhandled exception

## how to use

In main.py, put `import wlog.force` at the beginning of the file.

```py
import wlog.force

import other_library
```

in other codeset, use this library like [structlog's BoundLogger](standard logging libraray.).

```py
from wlog import get_logger
logger = get_logger(__name__)

logger.bind(xxx="yyy").info("this is info message")

try:
    raise Exception("hmm")
except Exception as e:
    logger.bind(exception=e).error(repr(e))
```
