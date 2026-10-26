import cv2
import numpy as np


#incarcam imaginea in format png
def incarca_imagine(image_path):
    img=cv2.imread(image_path)

    if img is None:
        print("Image Not Found")
        exit()

    redimensionat=cv2.resize(img,(800,900))
    return redimensionat


#conversie in grayscale si reducerea zgomotului
def preprocesare_initiala(img):
    gri=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    blurat=cv2.GaussianBlur(gri,(5,5),0)
    return gri,blurat

#ordonarea colturilor, pentru a ajuta in procesul de corectie geometrica
def ordoneaza_puncte(pct):
    rect=np.zeros((4,2),dtype="float32")

    #succesiunea in matrice este de stanga-sus,dreapta-sus,dreapta-jos,stanga-jos

    suma=pct.sum(axis=1)#axis=1 pentru a face suma pe linie
    rect[0]=pct[np.argmin(suma)]#punem stanga sus cea mai mica suma dintre x si y
    rect[2]=pct[np.argmax(suma)]#punem dreapta jos cea mai mare suma dintre x si y
    diff=np.diff(pct,axis=1)
    rect[1]=pct[np.argmin(diff)]#punem dreapta sus cea mai mica diferenta dintre y si x
    rect[3]=pct[np.argmax(diff)]#punem stanga jos cea mai mare diferenta dintre y si x

    return rect

def corectie_geometrica(img,blurat):
    marginit=cv2.Canny(blurat,75,200)
    #schimbarile (diferentele) dintre pixeli care sunt alaturati si sunt sub 75
    #sunt considereate zgomot de fundal, iar schimbarile de peste 200 sunt considerate
    #margini puternic pronuntate, deci vor fi pastrate in imagine

    contururi,_=cv2.findContours(marginit,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    #retr_list extrage contururile fara a le ierarhiza
    #cu chain_aprox aproximam punctele extreme, care vor ramane pentru contururi

    contururi = sorted(contururi, key=cv2.contourArea, reverse=True)[:5]
    #sortam lista de contururi rezultate, in mod descrescator
    #sortarea se face dupa suprafata conturului

    screen_cnt=None
    for c in contururi:
        perimetru=cv2.arcLength(c,True)
        #calculare perimetru

        aprox=cv2.approxPolyDP(c,0.02*perimetru,True)
        if len(aprox)==4:
            screen_cnt=aprox
            break

    if screen_cnt is None:
        return img #returnam imaginea originala daca nu gasim patrulatere

    #odronare puncte si transformare perspectiva
    pct=screen_cnt.reshape(4,2)
    rect=ordoneaza_puncte(pct)
    (ss,ds,dj,sj)=rect

    latime=max(int(np.linalg.norm(ds-ss)),int(np.linalg.norm(dj-sj)))
    inalt=max(int(np.linalg.norm(ds-dj)),int(np.linalg.norm(ss-sj)))
    #calculam latimea si inaltimea finala a imaginii

    dst = np.array([[0, 0], [latime- 1, 0], [latime - 1, inalt - 1], [0, inalt - 1]], dtype="float32")

    M=cv2.getPerspectiveTransform(rect,dst)
    #M= matricea de transf geometrica
    return cv2.warpPerspective(img,M,(latime,inalt))
    #aplicam matricea de transf geometrica



def detectare_grila(imagine_transformata):
    grayscale= cv2.cvtColor(imagine_transformata, cv2.COLOR_BGR2GRAY)

    #binarizare adaptiva
    prag=cv2.adaptiveThreshold(grayscale,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)

    kernel_oriz=cv2.getStructuringElement(cv2.MORPH_RECT, (23, 1))
    orizontal=cv2.morphologyEx(prag, cv2.MORPH_OPEN,kernel_oriz)

    kernel_vert = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 23))
    vert = cv2.morphologyEx(prag, cv2.MORPH_OPEN, kernel_vert)

    grid=cv2.add(orizontal,vert)
    return grid

def extrage_celule(grid):
    contururi,_=cv2.findContours(grid,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

    celule = []
    for c in contururi:
        aria=cv2.contourArea(c)
        if 500<aria<10000:
            x,y,w,h=cv2.boundingRect(c)
            celule.append([x,y,w,h])

    return celule




def main():
    image_path = "Prezenta-1.png"
    img=incarca_imagine(image_path)
    print("imagine incarcata")

    gri, blurat = preprocesare_initiala(img)
    print("preprocesare initiala")

    imagine_transformata=corectie_geometrica(img,blurat)
    print("corectie_geometrica")

    grid=detectare_grila(imagine_transformata)
    print("detectare grila")

    celule=extrage_celule(grid)
    print("extrage celule")


    print("afisare rezultate")

    cv2.imshow("Imagine initiala", img)
    cv2.waitKey(0)

    cv2.imshow("Imagine corectata",imagine_transformata)
    cv2.waitKey(0)

    cv2.imshow("Imagine grila", grid)
    cv2.waitKey(0)

    img_cu_celule = imagine_transformata.copy()
    for (x, y, w, h) in celule:
        cv2.rectangle(img_cu_celule, (x, y), (x + w, y + h), (0, 255, 0), 1)

    cv2.imshow("Imagine cu Celule Identificate", img_cu_celule)
    cv2.waitKey(0)


    cv2.destroyAllWindows()




if __name__=="__main__":
    main()