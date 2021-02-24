import numpy as np
from sklearn.linear_model import LinearRegression


def build_convex_hull(points, is_sorted=False):
    if not is_sorted:
        points.sort(axis=0)
    first_point = points[0]
    last_point = points[-1]
    upper_bound = [first_point]
    lower_bound = [first_point]
    for i, point in enumerate(points[1:]):
        point_sign = np.cross(last_point - first_point, point - first_point)
        if i == len(points) - 2 or point_sign > 0:
            while len(upper_bound) > 1 and np.cross(upper_bound[-1] - upper_bound[-2],
                                                    point - upper_bound[-2]) >= 0:
                upper_bound.pop()
            upper_bound.append(point)
        if i == len(points) - 2 or point_sign < 0:
            while len(lower_bound) > 1 and np.cross(lower_bound[-1] - lower_bound[-2],
                                                    point - lower_bound[-2]) <= 0:
                lower_bound.pop()
            lower_bound.append(point)

    return np.array(lower_bound), np.array(upper_bound)


def get_upper_bound(points, is_sorted=False):
    return build_convex_hull(points, is_sorted)[1]


def get_lower_bound(points, is_sorted=False):
    return build_convex_hull(points, is_sorted)[0]


def put_line(points):
    model = LinearRegression().fit(points.T[0].reshape(len(points), 1), points.T[1])
    return [model.coef_[0], model.intercept_]
