import pymupdf, re
doc = pymupdf.open('/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf')
for pno in range(155, 309):
    page = doc[pno]
    text = page.get_text()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    figs = sorted(set(re.findall(r'Figure\s+(\d+-?\d*)', text)))
    # only figure caption lines (start with Figure)
    figlines = [l for l in lines if re.match(r'^Figure\s+\d+', l)]
    tbllines = [l for l in lines if re.match(r'^Table\s+\d+', l)]
    # chapter heading
    chap = [l for l in lines if re.match(r'^Chapter\s+\d+', l) or re.match(r'^Part\s+[IVX]+', l) or re.match(r'^Appendix\s+[A-Z]', l)]
    n_draw = len(page.get_drawings())
    n_img = len(page.get_images(full=True))
    if figlines or tbllines or chap or n_draw>0:
        print(f"p{pno+1} | draw={n_draw} img={n_img} | CH: {chap[:1]} | FIG: {figlines[:2]} | TBL: {tbllines[:2]}")
