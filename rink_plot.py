import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.transforms import Affine2D
import numpy as np


def arc_patch(center, width, height, theta1, theta2, resolution=50, **kwargs):
    """
    Return matplotlib patch for a filled-in half-ellipse.

    Courtesy of https://stackoverflow.com/questions/30642391/how-to-draw-a-filled-arc-in-matplotlib
    """

    # generate the points
    theta = np.linspace(np.radians(theta1), np.radians(theta2), resolution)
    points = np.vstack((width * np.cos(theta) + center[0],
                        height * np.sin(theta) + center[1]))

    # build the polygon and add it to the axes
    poly = mpatches.Polygon(points.T, closed=True, **kwargs)

    return poly


def draw_rink(is_horizontal=True, x_range=None, y_range=None, rink_length=None):
    """
    Draw a plot of an NHL ice surface.

    Plotting is based on the NHL coordinate system which goes from -100 to 100 on the x-axis and -42.5 to 42.5
    on the y-axis.

    Args:
        is_horizontal: bool; default=True
            Indicates whether to draw the rink horizontally (left and right as end boards) or vertically (top and
            bottom as end boards).

            When is_horizontal is False, x,y-coordinates will have to be reversed (x,y => y,x) when adding to the plot.

        x_range: "half", "ozone", float, or list; default=None
            Lower and upper bounds of the default display on the x-axis.  The entire rink will be drawn regardless,
            this only controls what section of the rink's length is initially shown.

            Coordinates can range from -100 to 100.

            "half": bounds set to 0 and 100.
            "ozone": bounds set to 25 and 100.
            float: value will be used as the lower bound with 100 as the upper bound.
            list: will attempt to use the first element as the lower bound, the second as the upper bound.

            If none of the above are provided, the bounds will be set to -100 and 100.

        y_range: "half", float or list; default=None
            Lower and upper bounds of the default display on the y-axis.  The entire rink will be drawn regardless,
            this only controls what section of the rink's width is initially shown.

            Coordinates can range from -42.5 to 42.5.

            "half": bounds set to 0 and 42.5.
            float: value will be used as the lower bound with 42.5 as the upper bound.
            list: will attempt to use the first element as the lower bound, the second as the upper bound.

            If none of the above are provided, the bounds will bet set to -42.5 and 42.5.

        rink_length: float; default=None
            Length of the rink (end board to end board) for plotting.

            If None, will use default of 14 if using a full horizontal rink or 8 otherwise.
            Width is set automatically based on rink_length and dimensions used.

    Returns:
        matplotlib Axes.
            Axes for the rink plot.
    """

    if x_range in ("half", "ozone"):
        x_range = [0 if x_range == "half" else 25, 100]
    elif isinstance(x_range, (int, float)):
        x_range = [x_range, 100]
    elif isinstance(x_range, list) and x_range:
        x_range.append(100)
        x_range = x_range[:2]
    else:
        x_range = [-100, 100]

    if x_range[0] > x_range[1]:
        x_range = x_range[::-1]

    x_range = [max(-100, x_range[0]), min(100, x_range[1])]

    if x_range[0] >= 100:
        x_range = [-100, 100]

    if y_range == "half":
        y_range = [0, 42.5]
    elif isinstance(y_range, (int, float)):
        y_range = [y_range, 42.5]
    elif isinstance(y_range, list) and y_range:
        y_range.append(42.5)
        y_range = y_range[:2]
    else:
        y_range = [-42.5, 42.5]

    if y_range[0] > y_range[1]:
        y_range = y_range[::-1]

    y_range = [max(-42.5, y_range[0]), min(100, y_range[1])]

    if y_range[0] >= 42.5:
        y_range = [-42.5, 42.5]

    delta_x = x_range[1] - x_range[0]
    delta_y = y_range[1] - y_range[0]
    if rink_length is None:
        rink_length = 14 if is_horizontal and delta_x == 200 else 8

    length = rink_length
    width = rink_length * delta_y / delta_x
    if not is_horizontal:
        length, width = width, length
    plt.figure(figsize=(length, width))

    ax = plt.gca()
    ax.set_aspect("equal")

    patches = []

    # red line
    # 1' in width
    # all other red lines are 2" in width, but will be drawn thicker
    patches.append(mpatches.Rectangle((-0.5, -42.5), 1, 85, color="red", zorder=0))

    # center faceoff
    patches.append(mpatches.Circle((0, 0), .5, color="blue", fill=True, zorder=0))

    # center circle
    patches.append(mpatches.Circle((0, 0), 15, color="red", fill=False, zorder=0))

    # ref half-circle
    # 10' radius
    patches.append(mpatches.Arc((0, -42.5), 20, 20, theta1=0, theta2=180, color="red", zorder=0))

    # 5'7" between, 5'7" = 67", divide by 12 to get feet, divide by 2 to get half on each side
    between_hashmarks = 67 / 24

    # edge of the circle
    hashmark_edge = (15**2 - between_hashmarks**2)**.5

    for side in (-1, 1):
        # blue lines
        # 1' in width
        # neutral zone is 50', half on each side = 25
        patches.append(mpatches.Rectangle((25 * side, -42.5), side, 85, color="blue", zorder=0))

        for y in (-22, 22):
            # faceoff dots
            # 2' diameter
            # offensive zone dots are 20' from the goal line with 44' in between
            patches.append(mpatches.Circle((69 * side, y), 1, color="red", fill=True, zorder=0))

            # neutral zone dots
            # 5' from the bluelines (25 - 5 = 20), 44' in between
            patches.append(mpatches.Circle((20 * side, y), 1, color="red", fill=True, zorder=0))

            # faceoff circles
            # 15' radius
            patches.append(mpatches.Circle((69 * side, y), 15, color="red", fill=False, zorder=0))

            for circle_side in (-1, 1):
                # faceoff lines
                # 4' length, 3' width
                ax.plot((69 * side * circle_side + 2 * side, 69 * circle_side * side + 6 * side), (y + 1.75, y + 1.75),
                        "red", zorder=0)
                ax.plot((69 * side * circle_side + 2 * side, 69 * circle_side * side + 6 * side), (y - 1.75, y - 1.75),
                        "red", zorder=0)
                ax.plot((69 * side * circle_side + 2 * side, 69 * circle_side * side + 2 * side), (y + 1.75, y + 4.75),
                        "red", zorder=0)
                ax.plot((69 * side * circle_side + 2 * side, 69 * circle_side * side + 2 * side), (y - 1.75, y - 4.75),
                        "red", zorder=0)

                # hashmarks
                ax.plot((69 * side * circle_side + between_hashmarks * side,
                         69 * side * circle_side + between_hashmarks * side),
                        (y - hashmark_edge, y - hashmark_edge - 2),
                        "red", zorder=0)
                ax.plot((69 * side * circle_side + between_hashmarks * side,
                         69 * side * circle_side + between_hashmarks * side),
                        (y + hashmark_edge, y + hashmark_edge + 2),
                        "red", zorder=0)

        # nets
        # depth is 40" with 20" radius corner
        patches.append(mpatches.Rectangle((89*side, -3), 20.0/12 * side, 6, color="grey", zorder=2))
        patches.append(arc_patch(((89 + 20.0/12) * side, 0), 20.0/12, 3, 270 + 180 * side, 270,
                                 fill=True, color="grey", zorder=2))

        # creases
        # rectangle extends 4'6" out, then ellipse of width 2'
        patches.append(mpatches.Rectangle((89*side, -4), 4.5*-side, 8, color="lightblue", zorder=-1))
        patches.append(arc_patch((84.5*side, 0), 2, 4, 270-180*side, 270, fill=True, color="lightblue", zorder=-1))

        # outline of crease
        ax.plot((89*side, 84.5*side), (-4, -4), "red", zorder=1)
        ax.plot((89*side, 84.5*side), (4, 4), "red", zorder=1)
        patches.append(mpatches.Arc((84.5*side, 0), 4, 8, theta1=90*side, theta2=270*side, color="red", zorder=1))

        # restricted zone
        # 8' from the post to 11' from the post (posts are 3' from center)
        ax.plot((89*side, 100*side), (-11, -14), "red", zorder=0)
        ax.plot((89*side, 100*side), (11, 14), "red", zorder=0)

        # curves at end of boards
        # arc of a circle with 28' radius
        patches.append(mpatches.Arc(((100 - 28) * side, 42.5 - 28), 56, 56,
                                    theta1=45 - 45 * side, theta2=135 - 45 * side,
                                    color="black", zorder=2))
        patches.append(mpatches.Arc(((100 - 28) * side, -42.5 + 28), 56, 56,
                                    theta1=225 + 45 * side, theta2=135 - 135 * side,
                                    color="black", zorder=2))

        # side boards
        ax.plot((100 - 28, 28 - 100), (42.5 * side, 42.5 * side), "black", zorder=2)
        # end boards
        ax.plot((100 * side, 100 * side), (42.5 - 28, 28 - 42.5), "black", zorder=2)

        # goal lines
        # 11' from end boards
        # boards curl in arc of circle with 28' radius
        # distance from center of circle to side boards = 28'
        # distance from center of circle to goal line = 28' - 11'
        # distance from center of ice (on y-axis) to center of circle = 42.5 - 28
        end_board_y = np.sqrt(28 ** 2 - (28 - 11) ** 2) + (42.5 - 28)
        ax.plot((89 * side, 89 * side), (-end_board_y, end_board_y), "red", zorder=1)

    ax.tick_params(axis="both", which="both", bottom=False, left=False, labelbottom=False, labelleft=False)

    # rotate everything 90 degrees if displaying rink vertically
    trans = Affine2D().rotate_deg(0 if is_horizontal else 90) + ax.transData

    for patch in patches:
        patch.set_transform(trans)
        ax.add_patch(patch)

    for line in ax.lines:
        line.set_transform(trans)

    if not is_horizontal:
        old = ax.axis()
        ax.axis(old[2:4] + old[0:2])
        x_range, y_range = y_range, x_range

    # only display the specified region of the rink
    ax.set_xlim(*x_range)
    ax.set_ylim(*y_range)

    if not is_horizontal:
        ax.invert_yaxis()

    return ax
