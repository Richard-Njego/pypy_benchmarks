
from pypy.module.micronumpy.arrayimpl import base
from pypy.module.micronumpy.base import W_NDimArray, convert_to_array
from pypy.module.micronumpy import support
from pypy.interpreter.error import OperationError

class ScalarIterator(base.BaseArrayIterator):
    def __init__(self, v):
        self.v = v
        self.called_once = False

    def next(self):
        self.called_once = True

    def getitem(self):
        return self.v.get_scalar_value()

    def setitem(self, v):
        self.v.set_scalar_value(v)

    def done(self):
        return self.called_once

    def reset(self):
        pass

class Scalar(base.BaseArrayImplementation):
    def __init__(self, dtype, value=None):
        self.dtype = dtype
        self.value = value

    def is_scalar(self):
        return True

    def get_shape(self):
        return []

    def get_strides(self):
        return []

    def get_backstrides(self):
        return []

    def create_iter(self, shape=None, backward_broadcast=False):
        return ScalarIterator(self)

    def get_scalar_value(self):
        return self.value

    def set_scalar_value(self, w_val):
        self.value = w_val.convert_to(self.dtype)

    def copy(self, space):
        scalar = Scalar(self.dtype)
        scalar.value = self.value
        return scalar

    def get_size(self):
        return 1

    def transpose(self, _):
        return self

    def get_real(self, orig_array):
        if self.dtype.is_complex_type():
            scalar = Scalar(self.dtype.float_type)
            scalar.value = self.value.convert_real_to(scalar.dtype)
            return scalar
        return self

    def set_real(self, space, orig_array, w_val):
        w_arr = convert_to_array(space, w_val)
        dtype = self.dtype.float_type or self.dtype
        if len(w_arr.get_shape()) > 0:
            raise OperationError(space.w_ValueError, space.wrap(
                "could not broadcast input array from shape " + 
                "(%s) into shape ()" % (
                    ','.join([str(x) for x in w_arr.get_shape()],))))
        if self.dtype.is_complex_type():
            self.value = self.dtype.itemtype.composite(
                               w_arr.get_scalar_value().convert_to(dtype),
                               self.value.convert_imag_to(dtype))
        else:
            self.value = w_arr.get_scalar_value()

    def get_imag(self, orig_array):
        if self.dtype.is_complex_type():
            scalar = Scalar(self.dtype.float_type)
            scalar.value = self.value.convert_imag_to(scalar.dtype)
            return scalar
        scalar = Scalar(self.dtype)
        if self.dtype.is_flexible_type():
            scalar.value = self.value
        else:
            scalar.value = scalar.dtype.itemtype.box(0)
        return scalar

    def set_imag(self, space, orig_array, w_val):
        #Only called on complex dtype
        assert self.dtype.is_complex_type()
        w_arr = convert_to_array(space, w_val)
        dtype = self.dtype.float_type
        if len(w_arr.get_shape()) > 0:
            raise OperationError(space.w_ValueError, space.wrap(
                "could not broadcast input array from shape " + 
                "(%s) into shape ()" % (
                    ','.join([str(x) for x in w_arr.get_shape()],))))
        self.value = self.dtype.itemtype.composite(
                            self.value.convert_real_to(dtype),
                            w_arr.get_scalar_value().convert_to(dtype),
                            )

    def descr_getitem(self, space, _, w_idx):
        raise OperationError(space.w_IndexError,
                             space.wrap("scalars cannot be indexed"))

    def getitem_index(self, space, idx):
        raise OperationError(space.w_IndexError,
                             space.wrap("scalars cannot be indexed"))

    def descr_setitem(self, space, _, w_idx, w_val):
        raise OperationError(space.w_IndexError,
                             space.wrap("scalars cannot be indexed"))

    def setitem_index(self, space, idx, w_val):
        raise OperationError(space.w_IndexError,
                             space.wrap("scalars cannot be indexed"))
    def set_shape(self, space, orig_array, new_shape):
        if not new_shape:
            return self
        if support.product(new_shape) == 1:
            arr = W_NDimArray.from_shape(new_shape, self.dtype)
            arr_iter = arr.create_iter(new_shape)
            arr_iter.setitem(self.value)
            return arr.implementation
        raise OperationError(space.w_ValueError, space.wrap(
            "total size of the array must be unchanged"))

    def reshape(self, space, orig_array, new_shape):
        return self.set_shape(space, orig_array, new_shape)

    def create_axis_iter(self, shape, dim, cum):
        raise Exception("axis iter should not happen on scalar")

    def swapaxes(self, orig_array, axis1, axis2):
        raise Exception("should not be called")

    def fill(self, w_value):
        self.value = w_value

    def get_storage_as_int(self, space):
        raise OperationError(space.w_ValueError,
                             space.wrap("scalars have no address"))

    def argsort(self, space, w_axis):
        return space.wrap(0)

    def astype(self, space, dtype):
        return W_NDimArray.new_scalar(space, dtype, self.value)

    def base(self):
        return None

    def get_buffer(self, space):
        raise OperationError(space.w_ValueError, space.wrap(
            "cannot point buffer to a scalar"))

