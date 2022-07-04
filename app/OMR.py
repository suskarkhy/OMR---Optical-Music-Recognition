from glob import glob
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from midiutil import MIDIFile


class OMR:
    def __init__(self, upload_path, output_path):
        self.upload_path = upload_path
        self.output_path = output_path
        
        self.pitch_to_midi = {
            "C8": 108,
            "B7": 107,
            "Bb7": 106,
            "A#7": 106,
            "A7": 105,
            "Ab7": 104,
            "G#7": 104,
            "G7": 103,
            "Gb7": 102,
            "F#7": 102,
            "F7": 101,
            "E7": 100,
            "Eb7": 99,
            "D#7": 99,
            "D7": 98,
            "Db7": 97,
            "C#7": 97,
            "C7": 96,
            "B6": 95,
            "Bb6": 94,
            "A#6": 94,
            "A6": 93,
            "Ab6": 92,
            "G#6": 92,
            "G6": 91,
            "Gb6": 90,
            "F#6": 90,
            "F6": 89,
            "E6": 88,
            "Eb6": 87,
            "D#6": 87,
            "D6": 86,
            "Db6": 85,
            "C#6": 85,
            "C6": 84,
            "B5": 83,
            "Bb5": 82,
            "A#5": 82,
            "A5": 81,
            "Ab5": 80,
            "G#5": 80,
            "G5": 79,
            "Gb5": 78,
            "F#5": 78,
            "F5": 77,
            "E5": 76,
            "Eb5": 75,
            "D#5": 75,
            "D5": 74,
            "Db5": 73,
            "C#5": 73,
            "C5": 72,
            "B4": 71,
            "Bb4": 70,
            "A#4": 70,
            "A4": 69,
            "Ab4": 68,
            "G#4": 68,
            "G4": 67,
            "Gb4": 66,
            "F#4": 66,
            "F4": 65,
            "E4": 64,
            "Eb4": 63,
            "D#4": 63,
            "D4": 62,
            "Db4": 61,
            "C#4": 61,
            "C4": 60,
            "B3": 59,
            "Bb3": 58,
            "A#3": 58,
            "A3": 57,
            "Ab3": 56,
            "G#3": 56,
            "G3": 55,
            "Gb3": 54,
            "F#3": 54,
            "F3": 53,
            "E3": 52,
            "Eb3": 51,
            "D#3": 51,
            "D3": 50,
            "Db3": 49,
            "C#3": 49,
            "C3": 48,
            "B2": 47,
            "Bb2": 46,
            "A#2": 46,
            "A2": 45,
            "Ab2": 44,
            "G#2": 44,
            "G2": 43,
            "Gb2": 42,
            "F#2": 42,
            "F2": 41,
            "E2": 40,
            "Eb2": 39,
            "D#2": 39,
            "D2": 38,
            "Db2": 37,
            "C#2": 37,
            "C2": 36,
            "B1": 35,
            "Bb1": 34,
            "A#1": 34,
            "A1": 33,
            "Ab1": 32,
            "G#1": 32,
            "G1": 31,
            "Gb1": 30,
            "F#1": 30,
            "F1": 29,
            "E1": 28,
            "Eb1": 27,
            "D#1": 27,
            "D1": 26,
            "Db1": 25,
            "C#1": 25,
            "C1": 24,
            "B0": 23,
            "Bb0": 22,
            "A#0": 22,
            "A0": 21
        }
        
        self.rhythm_to_midi = {"whole_note":4, "half_note":2, "quarter_note":1, "eighth_note":0.5, "sixteenth_note": 0.25}
        
        self.clef_table = {"bass_clef":["A3", "G3", "F3", "E3", "D3", "C3", "B2", "A2", "G2"],
              "c_clef":["G4", "F4", "E4", "D4", "C4", "B3", "A3", "G3", "F3"],
              "g_clef":["F5", "E5", "D5", "C5", "B4", "A4", "G4", "F4", "E4"]}
        
        self.time_signatures = {"common_time":{"imfiles":["common_time_0.png", "common_time_1.png", "common_time_2.png", "common_time_3.png"]},
                                "3/4":{"imfiles":["time_sig_34.png"]}, 
                                "4/4":{"imfiles":["time_sig_44.png"]},
                                "6/8":{"imfiles":["time_sig_68.png"]},
                                "2/4":{"imfiles":["time_sig_24.png"]},
                                "6/4":{"imfiles":["time_sig_64.png"]},
                                "cut_time":{"imfiles":["time_sig_cut_time.png"]}}
        
        for time_sig in self.time_signatures:
            self.time_signatures[time_sig]["imgs"] = [cv2.imread(os.path.join("my_templates", imfile), cv2.IMREAD_GRAYSCALE) for imfile in self.time_signatures[time_sig]["imfiles"]]
        
        
        clef_list = ["bass_clef", "c_clef", "g_clef"]
        
        self.note_thresholds = {"quarter_note":0.68, "half_note":0.65, "eighth_note":0.6, "whole_note":0.65, "sixteenth_note": 0.68}
        
        self.clef_templates = {c:np.array(Image.open(os.path.join("my_templates",c+".png"))) for c in clef_list}
        self.note_templates = {"quarter_note":
                              {"up":{"imfiles":["quarter_note_up_0.png", "quarter_note_up_1.png", "quarter_note_up_2.png"]},
                               "down":{"imfiles":["quarter_note_down_0.png", "quarter_note_down_1.png", "quarter_note_down_2.png"] }},
                          "half_note":
                              {"up":{"imfiles":["half_note_up_0.png", "half_note_up_1.png", "half_note_up_2.png"]},
                               "down":{"imfiles":["half_note_down_0.png", "half_note_down_1.png", "half_note_down_2.png"]}},
                          "eighth_note":
                              {"up":{"imfiles":["eighth_note_up_0.png", "eighth_note_up_1.png", "eighth_note_up_2.png"]},
                               "down":{"imfiles":["eighth_note_down_0.png", "eighth_note_down_1.png", "eighth_note_down_2.png"]}},
                         "whole_note":{
                             "none": {"imfiles":["whole_note_0.png", "whole_note_1.png", "whole_note_2.png"]}},
                        "sixteenth_note":
                              {"up":{"imfiles":["sixteenth_note_up_0.png", "sixteenth_note_up_1.png", "sixteenth_note_up_2.png"]},
                               "down":{"imfiles":["sixteenth_note_down_0.png", "sixteenth_note_down_1.png", "sixteenth_note_down_2.png"]}},
                         }
                         
        

        for note in self.note_templates:
            for stem_direction in self.note_templates[note]:
                self.note_templates[note][stem_direction]["imgs"] = [cv2.imread(os.path.join("my_templates",imfile),cv2.IMREAD_GRAYSCALE) for imfile in self.note_templates[note][stem_direction]["imfiles"]]
    
    

    def show(self, img):
        plt.figure(figsize=(20,20))
        plt.imshow(img,"binary")
        plt.show()
    
    def get_staff_lines(self, staff_img):
        contours, _ = cv2.findContours(staff_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        ys = []
        staff_ds = np.ones((9,1))
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            ys.append(y)
        ys = sorted(ys)
        for i, y in enumerate(ys):
            staff_ds[i*2]=y
            if i>0:
                ly = staff_ds[i*2-2]
                staff_ds[i*2-1]=+ ly+(y-ly)//2

        return staff_ds


    def detect_pitch(self, symbol_y, symbol_h, stem_direction, clef):
        note_y = symbol_y + 15
        if stem_direction=="up":
            note_y = symbol_y+15

        if stem_direction=="down":
            note_y = symbol_y+symbol_h-15
        

        si = np.argmin(np.abs(self.staff_ds-note_y))
        return self.clef_table[clef][si]
    
    def run(self, img, imindex):
        cimg = img.copy()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        imfile = f"img_{imindex}.png"
        midifile = f"midi_{imindex}.mid"

        # remove noise
        img = cv2.fastNlMeansDenoising(img, None, 10, 7, 21)


        # binarize
        _, img_thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)


        # get staff lines
        hs = cv2.getStructuringElement(cv2.MORPH_RECT, (img_thresh.shape[1]//2, 1))
        staff = cv2.erode(img_thresh, hs)
        staff = cv2.dilate(staff, hs)

        self.staff_ds = self.get_staff_lines(staff)


        # get symbols
        kv = cv2.getStructuringElement(cv2.MORPH_CROSS,(1,4))
        # kh = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        symbols = cv2.erode(img_thresh, kv)


        CLEF = "g_clef"

        for clef in self.clef_templates:
            clef_img = cv2.bitwise_not(self.clef_templates[clef])
            try:
                matches = cv2.matchTemplate(symbols, clef_img, cv2.TM_CCOEFF_NORMED)
                coords = np.where(matches>=0.5)
                if len(coords[0]):
                    CLEF=clef
                    break
            except:
                continue


        print(CLEF)
        
        time_signature = "None"
        for time_sig in self.time_signatures:
            time_sig_img = cv2.bitwise_not(self.time_signatures[time_sig]["imgs"][0])
            try:
                matches = cv2.matchTemplate(symbols, time_sig_img, cv2.TM_CCOEFF_NORMED)
                coords = np.where(matches>=0.7)
                if len(coords[0]):
                    time_signature=time_sig
                    break
            except:
                continue
        
        print(time_signature)

        all_notes = []

        for note in self.note_templates:
            for stem_direction in self.note_templates[note]:
                for note_img in self.note_templates[note][stem_direction]["imgs"]:
                    note_img = cv2.bitwise_not(note_img)
                    note_h, note_w = note_img.shape[:2]

                    matches = cv2.matchTemplate(symbols, note_img, cv2.TM_CCOEFF_NORMED)
                    coords = sorted(list(zip(*np.where(matches>=self.note_thresholds[note]))), key=lambda x:x[1])
                    if len(coords):
                        for y, x in coords:
                            pitch = self.detect_pitch(y, note_h, stem_direction, CLEF)
                            all_notes.append({"rhythm":note, "pitch": pitch, "xywh":[x,y,note_w, note_h], "stem_direction":stem_direction})

        
        
        all_notes = sorted(all_notes, key=lambda x:x["xywh"][0])
        NOTES = []
        
        if len(all_notes)==0:
            return None
        
        last_x = all_notes[0]["xywh"][0]
        temp_list = []
        for note in all_notes:
            x, y, note_w, hote_h = note["xywh"]
            current_x = x
            distance = abs(current_x - last_x)
            last_x = x
            if distance < note_w*0.8:
                temp_list.append(note)
            else:
#                 print("*"*20)
#                 for i in temp_list:
#                     print(i)
                _note = {"rhythm":{r:0 for r in self.note_templates.keys()}, "pitch": {p:0 for p in self.clef_table[clef]}, "xywh":[]}
                for match in temp_list:
                    _note["rhythm"][match["rhythm"]]+=1
                    _note["pitch"][match["pitch"]]+=1
                    _note["xywh"].append(np.array(match["xywh"]))

                _note["rhythm"]=max(_note["rhythm"], key=lambda x:_note["rhythm"][x])
                _note["pitch"]=max(_note["pitch"], key=lambda x:_note["pitch"][x])
                _note["xywh"]=np.mean(np.array(_note["xywh"]), axis=0).astype(int)
                NOTES.append(_note)
                temp_list = []
                temp_list.append(note)
                x, y, note_w, note_h= _note["xywh"]
                
                cv2.rectangle(cimg, (x,y),(x+note_w, y+note_h), (0,0,255), 4)
                cv2.putText(cimg, f"{_note['rhythm']}-{_note['pitch']}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(255,0,0) , 1, cv2.LINE_AA)


        _note = {"rhythm":{r:0 for r in self.note_templates.keys()}, "pitch": {p:0 for p in self.clef_table[clef]}, "xywh":[]}
        for match in temp_list:
            _note["rhythm"][match["rhythm"]]+=1
            _note["pitch"][match["pitch"]]+=1
            _note["xywh"].append(np.array(match["xywh"]))

        _note["rhythm"]=max(_note["rhythm"], key=lambda x:_note["rhythm"][x])
        _note["pitch"]=max(_note["pitch"], key=lambda x:_note["pitch"][x])
        _note["xywh"]=np.mean(np.array(_note["xywh"]), axis=0).astype(int)
        NOTES.append(_note)
        temp_list = []
        x, y, note_w, note_h= _note["xywh"]

        cv2.rectangle(cimg, (x,y),(x+note_w, y+note_h), (0,0,255), 4)
        cv2.putText(cimg, f"{_note['rhythm']}-{_note['pitch']}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(255,0,0) , 1, cv2.LINE_AA)
                
        cv2.imwrite(os.path.join(self.upload_path, imfile), cimg)

        print("clef", CLEF)
        print("time_signature", time_signature)
        
        for i in NOTES:
            print(i)
            
        time_signature_to_bpm = {"common_time":120}
        

        
        track    = 0
        channel  = 0
        time     = 0    # In beats
        if time_signature in time_signature_to_bpm:
            tempo    = time_signature_to_bpm[time_signature]   # In BPM
        else:
            tempo = 60
        volume   = 100  # 0-127, as per the MIDI standard

        MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                              # automatically)
        MyMIDI.addTempo(track, time, tempo)
        
        

        for note in NOTES:
            duration = self.rhythm_to_midi[note["rhythm"]]
            print(duration)
            pitch = self.pitch_to_midi[note["pitch"]]
            MyMIDI.addNote(track, channel, pitch, time, duration, volume)
            time+=duration
        
        with open(os.path.join(self.output_path, midifile), "wb") as output_file:
            MyMIDI.writeFile(output_file)










    
    