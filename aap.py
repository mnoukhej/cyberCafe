from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from io import BytesIO
from zipfile import ZipFile
from PIL import Image, ImageOps, ImageFilter
import numpy as np
import cv2
from rembg import remove
import mediapipe as mp
from fpdf import FPDF

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXT = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.secret_key = 'replace-with-a-secure-secret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def pil_to_cv2(pil_image):
    arr = np.array(pil_image.convert('RGB'))
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

def cv2_to_pil(cv_img):
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(cv_img)

def auto_enhance(pil_img):
    img = pil_img.convert('RGB')
    img = ImageOps.autocontrast(img, cutoff=1)
    img = img.filter(ImageFilter.SHARPEN)
    return img

def detect_face_bbox(pil_img):
    h, w = pil_img.size[1], pil_img.size[0]
    cv_img = pil_to_cv2(pil_img)
    rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    if not results.multi_face_landmarks:
        return None
    lm = results.multi_face_landmarks[0]
    xs = [p.x for p in lm.landmark]
    ys = [p.y for p in lm.landmark]
    min_x = max(int(min(xs) * w) - 20, 0)
    max_x = min(int(max(xs) * w) + 20, w)
    min_y = max(int(min(ys) * h) - 40, 0)
    max_y = min(int(max(ys) * h) + 20, h)
    return (min_x, min_y, max_x, max_y)

def smart_crop_and_resize(pil_img, target_px, dpi=300):
    bbox = detect_face_bbox(pil_img)
    w_t, h_t = target_px
    if bbox:
        min_x, min_y, max_x, max_y = bbox
        box_w = max_x - min_x
        box_h = max_y - min_y
        center_x = min_x + box_w // 2
        center_y = min_y + box_h // 2
        desired_ratio = w_t / h_t
        crop_h = int(box_h * 3)
        crop_w = int(crop_h * desired_ratio)
        if crop_w < box_w:
            crop_w = int(box_w * 1.6)
            crop_h = int(crop_w / desired_ratio)
        left = max(center_x - crop_w // 2, 0)
        top = max(center_y - crop_h // 2, 0)
        right = min(left + crop_w, pil_img.size[0])
        bottom = min(top + crop_h, pil_img.size[1])
        crop = pil_img.crop((left, top, right, bottom))
    else:
        img_w, img_h = pil_img.size
        desired_ratio = w_t / h_t
        if img_w / img_h > desired_ratio:
            new_w = int(img_h * desired_ratio)
            left = (img_w - new_w) // 2
            crop = pil_img.crop((left, 0, left + new_w, img_h))
        else:
            new_h = int(img_w / desired_ratio)
            top = (img_h - new_h) // 2
            crop = pil_img.crop((0, top, img_w, top + new_h))
    resized = crop.resize((w_t, h_t), Image.LANCZOS)
    return resized

def replace_background(pil_img, bg_color_hex):
    with BytesIO() as inp:
        pil_img.save(inp, format='PNG')
        inp.seek(0)
        out_bytes = remove(inp.read())
    fg = Image.open(BytesIO(out_bytes)).convert('RGBA')
    if bg_color_hex.startswith('#'):
        bg_color_hex = bg_color_hex[1:]
    r = int(bg_color_hex[0:2], 16)
    g = int(bg_color_hex[2:4], 16)
    b = int(bg_color_hex[4:6], 16)
    bg = Image.new('RGBA', fg.size, (r, g, b, 255))
    composed = Image.alpha_composite(bg, fg)
    return composed.convert('RGB')

def make_layout(single_img, copies, layout_cols, paper_size_px=(2480,3508), margin=100):
    paper_w, paper_h = paper_size_px
    canvas = Image.new('RGB', (paper_w, paper_h), 'white')
    img_w, img_h = single_img.size
    cols = layout_cols
    rows = (copies + cols - 1) // cols
    spacing_x = (paper_w - 2*margin - cols*img_w) // max(cols-1,1) if cols>1 else 0
    spacing_y = (paper_h - 2*margin - rows*img_h) // max(rows-1,1) if rows>1 else 0
    x = margin
    y = margin
    placed = 0
    for r in range(rows):
        for c in range(cols):
            if placed >= copies:
                break
            canvas.paste(single_img, (x, y))
            x += img_w + spacing_x
            placed += 1
        x = margin
        y += img_h + spacing_y
    return canvas

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'photo' not in request.files:
        flash('No file provided')
        return redirect(url_for('index'))
    file = request.files['photo']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    if not allowed_file(file.filename):
        flash('Invalid file type')
        return redirect(url_for('index'))
    bg_color = request.form.get('bg_color', '#FFFFFF')
    copies_choice = request.form.get('copies', '6')
    copies = int(copies_choice)

    filename = secure_filename(file.filename)
    in_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(in_path)

    pil = Image.open(in_path)
    pil = auto_enhance(pil)
    try:
        rgba = replace_background(pil, bg_color)
    except Exception as e:
        print('rembg failed:', e)
        rgba = pil.convert('RGB')
    passport_px = (413, 531)
    stamp_px = (236, 295)
    passport_img = smart_crop_and_resize(rgba, passport_px)
    stamp_img = smart_crop_and_resize(rgba, stamp_px)

    layout3 = make_layout(passport_img, copies=3, layout_cols=3)
    layout6 = make_layout(passport_img, copies=6, layout_cols=3)

    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'w') as zf:
        buf = BytesIO()
        passport_img.save(buf, format='JPEG', quality=95)
        zf.writestr('passport_single.jpg', buf.getvalue())
        buf = BytesIO()
        stamp_img.save(buf, format='JPEG', quality=95)
        zf.writestr('stamp_single.jpg', buf.getvalue())
        buf = BytesIO()
        layout3.save(buf, format='JPEG', quality=95)
        zf.writestr('layout_3.jpg', buf.getvalue())
        buf = BytesIO()
        layout6.save(buf, format='JPEG', quality=95)
        zf.writestr('layout_6.jpg', buf.getvalue())
        pdf = FPDF(unit='pt', format=[2480,3508])
        pdf.add_page()
        tmp = BytesIO()
        layout6.save(tmp, format='JPEG', quality=95)
        tmp.seek(0)
        pdf.image(tmp, 0, 0, 2480, 3508)
        zf.writestr('a4_layout6.pdf', pdf.output(dest='S').encode('latin1'))

    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='processed_photos.zip')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
