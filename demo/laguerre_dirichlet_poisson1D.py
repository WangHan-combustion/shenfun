r"""
Solve Poisson equation in 1D with homogeneous Dirichlet bcs on the domain [0, inf)

    \nabla^2 u = f,

The equation to solve for a Laguerre basis is

     (\nabla u, \nabla v) = -(f, v)

"""
import os
import sys
from sympy import symbols, sin, exp, lambdify
import numpy as np
from shenfun import inner, grad, TestFunction, TrialFunction, \
    Array, Function, Basis

assert len(sys.argv) == 2, 'Call with one command-line argument'
assert isinstance(int(sys.argv[-1]), int)

# Use sympy to compute a rhs, given an analytical solution
x = symbols("x")
ue = sin(2*x)*exp(-x)
fe = ue.diff(x, 2)

# Lambdify for faster evaluation
ul = lambdify(x, ue, 'numpy')
fl = lambdify(x, fe, 'numpy')

# Size of discretization
N = int(sys.argv[-1])

SD = Basis(N, 'Laguerre', bc=(0, 0))
X = SD.mesh()
u = TrialFunction(SD)
v = TestFunction(SD)

# Get f on quad points
fj = Array(SD, buffer=fl(X))

# Compute right hand side of Poisson equation
f_hat = Function(SD)
f_hat = inner(v, -fj, output_array=f_hat)

# Get left hand side of Poisson equation
A = inner(grad(v), grad(u))

f_hat = A.solve(f_hat)
uj = f_hat.backward()
uh = uj.forward()

# Compare with analytical solution
ua = ul(X)
print("Error=%2.16e" %(np.linalg.norm(uj-ua)))
assert np.allclose(uj, ua, atol=1e-5)

point = np.array([0.1, 0.2])
p = SD.eval(point, f_hat)
assert np.allclose(p, ul(point), atol=1e-5)

if not 'pytest' in os.environ:
    import matplotlib.pyplot as plt
    xx = np.linspace(0, 16, 100)
    plt.plot(xx, ul(xx), 'r', xx, uh.eval(xx), 'bo', markersize=2)
    plt.show()
