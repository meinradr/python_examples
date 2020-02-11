# https://stackoverflow.com/questions/18897511/how-to-drawimage-a-matplotlib-figure-in-a-reportlab-canvas
# http://www.blog.pythonlibrary.org/2010/03/08/a-simple-step-by-step-reportlab-tutorial/
# https://www.reportlab.com/docs/reportlab-userguide.pdf
# https://stackoverflow.com/questions/8827871/a-multilineparagraph-footer-and-header-in-reportlab
# https://www.pkimber.net/howto/python/modules/reportlab/header-footer.html


import matplotlib.pyplot as plt
from svglib.svglib import svg2rlg
from reportlab.lib import pagesizes
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import units, utils
from PIL import Image as PIL_Image
from io import BytesIO


def scale_image(file, target_width=None, target_height=None, dpi=300, hAlign='CENTER'):

    img = PIL_Image.open(file)
    size_px = img.size

    aspect_ratio = size_px[0]/size_px[1]

    if target_height and not target_width:
        target_width = target_height * aspect_ratio
    elif not target_height and target_width:
        target_height = target_width / aspect_ratio
    elif not target_height and not target_width:
        raise AttributeError("'target_width' or 'target_height' must be specified")

    size_inch = (target_width / units.inch, target_height / units.inch)

    print(size_px)
    print(size_inch)
    print(dpi)

    size_px_new = (int(min(size_inch[0] * dpi, size_px[0])), int(min(size_inch[1] * dpi, size_px[1])))

    print(size_px_new)

    if not size_px == size_px_new :
        img = img.resize(size_px_new)

    print(img.size)

    img_data = BytesIO()
    img.save(img_data, format='JPEG')
    img_data.seek(0)

    return Image(img_data, width=target_width, height=target_height, hAlign=hAlign)


picture = 'pc-24.jpg'


fig = plt.figure(figsize=(4, 3))
plt.plot([1,2,3,4])
plt.ylabel('some numbers')

imgdata = BytesIO()
fig.savefig(imgdata, format='svg')
imgdata.seek(0)  # rewind the data

drawing = svg2rlg(imgdata)

doc = SimpleDocTemplate("form_letter.pdf", pagesize=pagesizes.A4,
                        rightMargin=25 * units.mm,
                        leftMargin=25 * units.mm,
                        topMargin=15 * units.mm,
                        bottomMargin=10 * units.mm)


Story = []
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name='Footer',
    parent=styles['Normal'],
    fontSize=8,
    leading=8))

Story.append(Paragraph('Heading1', styles["Heading1"]))
Story.append(Image(drawing, 100 * units.mm, 100 * units.mm))
Story.append(scale_image(picture, target_width=200 * units.mm, dpi=300))
Story.append(Spacer(1, 12))
Story.append(Paragraph('Heading1', styles["Heading1"]))
Story.append(Paragraph('Heading2', styles["Heading2"]))
Story.append(Paragraph('Heading3', styles["Heading3"]))
Story.append(Paragraph('Heading4', styles["Heading4"]))
Story.append(Paragraph('Normal', styles["Normal"]))
Story.append(Paragraph('Normal', styles["Normal"]))
Story.append(Spacer(1, 12))
Story.append(Paragraph('Normal', styles["Normal"]))

for i in range(100):
    Story.append(Paragraph(str(i), styles["Normal"]))


def footer(canvas, doc):
    canvas.saveState()
    #canvas.drawString(doc.leftMargin, doc.bottomMargin - 5, "Welcome to Reportlab!")
    P = Paragraph("This is a footer.  " * 5, styles["Footer"])
    w, h = P.wrap(doc.width, doc.bottomMargin)
    P.drawOn(canvas, doc.leftMargin, h + 15)

    P = Paragraph(f'{doc.page}', styles["Footer"])
    w, h = P.wrap(doc.width, doc.bottomMargin)
    P.drawOn(canvas, doc.leftMargin + doc.width, h + 15)
    canvas.restoreState()


doc.build(Story, onFirstPage=footer, onLaterPages=footer)

