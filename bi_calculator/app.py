#!/usr/bin/env python3

# -*- coding: utf-8 -*-
#
#  Copyright 2017 Bruno Ribeiro-Goncalves <bfgoncalves@medicina.ulisboa.pt>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

"""
Belonging Index Calculator

This program calculates the belonging index of a set of profiles.

Input types (tab delimited):
    - distance matrix
    - profile file

Test:
    python3 app.py -o data -p data/wg_p.tab -c data/class_wg.txt

"""

# Library import
import os
import argparse
from utils.bi_calculator import BiCalculator
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="Bi Calculator",
        description="Calculate the belonging index of a set of allelic "
                    "profiles by adding a distance matrix as input and a  "
                    "classification file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument_group("Required Options")
    parser.add_argument("-o", "--output-dir", dest="outdir",
                        help="Path for output directory",
                        required=False, default=".")
    parser.add_argument("-d", "--distance-matrix", dest="dm",
                        help="Path to distance matrix file",
                        required=False)
    parser.add_argument("-c", "--classification", dest="c",
                        help="Path to classification file (Tab separated)",
                        required=True)
    parser.add_argument("-p", "--profiles", dest="p",
                        help="Path to profiles file (Tab separated)",
                        required=False)

    args = parser.parse_args()

    # Create outut directory if not exists
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    # Initialize BiCalculator class
    bicalculator = BiCalculator()

    if not args.p and not args.d:
        raise ValueError('A profile or matrix file is required.')

    elif args.p:
        print("Loading profiles file...")
        bicalculator.load_profiles_file(args.p)
        print("Updating distance index...")
        index_name = bicalculator.update_index(args.p, args.outdir)

    else:
        # Load distance matrix file
        if os.path.isfile(args.dm):
            print("Loading distance matrix file...")
            bicalculator.load_matrix_file(args.dm)
            bicalculator.get_headers()

    # Load classification file
    if os.path.isfile(args.c):
        print("Loading classification file...")
        bicalculator.load_classification_file(args.c)
        bicalculator.count_n_classifier()

    print('Calculating Bi...')
    counter_bi = 0;
    if not args.p:
        # Calculate Bi for all entries
        for value in bicalculator.headers:
            counter_bi += 1
            print('Calculating Bi %s out of %s...'
                  % (str(counter_bi), str(len(bicalculator.headers))), end='\r')
            sys.stdout.flush()
            bicalculator.calculate_bi_from_matrix(value)
    else:
        for index in bicalculator.headers:
            counter_bi += 1
            print('Calculating Bi %s out of %s...'
                  % (str(counter_bi), str(len(bicalculator.headers))), end='\r')
            sys.stdout.flush()
            profile_string = "\t".join(bicalculator.profiles.loc[
                                           index].apply(str))
            profiles_length = len(bicalculator.profiles.loc[
                                           index].values)

            entries = bicalculator.get_closest_profiles(
                index, profile_string, index_name, profiles_length/2)

            bicalculator.calculate_bi_from_profiles(index, entries)

    print()
    print("Plotting data...")

    # Layout for the plot display
    # COL x ROW
    traces = [[], []]

    # Plot average Bi by classification
    bicalculator.average_bi_per_class()
    traces[0].append(
        bicalculator.trace_bi_bar(bicalculator.bi_means_by_class, "cl_"))

    # Plot all Bi
    traces[1].append(
        bicalculator.trace_bi_histogram(bicalculator.bis_class["bis"]))

    # Set titles
    titles = ("Bi Means by Classification", "All Bi")

    # Plot data
    bicalculator.plot_data(titles, *traces)
    print("Done!")


if __name__ == "__main__":
    main()
