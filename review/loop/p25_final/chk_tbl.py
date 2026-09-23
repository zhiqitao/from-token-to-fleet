import pymupdf
pdf='/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf'
d=pymupdf.open(pdf)
# find pages containing 'Table 10-1' and the fig10.1 embedded table markers
for i in range(0,155):
    t=d[i].get_text()
    if "Table 10-1" in t:
        print("Table 10-1 on page", i+1, "book", i-21)
for i in range(0,155):
    t=d[i].get_text()
    if "Fits when" in t:
        print("'Fits when' on page", i+1, "book", i-21)
    if ("Replicated" in t and "all-reduce" in t and "PARTITIONED" not in t and "What splits" in t):
        print("page133-table on page", i+1, "book", i-21)
