""" check_gene_qc.py

Use the coverage file from nirvana to check if the data in the xls reports in the QC sheets is correct

Example:
python check_gene_qc.py X006692_QC.csv X006692_markdup.nirvana_2010_5bp.gz exons_nirvana2010_no_PAR_Y.tsv
"""

import argparse
from collections import defaultdict
import gzip
import os
import sys


def parse_csv_qc_sheet(csved_qc_sheet):
    transcripts = set()

    with open(csved_qc_sheet) as f:
        for line in f:
            line = line.strip()
            
            if line.startswith("Name"):
                continue
            elif line.startswith("Total"):
                continue
            elif line.startswith(","):
                continue

            line = line.split(",")
            transcripts.add(line[1])

    return transcripts


def parse_exons(reg2transcript_file):
    """ Parse through the exons of nirvana 2.0.3 
    
    Returns dict of dict of dict:
    {
        refseq: {
            "position": {
                chrom: [
                    (start1, end1, exon_nb1),
                    (start2, end2, exon_nb2)
                ]
            }
        }
    }
    """

    exons = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    with open(reg2transcript_file) as f:
        for line in f:
            chrom, start, end, gene_symbol, refseq, exon_nb = line.strip().split()
            exons[refseq]["position"][chrom].append((int(start)+1, int(end), int(exon_nb)))

    return exons


def parse_coverage_file(coverage_file):
    """ Parse coverage file

    """

    cov_data = defaultdict(lambda: defaultdict(list))

    with gzip.open(coverage_file, "rb") as f:
        for line in f:
            line = line.decode().strip("\n")

            if not line.startswith("#"):
                (
                    chrom, start, end,
                    depth_min, depth_mean, depth_max,
                    missing, depth_1to5, depth_6to9, depth_10to19
                ) = line.split("\t")
                cov_data[chrom][(int(start), int(end))] = [
                    depth_min, depth_mean, depth_max,
                    missing, depth_1to5, depth_6to9, depth_10to19
                ]

    return cov_data        


def get_worst_exon(transcript, cov_data, exon_data):
    worst_exon = None

    for chrom, exon_info in exon_data[transcript]["position"].items():
        for data in exon_info:
            exon_start, exon_end, exon_nb = data
            (
                depth_min, depth_mean, depth_max,
                missing, depth_1to5, depth_6to9, depth_10to19
            ) = cov_data[chrom][(exon_start, exon_end)]

            if worst_exon:
                if worst_exon["depth_min"] > int(depth_min):
                    worst_exon = {
                        chrom: (
                            exon_start, exon_end, exon_nb
                        ),
                        "depth_min": int(depth_min)
                    }
            else:
                worst_exon = {
                    chrom: (
                        exon_start, exon_end, exon_nb
                    ),
                    "depth_min": int(depth_min)
                }

    return worst_exon


def get_low_coverage(transcript, cov_data, exon_data):
    cov_missing = 0
    cov_1to5 = 0
    cov_6to9 = 0
    cov_10to19 = 0

    for chrom, exon_info in exon_data[transcript]["position"].items():
        for data in exon_info:
            exon_start, exon_end, exon_nb = data
            (
                depth_min, depth_mean, depth_max,
                missing, depth_1to5, depth_6to9, depth_10to19
            ) = cov_data[chrom][(exon_start, exon_end)]

            if missing:
                cov_missing += get_length_region(missing)

            if depth_1to5:
                cov_1to5 += get_length_region(depth_1to5)
            
            if depth_6to9:
                cov_6to9 += get_length_region(depth_6to9)

            if depth_10to19:
                cov_10to19 += get_length_region(depth_10to19)

    return [cov_missing, cov_1to5, cov_6to9, cov_10to19]


def get_length_region(regions):
    length = 0

    for region in regions.split(","):
        chrom, coor = region.split(":")
        start, end = coor.split("-")
        length += int(end) - int(start) + 1

    return length 


def main(csved_qc_sheet, cov_file, exon_file):
    transcripts = parse_csv_qc_sheet(csved_qc_sheet)
    exon_data = parse_exons(exon_file)
    cov_data = parse_coverage_file(cov_file)

    for transcript in transcripts:
        worst_exon = get_worst_exon(transcript, cov_data, exon_data)
        cov = get_low_coverage(transcript, cov_data, exon_data)

        with open(csved_qc_sheet) as f:
            for line in f:
                line = line.strip()
                
                if transcript in line:
                    line = line.split(",")
                    min_depth = int(float(line[3]))
                    cov_csv = [int(float(value)) for value in line[4:8]]
                    
                    if min_depth == worst_exon["depth_min"] and cov == cov_csv:
                        print("{} is all good".format(transcript))
                    else:
                        print("{} is no good".format(transcript))



if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("csv_sheet", help="CSV QC sheet for xls report")
    parser.add_argument("cov_file", help="Nirvana coverage output")
    parser.add_argument("exon_file", help="Dump of nirvana GFF")
    
    args = parser.parse_args()

    main(args.csv_sheet, args.cov_file, args.exon_file)
