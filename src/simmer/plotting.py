import matplotlib.colors as co
import matplotlib.pyplot as plt
import numpy as np
from schemas import read_yml as read

plot_config = None


def initialize_plotting(yml_filename=None):
    global plot_config
    plot_config = read.get_plotting_args(
        yml_filename
    )  # call with empty arguments


def check_plot_type(plot_type):
    """
    Ensures that invalid plot types don't make it to plotting functions.

    Inputs:
        plot_type: (string) type of plot to be used.
    """
    valid_plot_types = ["rots", "final_im", "intermediate"]
    if plot_type not in valid_plot_types:
        raise NotImplementedError(
            "Plotting is not implemented for this plot type."
        )


def zoom(image, zoom_scale):
    """
    TODO: Check that this works for odd, even zoom_scale
    TODO: write docsting
    TODO: write tests
    """
    cent_x = im_shape[0] / 2
    cent_y = im_shape[1] / 2
    zoomed = image[cent_x - zoom_scale / 2 : cent_x + zoom_scale / 2][
        cent_y - zoom_scale / 2 : cent_y + zoom_scale / 2
    ]
    return zoomed


def add_colorbars(fig, plot_type, cim):
    """
    Inputs:
        fig: (figure object) This is where the colorbars are added.
        plot_type: (string) The type of plot to add colorbars to.
    """
    check_plot_type(plot_type)
    scaling = plot_config[plot_type]["scaling"]
    text_dict = {
        "rots": "Residuals",
        "final_im": "Counts",
        "intermediate": "Counts",
    }
    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    cbar = fig.colorbar(cim, cax=cbar_ax)
    text = f"{text_dict[plot_type]}, {scaling} scaling"
    cbar.set_label(text)
    cbar.ax.tick_params(labelsize=50)


def plot_array(
    plot_type, im_array, vmin, vmax, directory, filename, extent=None
):  # pylint: disable=too-many-arguments
    """
    Plots arrays produced in the process of the pipeline.

    Inputs:
        :im_array: (3D array) array of 2D images.
        :vmin: (int) minimum for linear color mapping of plots.
        :vmax: (int) maximum for linear color mapping of plots.
        :directory: (str) path to directory to which the image file will be saved.
        :filename: (str) name of file to which the image will be saved.
        :extent: (tuple) from matplotlib documentation: controls the bounding box in data coordinates that
                                the image will fill specified as (left, right, bottom, top) in data coordinates

    Outputs:
        :fig: (Matplotlib figure) plotted figure.

    TODO: implement scaling
    TODO: write tests

    """

    def plot_few():
        fig = plt.figure(figsize=(30, 6))
        for i in range(array_len):
            ax = fig.add_subplot(
                1, array_len, i + 1
            )  # pylint: disable=invalid-name # common axis name!
            pltim = np.rot90(im_array[i, :, :], 2)
            cim = ax.imshow(
                pltim,
                origin="lower",
                cmap="plasma",
                norm=co.Normalize(vmin=vmin, vmax=vmax),
                extent=extent,
            )
            ax.tick_params(axis="both", which="major", labelsize=20)
        return fig, cim

    def plot_many():
        nrows = 4
        ncols = int(np.ceil((array_len / 4.0)))
        rowheight = nrows * 10
        colheight = ncols * 10

        fig = plt.figure(figsize=(colheight, rowheight))
        for i in range(array_len):
            ax = fig.add_subplot(
                nrows, ncols, i + 1
            )  # pylint: disable=invalid-name # common axis name!
            pltim = np.rot90(im_array[i, :, :], 2)

            cim = ax.imshow(
                pltim,
                origin="lower",
                cmap=plot_config[plot_type]["colormap"],
                norm=co.Normalize(vmin=vmin, vmax=vmax),
                extent=extent,
            )
            ax.tick_params(axis="both", which="major", labelsize=40)
        return fig, cim

    if not plot_config:
        initialize_plotting()

    # ipdb.set_trace()

    # if this shouldn't be plotted, break
    if not plot_config[plot_type]["plot"]:
        return
    array_len = np.shape(im_array)[0]

    if array_len <= 5:
        fig, cim = plot_few()

    elif array_len > 50:
        print("Too many images to plot.")
        return
    else:  # 11 images? 13 images? make it 4xn
        fig, cim = plot_many()

    fig.subplots_adjust(right=0.8)
    if plot_config[plot_type]["colorbars"]:
        add_colorbars(fig, plot_type, cim)
    plt.savefig(directory + filename)
    plt.close("all")
    return fig
