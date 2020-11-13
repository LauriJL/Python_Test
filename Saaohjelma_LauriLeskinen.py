import sqlite3
import http.client
import os
from datetime import datetime

def start():
    #Luodaan lokitiedosto ja kirjataan sinne aloitushetki
    f = open("saaohjelma_loki.txt", "a")
    f.write("..." + "\n" + "Sääohjelma käynnistetty " + str(datetime.now()) + "\n")
    f.write("\n")
    f.close()

    #Luodaan tietokanta ja kursori
    conn = sqlite3.connect('saatiedot.db')
    kursori = conn.cursor()

    #Tietokannan rakenteen luonti
    sql = """CREATE TABLE IF NOT EXISTS paikkakunnat (
        paikkakunta text
    )"""
    kursori.execute(sql)

    # Tallenetaan tietokantamuutokset
    conn.commit()

    #Suljetaan tietokantayhteys
    conn.close()

    print("-----*****-----")
    print("")
    print("Tervetuloa sääohjelmaan")
    print("")

    #Haetaan aikaisemmin tallennettujen paikkakuntien lämpötilat
    haeLampotilat1()

    #Käyttäjä valitsee haluaako lisätä/muuttaa paikkakuntalistaa
    print("")
    print("Haluatko muuttaa seurattavia paikkakuntia (K/E)?")
    print("")
    yesno = input("")
    if yesno == "k":
        #Ensin tyhjennetään paikkakunnat taulun sisältö
        poistaPaikkakunnat()
        #Avataan lisaaPaikkakunta funktio
        lisaaPaikkakunta()
    else:
        print("OK. Ohjelma sulkeutuu.")
        print()
        print("-----*****-----")
        
        #Kirjoitetaan loppuhetki lokitiedostoon ja suljetaan ohjelma
        with open ("saaohjelma_loki.txt", "a") as f:
            f.write("" + "\n" + "Ohjelman ajo lopetettu: " + str(datetime.now()) + "\n" + "...")
            f.close()

#Funktio, jolla haetaan ja tulostetaan ohjelman alussa edellisessä sessiossa tallennettujen paikkakuntien lämpötilat
def haeLampotilat1():
    #Avataan tietokantyhteys ja luodaan kursori
    conn = sqlite3.connect('saatiedot.db')
    kursori = conn.cursor()

    #Haetaan paikkakunnat
    haku = "SELECT * FROM paikkakunnat"
    kursori.execute(haku)
    hakutulos1 = kursori.fetchall()
    hakutulos2 = [i[0] for i in hakutulos1]

    #Tallennetut paikkakunnat
    with open ("saaohjelma_loki.txt", "a") as f:
        f.write("Tallennetut paikkakunnat: " + "\n")
        f.close()

    if len(hakutulos2) == 0:
        print("Ei tallennettuja paikkakuntia.")
        with open ("saaohjelma_loki.txt", "a") as f:
            f.write("Ei tallennettuja paikkakuntia."+ "\n")
            f.close()



    #Loopataan hakutulokset ja haetaan Ilmatieteenlaitokselta lämpötilatieto
    for i in hakutulos2:
        kaupunki = i
        try:           
            conn = http.client.HTTPSConnection("www.ilmatieteenlaitos.fi")
            conn.request("GET", f"/saa/{kaupunki}")
            vastaus = conn.getresponse()
            html = str(vastaus.read())
            temperature = html.index('<span class="temperature-plus"')
            alku = temperature+47
            loppu = alku+2
            #Lisätään strip("\\") poistamaan \-merkki jos lämpötila ilmaistaan vain yhdellä numerolla.
            lampotila = html[alku:loppu].strip("\\")
            if len(kaupunki) >= 7:
                print(f"{kaupunki} \t {lampotila} astetta")
            elif len(kaupunki) < 7:
                print(f"{kaupunki} \t\t {lampotila} astetta")
            
            #Lisätään tallennetut paikkakunnat lokiin
            with open ("saaohjelma_loki.txt", "a") as f:
                f.write(f"{kaupunki}"+ "\n")
                f.close()
        except:
            if len(kaupunki) >= 7:
                print(f"{kaupunki} \t Hakuvirhe: säätietoja ei löytynyt.")
            elif len(kaupunki) < 7:
                print(f"{kaupunki} \t\t Hakuvirhe: säätietoja ei löytynyt.")
            
            #Lisätään tallennetut kaupungit lokiin
            with open ("saaohjelma_loki.txt", "a") as f:
                f.write(f"{kaupunki}"+ "\n")
                f.close()

#Funktio, joka tyhjentää 'paikkakunnat' taulun
def poistaPaikkakunnat():
    #Avataan tietokantyhteys ja luodaan kursori
    conn = sqlite3.connect('saatiedot.db')
    kursori = conn.cursor()

    #Tyhjennetään taulu
    sql = 'DELETE FROM paikkakunnat'
    kursori.execute(sql)

    # Tallenetaan muutokset ja suljetaan tietokantayhteys
    conn.commit()
    conn.close()

