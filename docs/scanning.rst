.. _scanning-the-sky:

Scanning the sky
================

This chapter provides an explanation of the functions to simulate the
observation of the sky. The functions described here take a description of the
scanning strategy as input (see :ref:`scanning-strategy`) and produce a timeline
as output. 


.. _callback-functions:

Callback functions
------------------

Since the amount of data produced by the function described in this chapter is
potentially huge, their return values are not returned using the classic
Python's ``return`` statement. Rather, a `callback function` is called whenever
a new chunk of output data is ready.

Let's explain this point with a very simple (and unrealistic) example. This is a
function that accepts two lists ``X`` and ``Y`` and returns a list of all the pairs ``(x, y)``::

    from typing import Any, List, Tuple

    def pairs(x_list: List[Any], y_list: List[Any]) -> List[Tuple[Any, Any]]:
        return [(x, y) for x in x_list for y in y_list]

    print(pairs(['a', 'b', 'c'], [1, 2]))

The output of this program is a list containing six elements::

    [('a', 1), ('a', 2), ('b', 1), ('b', 2), ('c', 1), ('c', 2)]

The function above returns the result using the ``return`` statement. This is ok
when the output is small enough that it can be entirely kept in memory. However,
this function can potentially return a very large list, which might fill all the
computer's memory. A `callback function` can be used here, at the price of making
the implementation a bit more complex:

    from typing import Any, List, Tuple

    def pairs(x_list: List[Any], y_list: List[Any], callback):
        for cur_y in y_list:
            callback([(x, cur_y) for x in x_list])

    pairs(['a', 'b', 'c'], [1, 2], callback=lambda x: print(x))

In this case, the output is the following::

    [('a', 1), ('b', 1), ('c', 1)]
    [('a', 2), ('b', 2), ('c', 2)]

The fact that the output is spread across two lines is a symptom that the
callback function ``lambda`` has been called twice. In this way, the program had
never to keep the whole list of six elements in memory: in fact, it never keeps
more than three elements in memory at the same time.

One is not forced to use anonymous ``lambda`` functions to use callbacks, of
course::

    from typing import Any, List, Tuple

    def pairs(x_list: List[Any], y_list: List[Any], callback):
        for cur_y in y_list:
            callback([(x, cur_y) for x in x_list])

    def print_callback(x):
        print(x)

    pairs(['a', 'b', 'c'], [1, 2], callback=print_callback)


A potential disadvantage of functions used as callbacks is the fact that they
have no `state`, i.e., they cannot keep memory of previous calls. Let's suppose
for instance that we have implemented ``pairs`` using callbacks because we
feared the possibility that the result string was too large, but we're going to
use it in a situation where we're 100% sure the result will `do` fit in memory.
In this case, we would like to keep all the pairs in one single list, instead of
getting ``print_callback`` called twice with two lists of three elements each.
In other words: what can we do if we want to get the result as a `single` list
with `six` elements? The most naive approach would be to use a global variable::

    from typing import Any, List, Tuple

    def pairs(x_list: List[Any], y_list: List[Any], callback):
        for cur_y in y_list:
            callback([(x, cur_y) for x in x_list])

    list_of_pairs = []
    def my_callback(x):
        global list_of_pairs
        list_of_pairs += x

    pairs(['a', 'b', 'c'], [1, 2], callback=my_callback)
    print(list_of_pairs)

The result is what we expect::

    [('a', 1), ('b', 1), ('c', 1), ('a', 2), ('b', 2), ('c', 2)]

However, this approach is not elegant at all, as global variables are something
that must be used as little as possible, because of `many known problems
<http://wiki.c2.com/?GlobalVariablesAreBad>`_ in code maintenability.
Fortunately, Python provides a nice and elegant solution through the `__call__
method <https://docs.python.org/3/reference/datamodel.html#object.__call__>`_::

    from typing import Any, List, Tuple

    def pairs(x_list: List[Any], y_list: List[Any], callback):
        for cur_y in y_list:
            callback([(x, cur_y) for x in x_list])

    class MyCallback:
        def __init__(self):
            self.result = []

        def __call__(self, x):
            self.result += x
    
    my_callback = MyCallback()
    pairs(['a', 'b', 'c'], [1, 2], callback=my_callback)
    print(my_callback.result)
    
The result is the same as in our previous example::

    [('a', 1), ('b', 1), ('c', 1), ('a', 2), ('b', 2), ('c', 2)]

