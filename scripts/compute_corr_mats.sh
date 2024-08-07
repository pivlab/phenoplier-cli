# Compute correlation matrices for specified LVs

nohup bash -c "
for i in {1..117}; do
    poetry run python -m phenoplier run gene-corr generate \
    -c phenomexcan_rapid_gwas \
    -r GTEX_V8 \
    -m MASHR \
    -e 0.01 \
    -l \"\$i\"
done >> generate_output.log 2>&1
" &
