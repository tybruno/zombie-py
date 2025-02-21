"""Utilities for transforming and re-raising exceptions in Python.
This module provides utilities for transforming and re-raising exceptions
in Python. It includes classes and functions to define exception
transformations, apply these transformations to functions using decorators,
and handle exceptions within context managers.

Classes:
    ExceptionTransformation: Defines the transformation of one exception
        type to another.
    Reraise: Context manager and decorator class to handle exception

Functions:
    _raise_transformed_exception: Transforms and raises an exception based
        on provided exception transformations.
    _reraise_decorator: Decorator to apply exception transformations to a
        function.
"""

import logging
import string
import typing
import functools

_LOG = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class ExceptionTransformation:
    """Defines the transformation of one exception type to another.

    This class defines the transformation of one exception type to another.

    Args:
        original_exception (typing.Type[BaseException]): The original
            exception type to transform.
        new_exception (typing.Type[BaseException]): The new exception type
            to raise.
        error_message (typing.Optional[typing.Union[str, string.Template]]):
            The error message to use in the new exception. If a string
            template is provided, it will be substituted with the original
            error message. If the default `None` provided, the original error
            message will be used.
        raise_from_error (bool): Whether to chain the new exception from the
            original exception. If `True`, the new exception will be chained
            from the original exception. If `False`, the new exception will
            not be chained from the original exception. The default is `False`.
    """

    def __init__(
        self,
        original_exception: typing.Type[BaseException],
        new_exception: typing.Type[BaseException],
        error_message: str | string.Template | None = None,
        raise_from_error: bool = False,
    ):
        self.original_exception = original_exception
        self.new_exception = new_exception
        self.error_message = error_message
        self.from_error = raise_from_error

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'original_exception={self.original_exception.__name__}, '
            f'new_exception={self.new_exception.__name__}, '
            f'error_message={self.error_message!r}, '
            f'raise_from_error={self.from_error})'
        )


def _transform_and_raise(
    *, transform: ExceptionTransformation, error: BaseException
) -> None:
    """Transforms an exception and raises the new exception.

    This function transforms an exception using an `ExceptionTransformation`
    object and raises the new exception. The transformation includes
    substituting the error message with the provided template and optionally
    chaining the new exception from the original exception.

    Args:
        transform (ExceptionTransformation): The transformation to apply to
            the exception.
        error (BaseException): The original exception to transform.

    Raises:
        BaseException: The new exception with the transformed error message.
    """
    _LOG.debug(f'Transforming exception {error} using {transform}')
    error_message = transform.error_message

    # If the error message is a string.Template, substitute the original error message
    if isinstance(transform.error_message, string.Template):
        error_message = transform.error_message.safe_substitute(
            original_error_message=str(error)
        )
        _LOG.debug(f'Substituted error message: {error_message}')

    # Raise the new exception, optionally chaining it from the original exception
    if transform.from_error:
        _LOG.info(
            f'Raising {transform.new_exception} from {error} with message: {error_message}'
        )
        raise transform.new_exception(error_message) from error

    _LOG.info(
        f'Raising {transform.new_exception} with message: {error_message}'
    )
    raise transform.new_exception(error_message) from None


def _raise_transformed_exception(
    *exception_transformations: ExceptionTransformation,
    error: BaseException,
) -> None:
    """Transforms and raises an exception based on provided exception
    transformations.

    This function iterates over a collection of `ExceptionTransformation`
    objects and checks if the given error matches any of the original
    exceptions specified in the transformations. If a match is found, it
    transforms the error message (if necessary) and raises the new
    exception specified in the transformation.

    Args:
        *exception_transformations (ExceptionTransformation): Variable number
            of `ExceptionTransformation` objects that define how to transform
            and raise exceptions.
        error (BaseException): The original exception that needs to be
            transformed and raised.

    Raises:
        Exception: The new exception specified in the `ExceptionTransformation`
            object, with the transformed error message.
    """
    for transform in exception_transformations:
        if isinstance(error, transform.original_exception):
            _transform_and_raise(transform=transform, error=error)

    raise error  # Raise the original exception if no transformation is found