#Funktio, jolla käyttäjä voi lisätä kaupunkeja 'paikkakunnat' teuluun
def lisaaPaikkakunta():
    #Avataan tietokantyhteys ja luodaan kursori
    conn = sqlite3.connect('saatiedot.db')
    kursori = conn.cursor()

    #Ohjeet käyttäjälle
    print("Syötä paikkakunta ja paina Enter. Paina X + Enter lopettaaksesi paikkakuntien lisääminen.")
    print("")

    #WHILE loop, jossa lisätään paikkakuntien nimet 'paikkakunnat' tauluun
    while True:
        paikkakunta = input("Lisää paikkakunta: ")
        #Poistaa ääkköset - ei kuitenkaan auta resolvaamaan linkkejä!
        #paikkakunta_removediacr = paikkakunta.replace('ä','a').replace('ö','o').replace('å','a').replace('Ä','A').replace('Ö','O').replace('Å','A')
        
        #Lisätään paikkakunnat tietokantaan
        sql = f'INSERT INTO paikkakunnat VALUES ("{paikkakunta}")'
        kursori.execute(sql)       

        #Poistetaan X/x 'paikkakunnat' taulusta
        sql = f'DELETE FROM paikkakunnat WHERE paikkakunta = "X" OR paikkakunta = "x"'
        kursori.execute(sql)

        #Tallenetaan muutokset
        conn.commit() 
        
        if paikkakunta.upper() == "X":
            break
    #suljetaan tietokantayhteys
    conn.close()
    print("...")
 
    print("")

    #Käyttäjä valitsee haluaako nähdä lisäämiensä paikkauntien lämpötilat
    print("Haluatko hakea näiden paikkakuntien tämän hetkisen lämpötilan Ilmatieteenlaitoksen sääpalvelusta (K/E)?")
    yesno = input("")
    if yesno == "k":
        haeLampotilat2()
    else:
        print("OK. Ohjelma sulkeutuu.")
    print()
    print("-----*****-----")
        
    #Kirjoitetaan loppuhetki lokitiedostoon
    with open ("saaohjelma_loki.txt", "a") as f:
        f.write("" + "\n" + "Ohjelman ajo lopetettu " + str(datetime.now()) + "\n" + "...")
        f.close()

#Funktio, olla haetaan ja tulostetaan lisättyjen paikkakuntien lämpötilat sekä kirjoitetaan näistä tiedot lokitiedostoon
def haeLampotilat2():
    #Avataan tietokantyhteys ja luodaan kursori
    conn = sqlite3.connect('saatiedot.db')
    kursori = conn.cursor()

    #Haetaan paikkakunnat
    haku = "SELECT * FROM paikkakunnat"
    kursori.execute(haku)
    hakutulos1 = kursori.fetchall()
    lkmLisatyt = len(hakutulos1)
    with open ("saaohjelma_loki.txt", "a") as f:
        #Kirjoitetaan lokiin lisättyjen paikkakuntien lukumäärä
        f.write("\n" + "Uudet paikkakunnat määritelty. " + f"{lkmLisatyt} uutta paikkakuntaa lisätty:" + "\n")
    
    #Hakuvirheiden määrä
    lkm_virhe = []
    hakutulos2 = [i[0] for i in hakutulos1]
    #Lista paikkakunnista joiden säätietoja ei löydy
    hakuvirhe = []
    #Lista paikkakunnista joiden säätiedot löytyvät
    lkmLoytyy = []
    lkmLoytyyInt = len(lkmLoytyy)
    #Onnistuneiden ja epäonistuneiden hakuje erotus
    lkm_virhe = 0
    print()
    for i in hakutulos2:
        kaupunki = i
        try:           
            conn = http.client.HTTPSConnection("www.ilmatieteenlaitos.fi")
            conn.request("GET", f"/saa/{kaupunki}")
            vastaus = conn.getresponse()
            html = str(vastaus.read())
            temperature = html.index('<span class="temperature-plus"')
            alku = temperature+47
            loppu = alku+2
            #Lisätään strip("\\") poistamaan \-merkki jos lämpötila ilmaistaan vain yhdellä numerolla.
            lampotila = html[alku:loppu].strip("\\")

            #Tulostetaan onnistuneet haut
            if len(kaupunki) >= 7:
                print(f"{kaupunki} \t {lampotila} astetta")
            else :
                print(f"{kaupunki} \t\t {lampotila} astetta")

            lkmLoytyy.append(kaupunki)
            lkmLoytyyInt = len(lkmLoytyy)

            with open ("saaohjelma_loki.txt", "a") as f:
                f.write(f"{kaupunki} - Säätiedot löytyvät." + "\n")          

        except:
            #Tulostetaan epäonnistuneet haut
            if len(kaupunki) >= 7:
                print(f"{kaupunki} \t Hakuvirhe: säätietoja ei löytynyt.")
            else:
                print(f"{kaupunki} \t\t Hakuvirhe: säätietoja ei löytynyt.")
            with open ("saaohjelma_loki.txt", "a") as f:
                f.write(f"{kaupunki} - Hakuvirhe: Säätietoja ei löydy." + "\n")
            
            #Kerätään hakuvirheet listalle
            hakuvirhe.append(kaupunki)
            #Lasketaan hakuvirheiden lukumäärä          
            lkm_virhe = len(hakuvirhe)
    print()
    print("Ohjelma sulkeutuu.")

    #Lisätään hakutiedot lokiin       
    with open ("saaohjelma_loki.txt", "a") as f:
        f.write("\n" + f"{lkmLoytyyInt} paikkakunnan lämpötilat haettu onnistuneesti." + "\n")
        if lkm_virhe > 0:
            f.write(f"{lkm_virhe} paikkakunnan säätietoja ei löytynyt.")
            f.write("\n")
        f.close()
    
start()