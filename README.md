# check_xls_reports
Commands and scripts to check the xls reports in case of validation

```
# Check transcript length
grep ${transcript} exons_nirvana2010_no_PAR_Y_noflank.tsv | sort | awk '{len=len+$3-$2+11} END{print len}'

# Check depths in QC sheet
python check_gene_qc.py X005666_QC.csv X005666.nirvana_203_5bp.gz exons_nirvana2010_no_PAR_Y_noflank.tsv
```