def _reraise_decorator(
    *exception_transformations: ExceptionTransformation,
) -> typing.Callable:
    """Decorator to apply exception transformations to a function.

    This decorator applies a collection of `ExceptionTransformation` objects
    to a function. When the function raises an exception, the decorator
    checks if the exception matches any of the original exceptions specified
    in the transformations. If a match is found, it transforms the error
    message (if necessary) and raises the new exception specified in the
    transformation.

    Args:
        *exception_transformations (ExceptionTransformation): Variable number
            of `ExceptionTransformation` objects that define how to transform
            and raise exceptions.

    Returns:
        typing.Callable: The decorated function with exception transformations applied.
    """

    def decorator(callable_: typing.Callable) -> typing.Callable:
        """Decorator function to apply exception transformations.

        This decorator function applies the exception transformations to the
        decorated function. If the function raises an exception, the decorator
        catches the exception, transforms it based on the provided
        transformations, and re-raises the new exception.

        Args:
            callable_ (typing.Callable): The function to decorate.

        Returns:
            typing.Callable: The decorated function with exception
                transformations applied.

        Raises:
            Exception: The new exception specified in the
                `ExceptionTransformation` object, with the transformed
                error

        """

        @functools.wraps(callable_)
        def wrapper(*args, **kwargs) -> typing.Any:
            """Wrapper function to apply exception transformations.

            This wrapper function applies the exception transformations to the
            decorated function. If the function raises an exception, the
            wrapper catches the exception, transforms it based on the
            provided transformations, and re-raises the new exception.

            Args:
                *args: Positional arguments to pass to the decorated function.
                **kwargs: Keyword arguments to pass to the decorated function.

            Returns:
                Any: The result of the decorated function.

            Raises:
                Exception: The new exception specified in the
                    `ExceptionTransformation` object, with the transformed
                    error message.
            """

            result = None
            try:
                result = callable_(*args, **kwargs)
            # pylint: disable=broad-except
            except BaseException as error:
                _raise_transformed_exception(
                    *exception_transformations, error=error
                )
            return result

        return wrapper

    return decorator


class Reraise:
    """Context manager and decorator class to handle exception
    transformations.

    Args:
        exception_transformations (typing.Union[ExceptionTransformation,
            typing.Sequence[ExceptionTransformation]]):
            A single `ExceptionTransformation` object or a sequence of
            `ExceptionTransformation` objects that define
            how to transform and raise exceptions.
    """

    def __init__(
        self,
        exception_transformations: ExceptionTransformation
        | typing.Sequence[ExceptionTransformation],
    ):
        # Store the exception transformations as a tuple
        self.exception_transformations: tuple[ExceptionTransformation, ...]

        # Check if a single ExceptionTransformation object is provided
        if isinstance(exception_transformations, ExceptionTransformation):
            # Convert the single object to a tuple
            self.exception_transformations = (exception_transformations,)
        else:
            # Convert the sequence of ExceptionTransformation objects to a tuple
            self.exception_transformations = tuple(exception_transformations)

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type: typing.Type[BaseException] | None,
        exc_value: BaseException,
        traceback: typing.Any | None,
    ):
        if exc_value is None:
            # No exception to handle, return False to indicate normal exit
            return False
        error = exc_value
        # Transform and raise the exception based on the provided transformations
        _raise_transformed_exception(
            *self.exception_transformations, error=error
        )
        # Return False to indicate that the exception was not handled here
        return False

    def decorate(self, callable_: typing.Callable) -> typing.Callable:
        """Decorates a callable with exception transformations.

        This method decorates a function with exception transformations using
        the `_reraise_decorator` function. The decorated function will apply
        the exception transformations to the function when it raises an
        exception.

        Args:
            callable_ (typing.Callable): The callable to decorate.

        Returns:
            typing.Callable: The decorated function with exception
              transformations applied.
        """
        wrapped_callable = _reraise_decorator(*self.exception_transformations)(
            callable_
        )
        return wrapped_callable

    def __call__(self, func: typing.Callable) -> typing.Callable:
        wrapped_callable = self.decorate(func)
        return wrapped_callable
