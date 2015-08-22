import numpy

def linear_regression(x, y):
	length = len(x)
	sum_x = sum(x)
	sum_y = sum(y)

	sum_x_squared = sum(map(lambda a: a * a, x))
	sum_of_products = sum([x[i] * y[i] for i in range(length)])

	a = (sum_of_products - (sum_x * sum_y) / length) / (sum_x_squared - ((sum_x ** 2) / length))
	b = (sum_y - a * sum_x) / length
	# y = a * x + b
	return (a, b)

x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
y = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

a, b = numpy.polyfit(x, y, 1)

for n in x:
	print a * n + b
