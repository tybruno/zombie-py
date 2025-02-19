![zombie-py-logo.png](images/zombie-py.png)

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![Code Style: Blue](https://img.shields.io/badge/code%20style-blue-0000ff.svg)](https://github.com/psf/blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-blueviolet.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/tybruno/zombie-py/branch/main/graph/badge.svg?token=ZO94EJFI3G)](https://codecov.io/gh/tybruno/zombie-py)
[![Pylint](https://img.shields.io/badge/Pylint-10.0%2F10-green)](10.0/10)
[![Mypy](https://img.shields.io/badge/Mypy-checked-blue)](10.0/10)

# zombie-py

Bringing Raised Exceptions Back From the Dead As New Exceptions.

## Key Features:

* **Easy**: Simplifies the process of transforming and re-raising exceptions.
* **Context Manager and Decorator**: Provides both context manager and decorator for handling exceptions.
* **Customizable**: Allows defining custom transformations for exceptions.
* **Fully Tested**: Ensures reliability through comprehensive tests.

## Installation

`pip install zombie-py`

## Usage

### Example 1: Using as a Context Manager

```python
from zombie import ExceptionTransformation, Reraise

transform = ExceptionTransformation(
        original_exception=KeyError,
        new_exception=ValueError,
    ),

# Using as a context manager with multiple transforms
with Reraise(transform):
    raise KeyError('Original error message')
```
#### Example Output

```shell
Traceback (most recent call last):
    File "example.py", line 20, in <module>
        raise KeyError('Original error message')
    File "example.py", line 15, in <module>
        raise ValueError('Original error message') from e
ValueError: 'Original error message'
```

### Example 2: Using as a Decorator

```python
from zombie import ExceptionTransformation, Reraise

transforms = [
    ExceptionTransformation(
        original_exception=KeyError,
        new_exception=ValueError,
        error_message='A KeyError occurred',
        raise_from_error=True,
    ),
    ExceptionTransformation(
        original_exception=TypeError,
        new_exception=RuntimeError,
        error_message='A TypeError occurred',
        raise_from_error=True,
    ),
]

# Using as a decorator with multiple transforms
@Reraise(*transforms)
def func():
    raise KeyError('Original error message')

func()
```
#### Example Output
```shell
Traceback (most recent call last):
    File "example.py", line 20, in <module>
        func()
    File "example.py", line 15, in func
        raise KeyError('Original error message')
KeyError: 'Original error message'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
    File "example.py", line 20, in <module>
        func()
    File "example.py", line 15, in func
        raise ValueError('A KeyError occurred') from e
ValueError: A KeyError occurred
```

#### Example 3: Catching and Transforming a Parent Exception
```python
from zombie import ExceptionTransformation, Reraise

@Reraise(
    ExceptionTransformation(
        original_exception=Exception,
        new_exception=ValueError,
    ),
)
def func():
    raise KeyError('Original error message')

func()
```

### Example Output
```shell
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<path_to_project>/zombie/zombie.py", line 212, in wrapper
    _raise_transformed_exception(
  File "<path_to_project>/zombie/zombie.py", line 137, in _raise_transformed_exception
    _transform_and_raise(transform=transform, error=error)
  File "<path_to_project>/zombie/zombie.py", line 103, in _transform_and_raise
    raise transform.new_exception(error_message) from error
ValueError: None
```
## Advanced Usage Examples for `ExceptionTransformation`

### Using `error_message`

The `error_message` parameter allows you to customize the error message of 
the new exception. You can use a static string or a `string.Template` to
 include dynamic content from the original exception. Using the default `None` will use the original exception's 
message.

#### Default Error Message

If the `error_message` parameter is not provided, the new exception will use the original exception's message.

```python
from zombie import ExceptionTransformation, Reraise

# Define an exception transformation without an error message
transform = ExceptionTransformation(
    original_exception=KeyError,
    new_exception=ValueError,
    raise_from_error=True
)

@Reraise(transform)
def example_function():
    raise KeyError("Original error message")

try:
    example_function()
except Exception as e:
    print(e)  # Output: Original error message
```
#### Static Error Message

```python
from zombie.zombie import ExceptionTransformation, Reraise

# Define an exception transformation with a static error message
transform = ExceptionTransformation(
    original_exception=KeyError,
    new_exception=ValueError,
    error_message="A static error message",
    raise_from_error=True
)

@Reraise(transform)
def example_function():
    raise KeyError("Original error message")

try:
    example_function()
except Exception as e:
    print(e)  # Output: A static error message

```
#### Dynamic Error Message with string.Template
```python
from zombie import ExceptionTransformation, Reraise
import string

# Define an exception transformation with a dynamic error message
transform = ExceptionTransformation(
    original_exception=KeyError,
    new_exception=ValueError,
    error_message=string.Template("Error: ${original_error_message}"),
    raise_from_error=True
)

@Reraise(transform)
def example_function():
    raise KeyError("Original error message")

try:
    example_function()
except Exception as e:
    print(e)  # Output: Error: Original error message
```
### Using `raise_from_error`
The `raise_from_error` parameter determines whether the new exception should be 
chained from the original exception. If raise_from_error is `True`,
 the new exception will include the original exception as its cause.
`False` will raise the new exception without the original exception as its cause.
`False` is the default value.

#### With `raise_from_error=True`
```python
from zombie.zombie import ExceptionTransformation, Reraise

# Define an exception transformation with raise_from_error=True
transform = ExceptionTransformation(
    original_exception=KeyError,
    new_exception=ValueError,
    error_message="An error occurred",
    raise_from_error=True
)

@Reraise(transform)
def example_function():
    raise KeyError("Original error message")

example_function()

```
##### Example Output

```shell
$ python example.py
Traceback (most recent call last):
    File "example.py", line 20, in <module>
        raise KeyError('Original error message')
KeyError: 'Original error message'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
    File "example.py", line 20, in <module>
        raise KeyError('Original error message')
    File "example.py", line 15, in <module>
        raise ValueError('A KeyError occurred') from e
ValueError: A KeyError occurred
```
#### With `raise_from_error=False` (default)
```python
from zombie import ExceptionTransformation, Reraise

# Define an exception transformation with raise_from_error=False
transform = ExceptionTransformation(
    original_exception=KeyError,
    new_exception=ValueError,
    error_message="An error occurred",
    raise_from_error=False
)

@Reraise(transform)
def example_function():
    raise KeyError("Original error message")

example_function()
```
##### Example Output

```shell
Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "<path_to_project>/zombie/zombie.py", line 146, in wrapper
        _raise_transformed_exception(*exception_transformations, error=error)
    File "<path_to_project>/zombie/zombie.py", line 116, in _raise_transformed_exception
        _transform_and_raise(transform=transform, error=error)
    File "<path_to_project>/zombie/zombie.py", line 85, in _transform_and_raise
        raise transform.new_exception(error_message) from None
ValueError: An error occurred
```