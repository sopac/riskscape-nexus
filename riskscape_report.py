import numpy as np
from matplotlib import pyplot as plt
import datetime
import pandas as pd
import matplotlib as mpl

mpl.rcParams["axes.formatter.useoffset"] = False

dateLabel = datetime.datetime.now().strftime("%d/%m/%Y")

df = pd.read_csv("average-loss.csv")
year = df.Year
scenario = df.Scenario
aal = df.Total_AAL

y_axis = df["Year"].unique()
y_axis_sorted = np.sort(y_axis)

percentiles = df["Percentile"].unique()
percentiles_sorted = np.sort(percentiles)

scenario = df["Scenario"].unique()

def first_page():
    fig, ax = plt.subplots(figsize=tuple(i / 2.54 for i in (21, 29.7)), dpi=200)
    ax.text(
        -0.05,
        -0.060,
        "Date Printed:" + dateLabel,
        transform=ax.transAxes,
        fontsize=8,
        verticalalignment="top",
    )
    # ax.text(0.76, -0.060,"Copyright 2023 SPC", transform=ax.transAxes,fontsize=8, verticalalignment='top')
    ax.text(
        0.01,
        1.12,
        "Riskscape Infographic",
        transform=ax.transAxes,
        fontsize=16,
        verticalalignment="top",
        color="#BB3F3F",
    )
    ax.text(
        0.01,
        1.09,
        "Cook Islands Government",
        transform=ax.transAxes,
        fontsize=8,
        verticalalignment="top",
        color="#BB3F3F",
    )
    ax.text(
        0.01,
        1.07,
        "Contact: contactus@spc.int",
        transform=ax.transAxes,
        fontsize=6,
        verticalalignment="top",
        color="#BB3F3F",
    )
    ax.axis("off")
    axline = fig.add_axes([0.001, 0.90, 0.99, 0.02])
    axline.axhline(y=0.5, color="#BB3F3F", linestyle="-", linewidth=15)
    axline.axis("off")
    axline.text(
        0.11,
        1.043,
        "Riskcape Report for Cook Islands, model run: 2023-05-30 16:00 UTC",
        fontweight="bold",
        transform=ax.transAxes,
        fontsize=8,
        verticalalignment="top",
        color="white",
    )

    ###PLOT 1 ###
    ax11 = fig.add_axes([0.095, 0.73, 0.88, 0.15])
    ax11.yaxis.get_major_formatter().set_scientific(False)
    ax11.yaxis.get_major_formatter().set_useOffset(False)
    for s in scenario:
        dataset_arr2 = df.loc[df["Scenario"] == s]
        dataset_arr = dataset_arr2.loc[df["Percentile"] == 50]
        hs = dataset_arr["Total_AAL"]
        year = dataset_arr["Year"]
        ax11.plot(year.values, hs.values, label=str(s))

    ax11.set_ylabel("Total AAL", fontsize=6)
    ax11.set_xlabel("Year", fontsize=6)
    ax11.set_title("50th Percentile", fontsize=6)
    ax11.xaxis.grid(True, which="major", linestyle="--")
    ax11.yaxis.grid(True, which="major", linestyle="dashdot", color="#dfdfdf")
    ax11.set_axisbelow(True)
    ax11.tick_params(axis="both", which="both", labelsize=6)
    ax11.legend(loc="upper left", prop={"size": 6})
    ###PLOT 1 ###

    ###PLOT 2 ###
    ax11 = fig.add_axes([0.095, 0.53, 0.88, 0.15])
    ax11.yaxis.get_major_formatter().set_scientific(False)
    ax11.yaxis.get_major_formatter().set_useOffset(False)
    for s in scenario:
        dataset_arr2 = df.loc[df["Scenario"] == s]
        dataset_arr = dataset_arr2.loc[df["Percentile"] == 50]
        hs = dataset_arr["SLR"]
        year = dataset_arr["Year"]
        ax11.plot(year.values, hs.values, label=str(s))

    ax11.set_ylabel("SLR", fontsize=6)
    ax11.set_xlabel("Year", fontsize=6)
    ax11.set_title("50th Percentile", fontsize=6)
    ax11.xaxis.grid(True, which="major", linestyle="--")
    ax11.yaxis.grid(True, which="major", linestyle="dashdot", color="#dfdfdf")
    ax11.set_axisbelow(True)
    # ax.set_xticklabels(hs.values)
    ax11.tick_params(axis="both", which="both", labelsize=6)
    ax11.legend(loc="upper left", prop={"size": 6})
    ###PLOT 2 ###

    # LOGO
    im = plt.imread("risk.jpg")
    newax = fig.add_axes([0.76, 0.92, 0.20, 0.06], anchor="NE", zorder=-1)
    newax.imshow(im)
    newax.axis("off")
    return fig


fig = first_page()
fig.savefig("test.pdf")
