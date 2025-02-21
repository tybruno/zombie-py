"""Examples of using the Reraise class to transform exceptions.

This module contains examples of how to use the Reraise class to transform
exceptions.

Example 1: Using as a Context Manager
Example 2: Using as a Decorator
Example 3: Using Dynamic Error Message with string.Template
Example 4: Using raise_from_error=True
"""

from zombie import ExceptionTransformation, Reraise
import string


# Example 1: Using as a Context Manager
def context_manager_example():
    """Example of using Reraise as a context manager."""
    transform = ExceptionTransformation(
        original_exception=KeyError,
        new_exception=ValueError,
    )

    try:
        with Reraise(transform):
            raise KeyError('Original error message')
    except ValueError as e:
        print(f'Caught ValueError: {e}')


# Example 2: Using as a Decorator
def decorator_example():
    """Example of using Reraise as a decorator."""
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

    @Reraise(*transforms)
    def func():
        raise KeyError('Original error message')

    try:
        func()
    except ValueError as e:
        print(f'Caught ValueError: {e}')


# Example 3: Using Dynamic Error Message with string.Template
def dynamic_error_message_example():
    """Example of using a dynamic error message with string.Template."""
    transform = ExceptionTransformation(
        original_exception=KeyError,
        new_exception=ValueError,
        error_message=string.Template('Error: ${original_error_message}'),
        raise_from_error=True,
    )

    @Reraise(transform)
    def example_function():
        raise KeyError('Original error message')

    try:
        example_function()
    except ValueError as e:
        print(f'Caught ValueError: {e}')


# Example 4: Using raise_from_error=True
def raise_from_error_example():
    """Example of using raise_from_error=True."""
    transform = ExceptionTransformation(
        original_exception=KeyError,
        new_exception=ValueError,
        error_message='An error occurred',
        raise_from_error=True,
    )

    @Reraise(transform)
    def example_function():
        raise KeyError('Original error message')

    try:
        example_function()
    except ValueError as e:
        print(f'Caught ValueError: {e}')


# Run examples
if __name__ == '__main__':
    print('Context Manager Example:')
    context_manager_example()
    print('\nDecorator Example:')
    decorator_example()
    print('\nDynamic Error Message Example:')
    dynamic_error_message_example()
    print('\nRaise From Error Example:')
    raise_from_error_example()
