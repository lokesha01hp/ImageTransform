from flask import Flask,render_template, request ,flash
from werkzeug.utils import secure_filename
from flask import send_from_directory
import os
import cv2

UPLOAD_FOLDER = 'uploadfiles'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif','webp'}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template('index.html')

@app.route("/howtouse")
def howtouse():
    return render_template("howtouse.html")

@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")

@app.route("/Contactus")
def contactus():
    return render_template("contactus.html")



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def processImage(filename, operation):
    print(f"The operation is {operation} and filename is {filename}")
    img = cv2.imread(f"uploadfiles/{filename}")

    name, ext = os.path.splitext(filename)

    if img is None:
        print("Image not loaded correctly.")
        return None

    if operation == "cgray":
        imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        new_ext = ".jpg"  # jpg for grayscale for max compatibility
        newfilename = f"{name}{new_ext}"
        newfilepath = f"static/{newfilename}"
        cv2.imwrite(newfilepath, imgProcessed)
        return newfilename

    elif operation == "cwebp":
        new_ext = ".webp"
        newfilename = f"{name}{new_ext}"
        newfilepath = f"static/{newfilename}"
        cv2.imwrite(newfilepath, img)
        return newfilename

    elif operation == "cpng":
        new_ext = ".png"
        newfilename = f"{name}{new_ext}"
        newfilepath = f"static/{newfilename}"
        cv2.imwrite(newfilepath, img)
        return newfilename

    elif operation == "cjpg":
        new_ext = ".jpg"
        newfilename = f"{name}{new_ext}"
        newfilepath = f"static/{newfilename}"
        cv2.imwrite(newfilepath, img)
        return newfilename

    elif operation == "cpdf":
        new_ext = ".pdf"
        newfilename = f"{name}{new_ext}"
        newfilepath = f"static/{newfilename}"
        # cv2.imwrite does not support PDF directly, so need to handle this separately
        # For now, save as PNG first then convert using PIL if needed
        temp_png = f"static/{name}_temp.png"
        cv2.imwrite(temp_png, img)
        from PIL import Image
        image = Image.open(temp_png)
        image.save(newfilepath, "PDF", resolution=100.0)
        os.remove(temp_png)
        return newfilename

    elif operation == "cgif":
        new_ext = ".gif"
        newfilename = f"{name}{new_ext}"
        newfilepath = f"static/{newfilename}"
        # cv2.imwrite does not support GIF directly, so use PIL
        from PIL import Image
        image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        image.save(newfilepath, "GIF")
        return newfilename

    else:
        print("Invalid operation provided.")
        return None


@app.route("/edit", methods=["GET","POST"])
def edit():
    if request.method == 'POST':
        operation = request.form.get("operation")
        if request.method == 'POST':
        # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return "Please Upload File First"
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return "Not Selected a File"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new = processImage(filename, operation)
        if new:
            flash(f"Your image has been processed. Click <a href='/download/{new}'>here</a> to download.")
        else:
            flash("Processing failed due to an invalid operation. Please try again.", "danger")


            return render_template('index.html')
    
    return render_template('index.html')


@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(directory='static', path=filename, as_attachment=True)


app.run(debug=True,port=999)