However, here we have avoided the usage of global variables by implementing a
so-called `callback class`, ``MyCallback``. An object which implements the
``__call__`` method can be used as a class object and as a function at the same
time: the fact that it behaves like a class allows it to keep a `state`, i.e.
the member variable ``self.result``, while the fact that it behaves like a
function allows it to be called by our function ``pairs``. Refer to the `Python
documentation
<https://docs.python.org/3/reference/datamodel.html#object.__call__>`_ for an
explanation; what Python does is really trivial, but it allows some powerful
possibilities, as you can see.


.. _callbacks-and-stripeline:

Callbacks and Stripeline
------------------------

Having presented the general theory of callback functions and callback classes,
let's turn to their usave in Stripeline. Callbacks are typically used as a way
for TOD-generating functions to returns the TOD, as these are potentially very
large objects and do not typically fit in memory.

One example is the :func:`stripeline.scanning.generate_pointings` function,
which accepts a ``tod_callback`` argument. This callback is called whenever a
new chunk of the TOD has been computed, and it accepts four parameters:

1. `pointings` is a 4xn matrix containing the time, the colatitude, the
   longitude, and the polarization angle of the `i`-th sample;
2. `scanning` is a copy of the object containing the details of the scanning
   strategy to use for the generation of the TOD;
3. `dir_vec` is a 3-element vector containing the direction of the beam axis;
4. `index` is an integer which is increased every time the callback is called.

An example of use is the following::

    import stripeline.scanning as sc

    def my_callback(pointings,
                scanning: sc.ScanningStrategy,
                dir_vec,
                index: int):
        pass

    scanning = sc.ScanningStrategy(wheel3_rpm=1.0,
                                wheel2_angle0_deg=45.0,
                                latitude_deg=28.3,
                                overall_time_s=3600.0,
                                sampling_frequency_hz=50.0)
    sc.generate_pointings(scanning=scanning,
                        dir_vec=[0., 0., 1.],
                        num_of_chunks=1,
                        tod_callback=my_callback)

We have implemented here the simplest callback: one that does nothing! Of
course, it is not really useful to generate pointings and immediately throw them
away, so we turn to a more realistic example. We assume that we are not going to
produce large TODs, so that they can be fully kept in memory. Using the idea
presented in the previous section (:ref:`callback-functions`), we can implement
``my_callback`` as a callback class::

    import numpy as np

    class MyCallback:
        def __init__(self):
            self.time = np.array([], dtype=np.float64)
            self.theta = np.array([], dtype=np.float64)
            self.phi = np.array([], dtype=np.float64)
            self.psi = np.array([], dtype=np.float64)

        def __call__(self, pointings, scanning, dir_vec, index):
            self.time = np.concatenate((self.time, pointings[:, 0]))
            self.theta = np.concatenate((self.theta, pointings[:, 0]))
            self.phi = np.concatenate((self.phi, pointings[:, 0]))
            self.psi = np.concatenate((self.psi, pointings[:, 0]))

At the end of the call to ``sc.generate_pointings``, the callback object will
contain all the pointings and will be accessible like any other class::

    my_callback = MyCallback()

    sc.generate_pointings(..., tod_callback=my_callback)
    
    print('Time: ', my_callback.time)
    print('Colatitude: ', my_callback.theta)
    print('Longitude: ', my_callback.phi)
    print('Polarization angle: ', my_callback.psi)

Another application might be to save the data into binary files, using NumPy's
`savetxt
<https://docs.scipy.org/doc/numpy/reference/generated/numpy.savetxt.html>`_::

    import os.path
    import numpy as np

    class MyCallback:
        def __init__(self, output_path: str):
            self.output_path = output_path

        def __call__(self, pointings, scanning, dir_vec, index):
            file_name = os.path.join(output_path, 'tod{0:04}.bin'.format(index))
            np.savetxt(file_name, pointings)

Here we take advantage of the fact that
:func:`stripeline.scanning.generate_pointings` passes an `index` parameter which
contains an increasing number: therefore, the files created by the callback will
be named ``tod0000.bin``, ``tod0001.bin``, etc.

Stripeline provides a class, :class:`~stripeline.scanning.TodWriter`, which is
similar to `MyCallback` but saves the TODs in FITS files.


.. _quick-generation-of-pointing-timelines:

Quick generation of pointing timelines
--------------------------------------

.. automodule:: stripeline.scanning
                :members:


.. _accurate-generation-of-pointing-timelines:

Accurate generation of pointing timelines
-----------------------------------------

To be written.
