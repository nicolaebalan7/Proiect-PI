# Proiect-PI

###Literatura de specialitate consultată
| Nr. | Autor(i) / An | Titlul articolului / proiectului | Aplicație / Domeniu | Tehnologii utilizate | Metodologie / Abordare | Rezultate | Limitări | Comentarii suplimentare |
|---|---|---|---|---|---|---|---|---|
| 1 | Insiya Rizvi, Sayma Shaikh, Dr. Jasbir Kaur, Prof. Ifrah Kampoo, Prof. Sandhya Thakkar / 2026 | [AttendAI: Automated Attendance Detection](https://www.ijert.org/attendai-automated-attendance-detection-ijertv15is060109) | Automatizarea prezenței din foi scanate | OCR/HTR, procesarea imaginilor, potrivirea numelor | Se preprocesează imaginea, se extrage textul și se asociază numele cu lista de studenți. | Prezintă un flux de automatizare a prezenței din documente încărcate. | Poate necesita verificare manuală pentru scris ilizibil sau nume asemănătoare. | Foarte apropiată de tema proiectului; verifică autorii și detaliile bibliografice pe pagina editorului. |
| 2 | DARABATTULA JOSHNA SRI,V.SARALA / 2026 | [Automated Attendance Management System Using OCR and Django Framework](https://ijdim.com/journal/index.php/ijdim/article/view/540) | Digitalizarea registrelor de prezență | OCR, aplicație web, procesare și export de date | Se încarcă imaginea, se extrag informațiile și se gestionează într-o aplicație digitală. | Descrie un sistem pentru prelucrarea și administrarea datelor de prezență. | Nu este axată exclusiv pe recunoașterea scrisului de mână. | Utilă pentru proiectarea fluxului aplicației și organizarea rezultatelor. |
| 3 | José A. P. Lopes, Bernardo Baptista, Nuno Lavado and Mateus Mendes / 2022 | [Offline Handwritten Signature Verification Using Deep Neural Networks](https://www.mdpi.com/1996-1073/15/20/7611) | Analiza semnăturilor din documente | Preprocesarea imaginilor, rețele neuronale | Documentele sunt preprocesate, iar zonele cu semnături sunt analizate automat. | Prezintă metode de analiză a documentelor și a semnăturilor scrise de mână. | Nu recunoaște nume; obiectivul este verificarea semnăturilor. | Etape de preprocesare a foii. |
| 4 | Chenglong Yu , Weibin Li, Wei Li, Zixuan Zhu, Ruochen Liu, Biao Hou,  Licheng Jiao / 2024 | [A Survey for Table Recognition Based on Deep Learning](https://doi.org/10.1016/j.neucom.2024.128154) | Recunoașterea structurii tabelelor din documente | Procesarea imaginilor, metode de deep learning | Analizează metode pentru detectarea tabelelor, structurii celulelor și conținutului. | Compară abordări și metrici folosite la recunoașterea tabelelor. | Se concentrează pe structura tabelelor, nu și pe recunoașterea conținutului scris de mână din celule. | Relevantă pentru separarea rândurilor și coloanelor foii de prezență. |
| 5 | Minghao Li, Tengchao Lv, Jingye Chen, Lei Cui, Yijuan Lu, Dinei Florencio, Cha Zhang, Zhoujun Li, Furu Wei / 2023 | [TrOCR: Transformer-Based Optical Character Recognition with Pre-trained Models](https://ojs.aaai.org/index.php/AAAI/article/view/26538) | Recunoașterea textului tipărit și scris de mână | Transformers, modele preantrenate | Un model vizual procesează imaginea, iar un model de limbaj generează textul recunoscut. | Prezintă rezultate competitive pentru recunoașterea textului, inclusiv scris de mână. | Mai complex decât OCR-ul de bază; poate necesita resurse de calcul mai mari. | Poate fi evaluat ca alternativă dacă EasyOCR nu recunoaște corect numele. |


# AutoAttendance — Detectare Automată a Prezenței Studenților

## Sumar Proiect
 Proiectul își propune **detectarea automată a numelor și prenumelor studenților prezenți** dintr-o foaie de prezență scanată de către utilizator și **completarea automată a unui tabel Excel**, care va fi disponibil ulterior pentru descărcare.

---

## Proiectare & Fluxul Aplicației

### Ipoteze
* **Format foaie:** Foaia conține un tabel cu coloanele *Nume* și *Prenume* (scris de tipar).
* **Format imagine:** Imaginea provine de la telefon/scanner în format **JPG**, **PNG** sau **PDF**.
* **Baza de date studenți:** Lista studenților există într-un fișier Excel existent, organizată pe coloane (*Nume*, *Prenume*, *Grupa*).
* **Stare inițială:** Toți studenții din listă pornesc cu starea `Absent`. Aplicația modifică starea în `Prezent` doar în cazurile în care identifică corect numele și prenumele corespunzător.

---

## Restricții și Limite

### Date de Test
* **Număr de foi de test:** Stabilirea numărului exact de foi folosite pentru evaluare.
* **Variații incluse:** Foi imaginate/scanate strâmb, scris sau semnături slabe (contrast mic), rânduri necompletate (goale).

### Metrici de Evaluare
* **Acuratețe recunoaștere:** Procentul de nume recunoscute corect din imagine.
* **Acuratețe prezențe:** Procentul de prezențe marcate corect în tabelul final.
* **Cazuri incerte:** Numărul total de cazuri ce necesită validare manuală.

### Limitări Cunoscute
* Scris de tipar foarte neclar sau ilizibil.
* Foi îndoite, șifonate sau cu umbre accentuate din cauza fotografierii.


### Arhitectura proiectului- diagramă-bloc
<img width="279" height="871" alt="Diagrama bloc proiect OCR drawio" src="https://github.com/user-attachments/assets/26cf5ce0-3df3-4fff-9cc7-767ca61a492d" />
