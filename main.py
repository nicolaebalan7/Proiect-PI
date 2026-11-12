import cv2
import numpy as np


# incarcam imaginea in format png/jpg
def incarca_imagine(image_path):
    img = cv2.imread(image_path)

    if img is None:
        print("Image Not Found")
        exit()

    return img


# conversie in grayscale si reducerea zgomotului
def preprocesare_blur(img):
    img_blur = cv2.GaussianBlur(img, (7, 7), 0)
    return img_blur

def preprocesare_gray(img):
    gri = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gri

# ordonarea colturilor, pentru a ajuta in procesul de corectie geometrica
def ordoneaza_puncte(pct):
    rect = np.zeros((4, 2), dtype="float32")

    # succesiunea in matrice este de stanga-sus, dreapta-sus, dreapta-jos, stanga-jos
    suma = pct.sum(axis=1)  # axis=1 pentru a face suma pe linie
    rect[0] = pct[np.argmin(suma)]  # punem stanga sus cea mai mica suma dintre x si y
    rect[2] = pct[np.argmax(suma)]  # punem dreapta jos cea mai mare suma dintre x si y
    diff = np.diff(pct, axis=1)
    rect[1] = pct[np.argmin(diff)]  # punem dreapta sus cea mai mica diferenta dintre y si x
    rect[3] = pct[np.argmax(diff)]  # punem stanga jos cea mai mare diferenta dintre y si x

    return rect


