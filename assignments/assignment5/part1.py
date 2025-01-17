from imp import lock_held
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy import optimize


###########################################
# Functions to implement:
###########################################

#########################################################################
# contact_points: a set of contact point positions [[pix; piy; piz] ...]; Nx3 ndarray
# contact_normals: a set of inward-pointing directions of contact normals [[nix; niy; niz]]; Nx3  ndarray
# w: a set of normalized contact screws [[cix; ciy; ciz; c0ix; c0iy; c0iz] ] such that norm([cix; ciy; ciz])=1; Nx6 ndarray
#########################################################################


def contact_screw_3d(contact_points: np.ndarray, contact_normals: np.ndarray) -> np.ndarray:
    wrench = []
    for i in range(contact_points.shape[0]):
        normal = np.array(contact_normals[i])
        C = normal / np.linalg.norm(normal)
        C0 = np.cross(contact_points[i], normal)
        wrench_i = np.array([C[0], C[1], C[2], C0[0], C0[1], C0[2]])
        wrench.append(wrench_i)
    wrench = np.array(wrench)
    return wrench

#########################################################################
# N: the number of contact points; scalar
# contact_points: a set of contact point positions [[pix; piy; piz] ...]; Nx3 matrix
# contact_normals: a set of inward-pointing directions of contact normals [[nix; niy; niz] ...]; Nx3 matrix
# mu: the coefficient of (static) friction; scalar
# n_fc : the number of side facets of a linearized polyhedral friction cone; scalar
# contact_points_FC: a set of contact point positions of edges of polyhedral friction cones [[pijx; pijy; pijz] ...]; Nx3 matrix
# contact_normals_FC: a set of inward-pointing directions of edges of polyhedral friction cones [[sijx; sijy; sijz] ...]; Nx3 matrix
#########################################################################


def friction_cone_3d(contact_points: np.ndarray, contact_normals: np.ndarray, mu: float, n_fc: int) -> tuple:
    #
    # your code here
    #
    #
    contact_points_FC = []
    contact_normals_FC = []
    N = contact_points.shape[0]
    cone_angle = np.arctan(mu)

    for i in range(N):
        pass
    

    return contact_points_FC, contact_normals_FC


#########################################################################
# w: a set of normalized contact screws [[cix; ciy; ciz; c0ix; c0iy; c0iz] ...]; Nx6 matrix
# is_fc: flag which is true if the grasp achieves force closure; bool
# z_max: maximum objective function value at optimal point; float
#########################################################################
def is_force_closure(w: np.ndarray) -> tuple:
    is_FC = False

    # W = set of normalized contact screws
    wc = 1.0 / len(w) * np.sum(w, axis=0)
    T = w - wc
    p = lambda x: scipy.optimize.linprog(x, A_ub=T, b_ub=np.ones(len(w))).fun
    print('W:', w, '\n', 'wc:', wc, '\n', 'T:', T, '\n', 'T rank:', np.linalg.matrix_rank(T), '\n', 'p(-wc):', -p(wc))
    if np.linalg.matrix_rank(T) < 6: # "< 3" for planar, "< 6" for 3D
        is_FC = False
    else:
        # NOTE: linprog does minimize, but we need maximize, so compute -p(wc) rather than p(-wc)
        is_FC = -p(wc) < 1
    z_max = -p(wc)
    # return -p(wc) < 1
    return is_FC, z_max


def main(testcase):

    if testcase == 0:
        # Case 0
        contact_points = np.array(
            [[2, 0, 0], [0, 1.5, 0], [0, 0, 2], [1.2, -2, 0]])
        # inward-pointing contact normal direction
        contact_normals = np.array(
            [[-1, 0, 0], [0, -1, 0], [0, 0, -1], [0, 1, 0]])

        # friction coefficient
        mu = 0.5

        # the number of side facets of a linearized polyhedral friction cone
        n_friction_cone = 100
    elif testcase == 1:
        # Case 1
        contact_points = np.array([[1, 1, 1], [-1, 1, -1], [0, -2, -1]])
        # inward-pointing contact normal direction
        contact_normals = np.array([[-1, -1, -1], [1, -1, 0], [0, 2, 1]])
        # friction coefficient
        mu = 0.5
        # the number of side facets of a linearized polyhedral friction cone
        n_friction_cone = 100
    elif testcase == 2:
        # Case 2
        contact_points = np.array([[-0.81, 1.26, 1.23], [-1.75, -1.37, 0.74], [
            1.49, 0.85, -1.39], [0.49, -2.57, -0.39], [1.23, -1.04, 1.20]])
        # % relative rotation matrix(first column in R, i.e., x-axis of local frame, is the pushing direction)
        contact_normals = np.array(
            [[0, -1, 0], [1, 0, 0], [0, -1, 0], [0, 1, 0], [0, 0, 1]])
        # friction coefficient
        mu = 0.2

        #  the number of side facets of a linearized polyhedral friction cone
        n_friction_cone = 100
    else:
        raise IndexError(
            "Test case does not exist. Provide either 0,1 or 2 as input argument.")

    # normalized screw coordinates of contact normals
    wrench = contact_screw_3d(contact_points, contact_normals)

    # draw contact screws
    # draw_contact_screw(contact_points, wrench)

    # force closure test (1: true, 0: false)
    is_FC, z_max = is_force_closure(wrench)

    # Q3 Frictional point contact

    # friction cone approximation
    contact_points_FC, contact_normals_FC = friction_cone_3d(
        contact_points, contact_normals, mu, n_friction_cone)

    # normalized screw coordinates of contact normals
    wrench_friction = contact_screw_3d(contact_points_FC, contact_normals_FC)

    # draw contact screw
    # draw_contact_screw(contact_points_FC, contact_normals_FC, n_friction_cone)

    # force closure test (1: true, 0: false)
    is_FC_friction, z_max_friction = is_force_closure(wrench_friction)

    # print results
    print('force closure without friction:', is_FC,
          '  maximum objective function value: ', z_max)
    print('force closure with friction:', is_FC_friction,
          '  maximum objective function value: ', z_max_friction)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Parse different test cases.')
    parser.add_argument('testcase', type=int,

                        help='Call file with an index for the respective test cases (0: an example from references [1] and [2], 1+2: are test cases for grading)')
    try:
        args = parser.parse_args()
        testcase = args.testcase
    except:
        print("No testcase specified. Running default testcase 0.")
        testcase = 1

    main(testcase)
