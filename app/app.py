from flask import Flask, render_template, request, url_for
import cv2
import numpy as np
import os
from OMR import OMR

app = Flask(__name__, static_url_path='/static')







@app.route("/", methods=["GET","POST"])
@app.route("/omr", methods=["GET","POST"])
def omr_page():
    upload_path = os.path.join(app.root_path, "static/upload_files")
    output_path = os.path.join(app.root_path, "static/output_files")
    omr = OMR(upload_path, output_path)
    
    if request.method=="POST":
        uploaded_file = request.files.to_dict()["file"]
        imindex = len(os.listdir(upload_path))
        
        img_url = os.path.join("static/upload_files/", f"img_{imindex}.png")
        uploaded_file.save(os.path.join(app.root_path, img_url))
        
        orimg = cv2.imread(os.path.join(app.root_path, img_url))
        
        
        omr.run(orimg, imindex)
        
        print("*"*100)
        img_url, midi_url = os.path.join("static/upload_files/", f"img_{imindex}.png"), os.path.join("static/output_files/", f"midi_{imindex}.mid") 

        return {"img_url":img_url, "midi_url":midi_url}
    
    img_urls = [os.path.join("static/upload_files/", i) for i in sorted(os.listdir(upload_path), key=lambda x:int(x[:-4].split("_")[-1]), reverse=True)]
    midi_urls = [os.path.join("static/output_files/", i) for i in sorted(os.listdir(output_path), key=lambda x:int(x[:-4].split("_")[-1]), reverse=True)]
    
    return render_template('omr.html', imidis=zip(img_urls, midi_urls))

@app.route("/test_cases", methods=["GET", "POST"])
def test_cases_page():
    test_cases_path = os.path.join(app.root_path, "static/test_cases")
    omr = OMR(os.path.join(test_cases_path, "output_images"), os.path.join(test_cases_path, "output_midis"))
    imfiles = os.listdir(os.path.join(test_cases_path, "images"))
    output_midis = os.listdir(os.path.join(test_cases_path, "output_midis"))
    for imfile in imfiles:
        imindex = imfile.split(".")[0].split("_")[-1]
        midifile = f"midi_{imindex}.mid"
        if midifile in output_midis:
            continue
        
        orimg = cv2.imread(os.path.join(test_cases_path, "images", imfile))
        
        omr.run(orimg, imindex)
        
        
    output_midis = os.listdir(os.path.join(test_cases_path, "output_midis"))
    # img_urls = [os.path.join("static/test_cases/images/", i) for i in sorted(imfiles, key=lambda x:int(x[:-4].split("_")[-1]), reverse=True)]
    midi_urls = [os.path.join("static/test_cases/midi", i) for i in sorted(output_midis, key=lambda x:int(x[:-4].split("_")[-1]), reverse=True)][:50]
    output_img_urls = [os.path.join("static/test_cases/output_images/", f"img_{i[:-4].split('_')[-1]}.png") for i in sorted(output_midis, key=lambda x:int(x[:-4].split("_")[-1]), reverse=True)][:50]
    output_midi_urls = [os.path.join("static/test_cases/output_midis", i) for i in sorted(output_midis, key=lambda x:int(x[:-4].split("_")[-1]), reverse=True)][:50]
    return render_template("test_cases.html", imidis=zip(midi_urls, output_img_urls, output_midi_urls))

if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
    