#!/usr/bin/env python3
import os
import time

objset_dir = "/proc/spl/kstat/zfs/lxd"
sleep_interval = 1


def get_dataset_name(objset_id):
    objset_file = "{}/{}".format(objset_dir, objset_id)

    with open(objset_file, 'r') as f:
        content = f.readlines()

    dataset_name = content[2].strip().split("/")[2]
    return dataset_name


def get_dataset_writes(objset_id):
    objset_file = "{}/{}".format(objset_dir, objset_id)

    with open(objset_file, 'r') as f:
        content = f.readlines()

    dataset_writes = int(content[3].split()[2])
    return dataset_writes


def get_dataset_nwrites(objset_id):
    objset_file = "{}/{}".format(objset_dir, objset_id)

    with open(objset_file, 'r') as f:
        content = f.readlines()

    dataset_nwrites = float(content[4].split()[2])
    return dataset_nwrites


def get_dataset_reads(objset_id):
    objset_file = "{}/{}".format(objset_dir, objset_id)

    with open(objset_file, 'r') as f:
        content = f.readlines()

    dataset_reads = int(content[5].split()[2])
    return dataset_reads


def get_dataset_nread(objset_id):
    objset_file = "{}/{}".format(objset_dir, objset_id)

    with open(objset_file, 'r') as f:
        content = f.readlines()

    dataset_nread = float(content[6].split()[2])
    return dataset_nread


def main():
    # List of objset
    # Example: ['objset-0x1026', 'objset-0x1041', 'objset-0x10424']
    objset_list = []

    # Extended results for each object
    objset_results = {}

    # Final formatted results
    final_results = {}

    # Loop through the objset_dir dir and append the objset to the list
    for objset_id in os.listdir(objset_dir):
        if objset_id.startswith("objset-"):
            objset_list.append(objset_id)
            objset_results[objset_id] = {}

    # Run two tests with a time sleep interval
    for test_id in range(0, 2):
        for objset_id in objset_list:

            # Gather the values in two intervals from the objset files
            objset_results[objset_id]["dataset_name"] = get_dataset_name(objset_id)
            objset_results[objset_id]["writes_iops_{}".format(test_id)] = get_dataset_writes(objset_id)
            objset_results[objset_id]["writes_bandwidth_{}".format(test_id)] = get_dataset_nwrites(objset_id)
            objset_results[objset_id]["reads_iops_{}".format(test_id)] = get_dataset_reads(objset_id)
            objset_results[objset_id]["reads_bandwidth_{}".format(test_id)] = get_dataset_nread(objset_id)

        time.sleep(sleep_interval)

    # Set variables for cumulative total IOPS and bandwidth
    writes_iops_p_second_total = 0
    writes_bandwidth_p_second_total = 0
    reads_iops_p_second_total = 0
    reads_bandwidth_p_second_total = 0

    # Loop through the modules results in objset_results dict and export the required information to final_results dict
    for objset_id in objset_results:
        dataset_name = objset_results[objset_id]['dataset_name']
        writes_iops_0 = objset_results[objset_id]["writes_iops_0"]
        writes_iops_1 = objset_results[objset_id]["writes_iops_1"]
        writes_bandwidth_0 = objset_results[objset_id]["writes_bandwidth_0"]
        writes_bandwidth_1 = objset_results[objset_id]["writes_bandwidth_1"]
        writes_iops_p_second = writes_iops_1 - writes_iops_0
        writes_bandwidth_p_second = round(float((writes_bandwidth_1 - writes_bandwidth_0) / 1024 / 1024), 3)
        reads_iops_0 = objset_results[objset_id]["reads_iops_0"]
        reads_iops_1 = objset_results[objset_id]["reads_iops_1"]
        reads_bandwidth_0 = objset_results[objset_id]["reads_bandwidth_0"]
        reads_bandwidth_1 = objset_results[objset_id]["reads_bandwidth_1"]
        reads_iops_p_second = reads_iops_1 - reads_iops_0
        reads_bandwidth_p_second = round(float((reads_bandwidth_1 - reads_bandwidth_0) / 1024 / 1024), 3)

        final_results[objset_id] = {}
        final_results[objset_id] = {
            "dataset_name": dataset_name,
            "writes_iops_p_second": writes_iops_p_second,
            "writes_bandwidth_p_second": writes_bandwidth_p_second,
            "reads_iops_p_second": reads_iops_p_second,
            "reads_bandwidth_p_second": reads_bandwidth_p_second
        }

        # Calculate cumulative total IOPS and bandwidth
        writes_iops_p_second_total += writes_iops_p_second
        writes_bandwidth_p_second_total += writes_bandwidth_p_second
        reads_iops_p_second_total += reads_iops_p_second
        reads_bandwidth_p_second_total += reads_bandwidth_p_second

    # A little bit formatting
    writes_bandwidth_p_second_total = round(writes_bandwidth_p_second_total, 3)
    reads_bandwidth_p_second_total = round(reads_bandwidth_p_second_total, 3)

    # Sort the keys in final_results dict to sort the output
    sorted_keys = sorted(objset_results, key=lambda x: (final_results[x]['writes_iops_p_second']), reverse=True)

    # Print the headers
    print("\n"
          "-----------------------------------------------------------------------------------------------------------"
          )
    print('{:<33s}{:<20}{:<20s}{:<20s}{:<20s}'.format(
            "",
            str("TotalWriteOps/s"),
            str("TotalWritesMB/s"),
            str("TotalReadsOps/s"),
            str("TotalReadsMB/s")
            ))

    print('{:<33s}{:<20s}{:<20s}{:<20s}{:<20s}\n'.format(
            "",
            str(writes_iops_p_second_total),
            str(writes_bandwidth_p_second_total),
            str(reads_iops_p_second_total),
            str(reads_bandwidth_p_second_total)
            ))

    print('{:<33s}{:<20s}{:<20s}{:<20s}{:<20s}'.format(
            "DatasetName",
            str("WriteOps/s"),
            str("WritesMB/s"),
            str("ReadOps/s"),
            str("ReadsMB/s")
            ))

    print("-----------------------------------------------------------------------------------------------------------")

    # Loop through the sorted keys and print the results to the user
    for objset_id in sorted_keys:
        dataset_name = final_results[objset_id]['dataset_name']
        writes_iops_p_second = final_results[objset_id]['writes_iops_p_second']
        writes_bandwidth_p_second = final_results[objset_id]['writes_bandwidth_p_second']
        reads_iops_p_second = final_results[objset_id]['reads_iops_p_second']
        reads_bandwidth_p_second = final_results[objset_id]['reads_bandwidth_p_second']

        if writes_iops_p_second > 0 or writes_bandwidth_p_second > 0:
            print('{:<33s}{:<20s}{:<20s}{:<20s}{:<20s}'.format(
                dataset_name,
                str(writes_iops_p_second),
                str(writes_bandwidth_p_second),
                str(reads_iops_p_second),
                str(reads_bandwidth_p_second)
                )
            )


if __name__ == "__main__":
    while True:
        main()
