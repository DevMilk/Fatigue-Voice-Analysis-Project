#!/usr/bin/env python
# coding: utf-8

# In[27]:

print("Program Açılıyor, Lütfen Bekleyiniz...") 
import numpy as np
import os  
from keras.preprocessing.image import load_img,img_to_array 
from keras.models import load_model  
from tkinter import * 
import tkinter.font 
from tkinter.filedialog import askopenfilename, askdirectory 
import pandas as pd  
 
 
 
MODEL_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)),"Models")
if(not os.path.exists(MODEL_ROOT)):
	print("{} yolu ve modeller mevcut değil, tahminler yapılamayacak".format(MODEL_ROOT) )
FONT = "Verdana"


class FVA:

    def __init__(self ): 
        self.ModelDict = {"":""}                      

 

    def importModel(self,Dest ):
        model = load_model(Dest)
        print("Model loaded")
        return model

    def nameToFolder(self,modelName):
        specType, voiceType =modelName.split("_")
         
        print("Importing specType: "+specType+" with voiceType: "+voiceType+"...")
        fileName = modelName + ".h5"
        fulldir = os.path.join(MODEL_ROOT, fileName)
        print("Full directory: ",fulldir)
        return fulldir
 

         
    def preProcess(self, specImgDest):
        image = load_img(specImgDest, target_size=( 224, 224 ))
        input_arr = img_to_array(image)/255
        input_arr = np.array([input_arr])  # Convert single image to a batch.

        return input_arr
    def predictClass(self, specImgDest, ModelName="BARK_harf"):
         
        data = self.preProcess(specImgDest)
        prediction = self.ModelDict[ModelName].predict(data)
         
        className = "Dinc" if prediction[0, 0] > prediction[0, 1] else "Yorgun"
         
        return className,prediction[0,0],prediction[0,1]
    def split(self):

        return "                                                                                                       "    

    def startUI(self):

        def set_text(entry, text):
            entry.delete(0, END)
            entry.insert(0, text)
            return None

        def set_label_text(label, text):
            label.config(text=text)
            return None

        def Giris():
            mainGUI = Tk()
            boyut = 500
            mainGUI.geometry("%dx%d" % (boyut, boyut))
            mainGUI.title("Ses Yorgunluk Analizi Aracı ")
            mainGUI.resizable(False, False)

            result = Label(mainGUI, bg="white", fg="Black",
                           font=FONT+ " 13", text="")

            testImageDest = Entry(
                mainGUI, relief=FLAT, bg="white", fg="black",
                font=FONT+" 15 italic", text="")

            harfMi = StringVar(value="harf")
            harf = Radiobutton(mainGUI, text="Harf",
                               variable=harfMi, value="harf")
            kelime = Radiobutton(mainGUI, text="Kelime",
                                 variable=harfMi, value="kelime")
            harf_kelime = Radiobutton(mainGUI, text="Harf ve Kelime",
                                 variable=harfMi, value="harf+kelime")

            specType = StringVar(value="BARK")
            MEL = Radiobutton(mainGUI, text="MEL",
                              variable=specType, value="MEL")
            BARK = Radiobutton(mainGUI, text="BARK",
                               variable=specType, value="BARK")
            ERB = Radiobutton(mainGUI, text="ERB",
                              variable=specType, value="ERB")
            LOG = Radiobutton(mainGUI, text="LOG",
                              variable=specType, value="LOG")

            def load_file():
                fname = askopenfilename(filetypes=(
                    ("Image files", "*.jpg;*.jpeg"), ("Image files", "*.png")))
                set_text(testImageDest, fname)

            def load_dir():
                fname = askdirectory()
                set_text(testImageDest, fname)

            fileDialog = Button(mainGUI, relief=FLAT, bg="white", fg="black",
                font=FONT+" 15 italic", text="Dosya Seç",
                                command=load_file)
            directoryDialog = Button(mainGUI, relief=FLAT, bg="white", fg="black",
                font=FONT+" 15 italic", text="Klasör Seç",
                                command=load_dir)

            def messageTest():

                imgpath = testImageDest.get()
                ModelName = specType.get()+"_"+harfMi.get()
                print("Model used: ",ModelName)


                if(ModelName not in self.ModelDict.keys()): 
                    set_label_text(result,"Model mevcut oturuma yükleniyor...")
                    mainGUI.after(1,set_label_text(result,"Model mevcut oturuma yükleniyor..."))
                    try:
                        self.ModelDict[ModelName] = self.importModel(self.nameToFolder(ModelName)) 
                    except OSError:
                        set_label_text(result, ModelName +".h5 dosyası bulunamadı")    
                        return None
 
                    set_label_text(result,"Model mevcut oturuma yüklendi ")    

                if(not os.path.isdir(imgpath)):
                    

                    className,prob1,prob2 = self.predictClass(imgpath,ModelName) 
                    set_label_text(result, ("Ses tipi {} olarak sınıflandırılmıştır\nYorgun Olma Olasılığı: %{:.2f}\nDinç Olma Olasılığı: %{:.2f}"
                                            .format(className,prob2,prob1)))
                else:
                    sonuclar = {"fileName": [], "className": [],"prob1": [], "prob2": []}
                     
                    for file in os.listdir(imgpath):
                        className,prob1,prob2 = self.predictClass(os.path.join(imgpath,file),ModelName) 
                        sonuclar["fileName"].append(file)
                        sonuclar["className"].append(className)
                        sonuclar["prob1"].append(prob1)
                        sonuclar["prob2"].append(prob2)
                      
                    df = pd.DataFrame(data=sonuclar)    
                    top = Tk()  
                    top.title("Klasör Sınıflandırma Sonuçları")

                    sb = Scrollbar(top)  
                    sb.pack(side = RIGHT, fill = Y)  
                      
                    mylist = Listbox(top, yscrollcommand = sb.set,width=60 )  
                     
                    for i in range(len(df)):
                        mylist.insert(END,"Dosya ismi: "+df["fileName"][i])  
                        mylist.insert(END,"    Sınıf: "+str(df["className"][i]))    
                        mylist.insert(END,"    Dinç Olma İhtimali: "+str(df["prob1"][i]))
                        mylist.insert(END,"    Yorgun Olma İhtimali: "+str(df["prob2"][i]))
                        mylist.insert(END," ")
                    mylist.pack( side = LEFT )  
                    sb.config( command = mylist.yview )


            Test = Button(mainGUI, relief=FLAT, bg="white", fg="black", font=FONT+ " 15 italic", text="Sınıfla",
                          command=messageTest)

            # Pozisyonlar

            radioSet1X, radioSet1Y = 0.45, 0.55
            radioSet2X, radioSet2Y = 0.2, 0.45
            dosyaSecX, dosyaSecY = 0.1, 0.7

            result.place(relx=dosyaSecX, rely=0.2)

            Label(mainGUI, bg="white", fg="Black", font=FONT+" 13", text=self.split()).place(relx=0,rely=radioSet2Y-0.1)

            harf.place(relx=radioSet1X, rely=radioSet1Y + 0.05)
            kelime.place(relx=radioSet1X, rely=radioSet1Y)
            harf_kelime.place(relx=radioSet1X, rely=radioSet1Y - 0.05)

            MEL.place(relx=radioSet2X, rely=radioSet2Y + 0.15)
            BARK.place(relx=radioSet2X, rely=radioSet2Y + 0.1)
            ERB.place(relx=radioSet2X, rely=radioSet2Y + 0.05)
            LOG.place(relx=radioSet2X, rely=radioSet2Y)

            directoryDialog.place(relx=dosyaSecX + 0.55, rely=dosyaSecY + 0.1)    
            fileDialog.place(relx=dosyaSecX + 0.55, rely=dosyaSecY - 0.02)
            testImageDest.place(relx=dosyaSecX, rely=dosyaSecY+0.05)
            Test.place(relx=0.3, rely=0.83)

        Giris()
        mainloop()

if(__name__=="__main__"):
	AI = FVA() 
	AI.startUI()
