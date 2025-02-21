import pytest
import string
from zombie.zombie import (
    ExceptionTransformation,
    _transform_and_raise,
    _raise_transformed_exception,
    _reraise_decorator,
    Reraise,
)


class TestExceptionTransformation:
    def test_initialization(self):
        transform = ExceptionTransformation(
            original_exception=KeyError,
            new_exception=ValueError,
            error_message='An error occurred',
            raise_from_error=False,
        )
        assert transform.original_exception == KeyError
        assert transform.new_exception == ValueError
        assert transform.error_message == 'An error occurred'
        assert not transform.from_error

    def test_repr(self):
        transform = ExceptionTransformation(
            original_exception=KeyError,
            new_exception=ValueError,
            error_message='An error occurred',
            raise_from_error=False,
        )
        expected_repr = (
            'ExceptionTransformation('
            'original_exception=KeyError, '
            'new_exception=ValueError, '
            "error_message='An error occurred', "
            'raise_from_error=False)'
        )
        assert repr(transform) == expected_repr


class TestTransformAndRaise:
    def test_bad_init(self):
        with pytest.raises(TypeError):
            Reraise(1)

    def test_transform_and_raise_with_template(self):
        transform = ExceptionTransformation(
            original_exception=KeyError,
            new_exception=ValueError,
            error_message=string.Template('Error: ${original_error_message}'),
            raise_from_error=True,
        )
        with pytest.raises(ValueError) as exc_info:
            _transform_and_raise(
                transform=transform, error=KeyError('Original error message')
            )
        assert str(exc_info.value) == "Error: 'Original error message'"
        assert exc_info.value.__cause__.__class__ == KeyError

    def test_transform_and_raise_without_template(self):
        transform = ExceptionTransformation(
            original_exception=KeyError,
            new_exception=ValueError,
            error_message='An error occurred',
            raise_from_error=False,
        )
        with pytest.raises(ValueError) as exc_info:
            _transform_and_raise(
                transform=transform, error=KeyError('Original error message')
            )
        assert str(exc_info.value) == 'An error occurred'
        assert exc_info.value.__cause__ is None


class TestRaiseTransformedException:
    def test_raise_transformed_exception(self):
        transform = ExceptionTransformation(
            original_exception=KeyError,
            new_exception=ValueError,
            error_message='An error occurred',
            raise_from_error=True,
        )
        with pytest.raises(ValueError) as exc_info:
            _raise_transformed_exception(
                [transform], error=KeyError('Original error message')
            )
        assert str(exc_info.value) == 'An error occurred'
        assert exc_info.value.__cause__.__class__ == KeyError

    def test_no_transformation_found(self, caplog):
        with pytest.raises(KeyError) as exc_info:
            _raise_transformed_exception(
                [], error=KeyError('Original error message')
            )
        assert str(exc_info.value) == "'Original error message'"


class TestReraiseDecorator:
    def test_reraise_decorator(self):
        transform = ExceptionTransformation(
            original_exception=KeyError,
            new_exception=ValueError,
            error_message='An error occurred',
            raise_from_error=True,
        )

        @_reraise_decorator([transform])
        def func():
            raise KeyError('Original error message')

        with pytest.raises(ValueError) as exc_info:
            func()
        assert str(exc_info.value) == 'An error occurred'
        assert exc_info.value.__cause__.__class__ == KeyError


class TestReraise:
    def test_reraise_context_manager(self):
        transform = ExceptionTransformation(
            original_exception=KeyError,
            new_exception=ValueError,
            error_message='An error occurred',
            raise_from_error=True,
        )

        with pytest.raises(ValueError) as exc_info:
            with Reraise(transform):
                raise KeyError('Original error message')
        assert str(exc_info.value) == 'An error occurred'
        assert exc_info.value.__cause__.__class__ == KeyError

    def test_reraise_context_manager_without_error(self):
        transform = ExceptionTransformation(
            original_exception=KeyError,
            new_exception=ValueError,
            error_message='An error occurred',
            raise_from_error=True,
        )
        with Reraise(transform):
            pass

    def test_reraise_decorator(self):
        transform = ExceptionTransformation(
            original_exception=KeyError,
            new_exception=ValueError,
            error_message='An error occurred',
            raise_from_error=True,
        )

        @Reraise(transform)
        def func():
            raise KeyError('Original error message')

        with pytest.raises(ValueError) as exc_info:
            func()
        assert str(exc_info.value) == 'An error occurred'
        assert exc_info.value.__cause__.__class__ == KeyError

    def test_reraise_decorator_without_error(self):
        transform = ExceptionTransformation(
            original_exception=KeyError,
            new_exception=ValueError,
            error_message='An error occurred',
            raise_from_error=True,
        )

        @Reraise(transform)
        def func():
            return True

        assert func()

    def test_inheritance(self):
        transform = ExceptionTransformation(
            original_exception=Exception,
            new_exception=ValueError,
            error_message='An error occurred',
            raise_from_error=True,
        )

        with pytest.raises(ValueError) as exc_info:
            with Reraise(transform):
                raise KeyError('Original error message')
        assert str(exc_info.value) == 'An error occurred'
        assert exc_info.value.__cause__.__class__ == KeyError

    def test_reraise_with_single_and_list_transformations(self):
        single_transform = ExceptionTransformation(
            original_exception=KeyError,
            new_exception=ValueError,
            error_message='Single transformation error',
            raise_from_error=True,
        )

        list_transforms = [
            ExceptionTransformation(
                original_exception=KeyError,
                new_exception=ValueError,
                error_message='List transformation error',
                raise_from_error=True,
            ),
            ExceptionTransformation(
                original_exception=TypeError,
                new_exception=RuntimeError,
                error_message='Another list transformation error',
                raise_from_error=True,
            ),
        ]

        # Test with single transformation
        with pytest.raises(ValueError) as exc_info:
            with Reraise(single_transform):
                raise KeyError('Original error message')
        assert str(exc_info.value) == 'Single transformation error'
        assert exc_info.value.__cause__.__class__ == KeyError

        # Test with list of transformations
        with pytest.raises(ValueError) as exc_info:
            with Reraise(list_transforms):
                raise KeyError('Original error message')
        assert str(exc_info.value) == 'List transformation error'
        assert exc_info.value.__cause__.__class__ == KeyError

        with pytest.raises(RuntimeError) as exc_info:
            with Reraise(list_transforms):
                raise TypeError('Original type error message')
        assert str(exc_info.value) == 'Another list transformation error'
        assert exc_info.value.__cause__.__class__ == TypeError