def corectie_geometrica(img):
    # Pasul 1: Gasim FOAIA lucrand pe o copie micsorata cu raportul de aspect pastrat
    h, w = img.shape[:2]
    sc = 800 / max(h, w)
    mic = cv2.resize(img, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    mic = preprocesare_blur(mic)

    # Calculam scorul de hartie (foaia e luminoasa si are B > R fata de lemn/parchet)
    b, g, r = [c.astype(np.float32) for c in cv2.split(mic)]
    gri_mic = preprocesare_gray(mic).astype(np.float32)
    scor = np.clip(gri_mic + 3 * (b - r), 0, 255).astype(np.uint8)

    # Binarizare Otsu si operatii morfologice pentru izolarea foii
    _, masca = cv2.threshold(scor, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
    masca = cv2.morphologyEx(masca, cv2.MORPH_CLOSE, k)
    masca = cv2.morphologyEx(masca, cv2.MORPH_OPEN, k)

    contururi, _ = cv2.findContours(masca, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contururi = sorted(contururi, key=cv2.contourArea, reverse=True)[:5]

    pct_foaie = None
    for c in contururi:
        hull = cv2.convexHull(c)
        perimetru = cv2.arcLength(hull, True)
        for eps in (0.02, 0.03, 0.04, 0.05):
            aprox = cv2.approxPolyDP(hull, eps * perimetru, True)
            if len(aprox) == 4:
                pct_foaie = aprox.reshape(4, 2).astype("float32") / sc
                break
        if pct_foaie is not None:
            break

    if pct_foaie is None:
        pct_foaie = cv2.boxPoints(cv2.minAreaRect(contururi[0])).astype("float32") / sc

    # Indreptam foaia la format A4 portret (1240 x 1753)
    rect_foaie = ordoneaza_puncte(pct_foaie)
    (ss, ds, dj, sj) = rect_foaie
    lat = (np.linalg.norm(ds - ss) + np.linalg.norm(dj - sj)) / 2
    inal = (np.linalg.norm(sj - ss) + np.linalg.norm(dj - ds)) / 2
    if lat > inal:
        rect_foaie = np.roll(rect_foaie, -1, axis=0)

    W_foaie = 1240
    H_foaie = int(W_foaie * 297 / 210)
    dst_foaie = np.array([[0, 0], [W_foaie - 1, 0], [W_foaie - 1, H_foaie - 1], [0, H_foaie - 1]], dtype="float32")
    M_foaie = cv2.getPerspectiveTransform(rect_foaie, dst_foaie)
    foaie = cv2.warpPerspective(img, M_foaie, (W_foaie, H_foaie))

    # Pasul 2: Gasim si decupam TABELUL din foaia indreptata (900 x 1300)
    gri_foaie = preprocesare_gray(foaie)
    prag = cv2.adaptiveThreshold(gri_foaie, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 8)
    hf, wf = prag.shape

    oriz = cv2.morphologyEx(prag, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (wf // 25, 1)))
    vert = cv2.morphologyEx(prag, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (1, hf // 50)))
    grila_tabel = cv2.dilate(cv2.add(oriz, vert), cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9)))

    contururi_tabel, _ = cv2.findContours(grila_tabel, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c_tabel = max(contururi_tabel, key=cv2.contourArea)
    pct_tabel = cv2.convexHull(c_tabel).reshape(-1, 2).astype("float32")
    rect_tabel = ordoneaza_puncte(pct_tabel)

    latime, inalt = 900, 1300
    dst_tabel = np.array([[0, 0], [latime - 1, 0], [latime - 1, inalt - 1], [0, inalt - 1]], dtype="float32")
    M_tabel = cv2.getPerspectiveTransform(rect_tabel, dst_tabel)

    # Returnam tabelul decupat si indreptat
    return cv2.warpPerspective(foaie, M_tabel, (latime, inalt))


def detectare_grila(imagine_transformata):
    grayscale = preprocesare_gray(imagine_transformata)

    # binarizare adaptiva (inversata: liniile devin albe pe fundal negru)
    prag = cv2.adaptiveThreshold(grayscale, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 6)
    h, w = prag.shape

    kernel_oriz = cv2.getStructuringElement(cv2.MORPH_RECT, (w // 6, 1))
    orizontal = cv2.morphologyEx(prag, cv2.MORPH_OPEN, kernel_oriz)

    kernel_vert = cv2.getStructuringElement(cv2.MORPH_RECT, (1, h // 10))
    vert = cv2.morphologyEx(prag, cv2.MORPH_OPEN, kernel_vert)

    grid = cv2.add(orizontal, vert)
    return grid


# Functie ajutatoare pentru gasirea varfurilor liniilor din grila
def pozitii_linii(profil, min_dist, prag_rel):
    p = np.convolve(profil, np.ones(3) / 3, mode="same")
    t = prag_rel * p.max()
    poz = []
    for i in range(1, len(p) - 1):
        if p[i] >= t and p[i] >= p[i - 1] and p[i] >= p[i + 1]:
            if poz and i - poz[-1] < min_dist:
                if p[i] > p[poz[-1]]:
                    poz[-1] = i
            else:
                poz.append(i)
    return poz


def extrage_celule(grid):
    h, w = grid.shape

    # separam liniile orizontale si verticale din grid pentru a le calcula profilul
    oriz = cv2.morphologyEx(grid, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (w // 6, 1)))
    vert = cv2.morphologyEx(grid, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (1, h // 10)))

    ly = pozitii_linii(oriz.sum(axis=1).astype(float), h // 70, 0.2)
    lx = pozitii_linii(vert.sum(axis=0).astype(float), w // 20, 0.2)

    # completam eventualele linii orizontale lipsa
    pas = np.median(np.diff(ly[1:])) if len(ly) > 3 else h / 21
    ly_complet = [ly[0]]
    for i in range(1, len(ly)):
        gap = ly[i] - ly[i - 1]
        n = int(round(gap / pas))
        if i > 1 and n > 1:
            ly_complet += [int(ly[i - 1] + gap * k / n) for k in range(1, n)]
        ly_complet.append(ly[i])

    # salvam celulele in formatul [x, y, w, h] ca in codul initial
    celule = []
    for r in range(len(ly_complet) - 1):
        for c in range(len(lx) - 1):
            x = lx[c]
            y = ly_complet[r]
            latime_celula = lx[c + 1] - lx[c]
            inaltime_celula = ly_complet[r + 1] - ly_complet[r]
            celule.append([x, y, latime_celula, inaltime_celula])

    return celule


def suprapunere_celule(imagine_transformata, celule):
    img_cu_celule = imagine_transformata.copy()
    for (x, y, w, h) in celule:
        cv2.rectangle(img_cu_celule, (x + 2, y + 2), (x + w - 2, y + h - 2), (0, 255, 0), 2)

    return img_cu_celule


def calculeaza_acuratete_celule(celule):
    if not celule:
        return 0.0

    # extragem latimile si inaltimile tuturor celulelor detectate
    latimi = [w for (x, y, w, h) in celule]
    inaltimi = [h for (x, y, w, h) in celule]

    # calculam deviatia standard a inaltimilor randurilor
    # daca avem deviatia mica inseamna ca avem o acuratete mare
    medie_inaltime = np.mean(inaltimi)
    deviatie_std = np.std(inaltimi)

    # facem un scor estimativ
    coeficient_variatie = deviatie_std / medie_inaltime if medie_inaltime > 0 else 1

    scor_acuratete = max(0, min(100, (1 - coeficient_variatie) * 100))

    # verificam daca am detectat numarul asteptat de randuri
    numar_celule_gasite = len(celule)

    print(f"-> Numar total de celule detectate: {numar_celule_gasite}")
    print(f"-> Scorul de uniformitate a grilei: {scor_acuratete:.2f}%")

    return scor_acuratete


# functie mica pentru afisare la dimensiune potrivita pe ecran
def afiseaza_fereastra(titlu, img):
    sc = 800 / max(img.shape[:2])
    redim = cv2.resize(img, None, fx=sc, fy=sc) if sc < 1 else img
    cv2.imshow(titlu, redim)


def main():
    image_paths=["Prezenta-1.png","s1.png","s2.png","s3.png","s4.png","fundal_alb.png"]

    for image in image_paths:

        img = incarca_imagine(image)
        print("imagine incarcata")


        imagine_transformata = corectie_geometrica(img)
        print("corectie_geometrica")

        grid = detectare_grila(imagine_transformata)
        print("detectare grila")

        celule = extrage_celule(grid)
        print("extrage celule")

        print("afisare rezultate")

        afiseaza_fereastra("Imagine initiala", img)
        cv2.waitKey(0)

        afiseaza_fereastra("Imagine corectata", imagine_transformata)
        cv2.waitKey(0)

        afiseaza_fereastra("Imagine grila", grid)
        cv2.waitKey(0)

        img_cu_celule = suprapunere_celule(imagine_transformata, celule)
        afiseaza_fereastra("Imagine cu Celule identificate", img_cu_celule)
        cv2.waitKey(0)

        scor_acuratete = calculeaza_acuratete_celule(celule)
        print(scor_acuratete)
        print()

        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()