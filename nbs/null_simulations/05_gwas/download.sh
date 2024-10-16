mkdir -p~/nullsim/input/
dx download "project-Gq7G9JQJYYYByQzg1b8XJG8Q:/phenoplier/null_sim/01-output/0-199/" -r -a -o ~/nullsim/input/


# remove unneeded columns
echo "Removing columns and compressing"
removecols() {
   FILE=$1
   OUTDIR=$2
   awk -F'\t' 'BEGIN {OFS = FS} {print $1,$2,$3,$4,$6,$9,$10,$12}' ${FILE} | gzip > ${OUTDIR}/${FILE}.tsv.gz
}
export -f removecols
parallel -j${N_JOBS} removecols {} ::: \
  ${GWAS_DIR}/*.glm.linear