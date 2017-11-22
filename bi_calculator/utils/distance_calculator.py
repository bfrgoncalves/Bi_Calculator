"""
Distance Calculator class

This class have all the methods required to calculate the closest profiles to a
given query profile.

It uses the fast-mlst dependency to biuld an index based on the profiles from a
more rapid calculation.
"""


import pandas as pd
import os
import subprocess
import random
import string


class DistanceCalculator:

    def __init__(self):
        self.profiles = []
        self.headers = []

    # Loads the profiles file
    def load_profiles_file(self, profiles_path):
        df_data = pd.read_csv(profiles_path, sep="\t")
        df_data = df_data.rename(columns={'FILE': 'ID'})
        df_data.set_index('ID', inplace=True)
        self.profiles = df_data
        self.headers = df_data.index.values

    # Creates the index based on a file with profiles of same size
    @staticmethod
    def update_index(profiles_path, output_dir):
        myinput = open(profiles_path)

        file_name = ''.join(
            random.choice(string.ascii_uppercase + string.digits) for _ in
            range(8))

        index_path = os.path.join(output_dir, file_name)

        command = '../dependencies/fast-mlst/src/main -i ' + index_path + \
                  ' -b';
        command = command.split(' ')
        print(command)

        proc = subprocess.Popen(
            command, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, stdin=myinput)

        stdout, stderr = proc.communicate()

        print(stdout.decode("utf-8"))
        print(stderr.decode("utf-8"))

        return index_path

    # Get the closest profiles to a given profile
    @staticmethod
    def get_closest_profiles(index, profile_string, index_path, max_closest):

        file = open(index_path + ".txt", 'wb')
        file.write((index + "\t" + profile_string).encode())
        file.close()

        file = open(index_path + ".txt", 'r')

        command = '../dependencies/fast-mlst/src/main -i ' + index_path + \
                  ' -q ' + str(max_closest)

        command = command.split(' ')
        #print(command)

        proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, stdin=file)

        stdout, stderr = proc.communicate()

        entries = stdout.decode("utf-8").split("\n")
        del entries[-1]

        return entries

