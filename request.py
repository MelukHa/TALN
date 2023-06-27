import requests
import os
import re
from nltk.corpus import stopwords
from requests.exceptions import HTTPError
import concurrent.futures
import urllib.parse
#import asyncio
#import aiohttp

def capitalize(mot):
    return mot[0].upper()+mot[1:]

stopWords = stopwords.words('french')
stopWords.extend(list(map(capitalize, stopWords)))
#print(stopWords)
listN = ['ne', 'pas', 'plus', 'rien', 'n', 'jamais', 'ni']

def filter_lines(lines):
    #print("filter_lines")
    first_line = True
    for line in lines:
        if first_line and line.strip().startswith('//'):
            yield line
            first_line = False
        elif not line.strip().startswith('//') and not line.strip().startswith('<'):
            yield line

def fetch(mot):
    try:
        #print("fetch " + mot)
        encoded_mot = urllib.parse.quote_plus(mot.encode('cp1252'), safe=' ')
        #print(encoded_mot)
        #encoded_mot = urllib.parse.quote(mot.encode('cp1252'), safe='')
        #encoded_mot = encoded_mot.replace('%20', '+')
        #url = 'http://jeuxdemots.org/rezo-dump.php'
        #params = {'gotermsubmit': 'Chercher', 'gotermrel': encoded_mot, 'rel': ''}
        #response = requests.get(url, params=params)
        #print('http://jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel=' + encoded_mot + '&rel=')
        response = requests.get('http://jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel=' + encoded_mot + '&rel=')
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print("Une erreur de réseau s'est produite :", e)
        return None

def recup_infos_mot(mot):
    #print("recup_infos_mot "+mot)
    file_path = 'cache/' + mot + '.txt'

    if os.path.isfile(file_path):
        # Le fichier existe déjà, lire les informations depuis le fichier
        with open(file_path, 'r') as file:
            filtered_text = file.read()
        #print('Les lignes filtrées ont été lues à partir du fichier :', file_path)
    else:
        try:
            html = fetch(mot)
        except requests.exceptions.RequestException as e:
            print(f'Erreur lors de la requête pour le mot {mot}: {str(e)}')
            return None

        print("mot : " + str(mot))
        #print(html)
        if '<CODE>' in html:
            lines = html.split('<CODE>')[1].split('\n')
            filtered_lines = filter_lines(lines)
            filtered_text = '\n'.join(filtered_lines)
        else:
            # Gérer le cas où '<CODE>' n'est pas trouve
            encoded_mot = urllib.parse.quote_plus(mot.encode('cp1252'), safe=' ')
            encoded_mot.replace('%20', '+')
            print("Erreur: '<CODE>' introuvable dans la réponse HTML de "+str(encoded_mot))
            return None

        # Écrire les lignes filtrées dans un fichier texte
        with open(file_path, 'w') as file:
            file.write(filtered_text)
        #print('Les lignes filtrées ont été écrites dans le fichier :', file_path)

    return filtered_text

def recup_infos_mots(mots):
    #print("recup_infos_mots")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(recup_infos_mot, mots)

    return list(results)

def recup_infos_mot_fichier(mot):
    #print("recup_infos_mot_fichier")
    file_path = 'cache/' + mot + '.txt'
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return recup_infos_mot(mot)

def remove_none_values(lst):
    #print("remove_none_values")
    return [item for item in lst if item is not None]
 


def get_eid(response):
    #print("get_eid")
    #On récupère l'id du noeud pour en faire un fichier de cache en local
    eid_pos = response.find("eid=")
    #print("print get eid : "+response[eid_pos:eid_pos+10])
    eid_mot = re.sub('[^0-9]', '', response[eid_pos:eid_pos+10])
    return eid_mot

def get_eid_global(data, nom):
    #print("get_eid_global")
    #print("### GET EID GLOBAL DEBUG ###")
    #print(nom)
    lines = data.split('\n')
    for line in lines:
        if line.startswith('e;'):
            line_data = line.split(';')
            if remove_quotes(line_data[2]) == nom:
                return(line_data[1])
    return None

def get_nom(data, eid):
    #print("get_nom")
    lines = data.split('\n')
    for line in lines:
        if line.startswith('e;'):
            line_data = line.split(';')
            if line_data[1] == eid:
                nom = remove_quotes(line_data[2])
                if not (nom.startswith('_') or nom.startswith(':') or '<' in nom):
                    regex = r"[^a-zA-Z .\-'äàáâêëéèîíïôóöûùúüÿçÂÊÎÔÛÄËÏÖÜÀÆæÇÉÈŒœÙ[\]_0-9<>]"
                    if not bool(re.search(regex, nom)): 
                        nom = remove_quotes(nom)
                        if nom != '':
                            if '>' in nom or '<' in nom:
                                raff_sem = line_data[5]
                                raff_sem = remove_quotes(raff_sem)
                                while '>' in raff_sem:
                                    raff_sem = raff_sem.replace('>', ' (', 1)+')'
                                #print(raff_sem)
                                return raff_sem
                            else:
                                return nom
    return None

def get_raff_sem(data, name):
    #print("get_raff_sem")
    liste_raff_sem = []
    if data != None:
        lines = data.split('\n')
        for line in lines:
            if line.startswith('e;'):
                line_data = line.split(';')
                nom = remove_quotes(line_data[2])
                if not (nom.startswith('_') or nom.startswith(':')) and ('<' in nom or '>' in nom) and nom.split('>')[0]==nom:
                    regex = r"[^a-zA-Z .\-'äàáâêëéèîíïôóöûùúüÿçÂÊÎÔÛÄËÏÖÜÀÆæÇÉÈŒœÙ[\]_0-9<>]"
                    if not bool(re.search(regex, line_data[5])):
                        raff_sem = remove_quotes(line_data[5])
                        if raff_sem != '':
                            while '>' in raff_sem:
                                raff_sem = raff_sem.replace('>', ' (', 1)+')'
                            #print(raff_sem)
                            liste_raff_sem.append(raff_sem)
    #print(liste_raff_sem)
    if liste_raff_sem != []:
        return liste_raff_sem
    else:
        return None

def get_rname(rid):
    #print("get_rname")
    #print("### RNAME ###")
    #print(rid)
    with open("data.txt", 'r') as file:
        for line in file:
            data = line.strip().split('|')
            current_rid = data[0].split('=')[1]
            
            if current_rid == rid:
                rname = data[1].split('=')[1].strip('\"')
                #print("rname: " + rname)
                return rname
    return None

def get_rid(nom):
    #print("get_rid")
    #print("### RID ###")
    #print(nom)
    with open("data.txt", 'r') as file:
        for line in file:
            data = line.strip().split('|')
            current_name = data[1].split('=')[1].strip('\"')
            
            if current_name == nom:
                rid = data[0].split('=')[1]
                #print("rid: " + rid)
                return rid
    return None

def remove_quotes(mot):
    #print("remove_quotes")
    while len(mot) >= 2 and (mot[0] == '"' or mot[0] == "'") and (mot[-1] == '"' or mot[-1] == "'"):
        mot = mot[1:-1]
    return mot

def traitement_str(string):
    #print("traitement_str")
    message_split = re.sub('[-\']', ' ', string)
    message_split = re.sub("[^a-zA-Z :.\-'äàáâêëéèîíïôóöûùúüÿçÂÊÎÔÛÄËÏÖÜÀÆæÇÉÈŒœÙ[\]|_0-9]()", '', message_split)
    #print("print message split : " + message_split)
    mots = message_split.split(' ')
    #print("print mots : ")
    #print(mots)
    phrase_correcte = ''
    mots_utiles = []
    negatif = False
    mot_avant = ''  # Variable pour stocker le mot précédent
    for mot in mots:
        if mot in listN:
            negatif = True
        if (mot not in stopWords and mot != '' and mot != ':') or (mot == '[x]') or (mot == '[y]'):
            if mot.startswith('(') and mot.endswith(')'):
                if mot_avant != '':
                    nouveau_mot = mot_avant + ' ' + mot  # Concaténer les mots
                    phrase_correcte += nouveau_mot + ' '
                    mot_avant = ''  # Réinitialiser le mot précédent
                else:
                    phrase_correcte += mot + ' '
            else:
                phrase_correcte += mot + ' '
                mot_avant = mot  # Stocker le mot précédent

    return [phrase_correcte, negatif]

def traitement_raff_sem(mots_utiles):
    print("traitement_raff_sem :")
    renvoie = []
    for i in range(len(mots_utiles)):
        #print(mots_utiles[i])
        data_mot = recup_infos_mot_fichier(mots_utiles[i])
        raffs = get_raff_sem(data_mot, mots_utiles[i])
        print(raffs)
        if raffs == None:
            renvoie.append(mots_utiles[i])
        else:
            recup_infos_mots(raffs)
            raffs.insert(0, mots_utiles[i])
            poids_raffs = [0 for _ in range(len(raffs))] # init poids tous les raffs à 0
            for j in range(len(mots_utiles)):
                if i != j:
                    data_motut = recup_infos_mot_fichier(mots_utiles[j])
                    for k in range(len(raffs)):
                        #print(raffs[k])
                        data_raffk = recup_infos_mot_fichier(raffs[k])
                        if data_raffk != None and data_motut != None:
                            poids_raffs[k] += poids_connexion(data_raffk, get_eid(data_raffk), get_eid(data_motut))
            max_poids_index = max(range(len(poids_raffs)), key=lambda l: poids_raffs[l])
            if poids_raffs[max_poids_index] == 0:
                min_poids_index = min(range(len(poids_raffs)), key=lambda l: poids_raffs[l])
                if poids_raffs[min_poids_index] == 0:
                    max_poids_index = 0
                else:
                    max_poids_index = min_poids_index
            renvoie.append(raffs[max_poids_index])
            print(poids_raffs)
    print(renvoie)
    return renvoie

def concatener_mots_entre_parentheses(liste_mots):
    #print("concatener_mots_entre_parentheses")
    mots_concatenes = []
    i = 0
    while i < len(liste_mots):
        mot = liste_mots[i]
        if mot.startswith('('):
            concatene = liste_mots[i-1] + ' ' + mot
            i += 1
            while i < len(liste_mots) and not liste_mots[i].endswith(')'):
                concatene += ' ' + liste_mots[i]
                i += 1
            if i < len(liste_mots):
                concatene += ' ' + liste_mots[i]
            mots_concatenes[-1] = concatene
        else:
            mots_concatenes.append(mot)
        i += 1
    return mots_concatenes



def poids_connexion(data, eid1, eid2):
    #print("poids_connexion")
    poids = []
    positive_weights = []
    max_neg_weight = 0

    for line in data.split('\n'):
        elements = line.split(';')

        if len(elements) == 6:
            if (elements[2] == eid1 and elements[3] == eid2) or (elements[2] == eid2 and elements[3] == eid1):
                weight = re.sub('[^0-9-]', '', elements[5])  # Extraction du poids en supprimant les caractères non numériques
                if weight != '':
                    weight = int(weight)
                    poids.append(weight)  # Ajout du poids à la liste générale des poids
                    if weight < 0:
                        #print(str(0-weight))
                        max_neg_weight = max(max_neg_weight, 0-weight)  # Mise à jour du poids négatif le plus fort
                    else:
                        positive_weights.append(weight) #On récupère les poids positifs aussi

    poids_sum = sum(poids)  # Calcul de la somme totale des poids
    #print("poids calculé puis liste des poids : ")
    #print(poids_sum)
    #print(poids)
    positive_weights.sort(reverse=True) #On trie les poids positifs par ordre décroissant pour pouvoir récupérer les 5 plus grands
    #print("print ordre des poids positifs et top positive weights : ")
    #print(positive_weights)
    top_positive_weights = positive_weights[:5]
    #print(top_positive_weights)
    if len(top_positive_weights)>0:
        if (max_neg_weight != 0) and (max_neg_weight > (sum(top_positive_weights) / len(top_positive_weights))):
            #print("neg poids")
            return (0-max_neg_weight)
    #print("pos poids")
    return sum(top_positive_weights)

def poids_connexion_avec_relation(data, eid1, eid2, relation):
    #print("poids_connexion_avec_relation")
    poids = []
    positive_weights = []
    max_neg_weight = 0
    rid = get_rid(relation)

    for line in data.split('\n'):
        elements = line.split(';')

        if elements[0]== "r" and len(elements) == 6:
            if ((elements[2] == eid1 and elements[3] == eid2) or (elements[2] == eid2 and elements[3] == eid1)) and elements[4]==rid:
                weight = re.sub('[^0-9-]', '', elements[5])  # Extraction du poids en supprimant les caractères non numériques
                if weight != '':
                    weight = int(weight)
                    poids.append(weight)  # Ajout du poids à la liste générale des poids
                    if weight < 0:
                        #print(str(0-weight))
                        max_neg_weight = max(max_neg_weight, 0-weight)  # Mise à jour du poids négatif le plus fort
                    else:
                        positive_weights.append(weight) #On récupère les poids positifs aussi

    poids_sum = sum(poids)  # Calcul de la somme totale des poids
    #print("poids calculé puis liste des poids : ")
    #print(poids_sum)
    #print(poids)
    positive_weights.sort(reverse=True) #On trie les poids positifs par ordre décroissant pour pouvoir récupérer les 5 plus grands
    #print("print ordre des poids positifs et top positive weights : ")
    #print(positive_weights)
    top_positive_weights = positive_weights[:5]
    #print(top_positive_weights)
    if (len(top_positive_weights) == 0) or ((max_neg_weight != 0) and (max_neg_weight > (sum(top_positive_weights) / len(top_positive_weights)))):
        #print("neg poids")
        return (0-max_neg_weight)
    #print("pos poids")
    return sum(top_positive_weights)



def inference(mot1, mot2, relation_id, eid_mot1=None, eid_mot2=None): 
    #print("inference")
    renvoie = [False, False, None]
    #return de la forme : (Bool rel_directe_trouvee, Bool rel_secondaire_trouvee, int poids_rel_directe, [str nom_noeud_B, str nom_rel_B-C,int poids_rel_A-B, int poids_rel_B-C])
    #print("## inference ##")
    #print(mot1, mot2, relation_id)
    #relation_id prend 6 pour r_isa (déduction), 78 pour r_hypo (induction) etc...
    hypo = False
    liste = [mot1, mot2]
    #print(liste)
    liste = remove_none_values(liste)
    recup_infos_mots(liste)

    if get_rname(relation_id)=="r_hypo" or get_rname(relation_id)=="r_cohypo":
        relation_id = get_rid("r_isa")
        hypo = True

    if eid_mot1 is None:
        # Récupérer les données et l'identifiant pour mot1
        data_mot1 = recup_infos_mot_fichier(mot1)
        if not data_mot1:
            return -1

        eid_mot1 = get_eid(data_mot1)
        if not eid_mot1:
            return -1

    if eid_mot2 is None:
        # Récupérer les données et l'identifiant pour mot2
        data_mot2 = recup_infos_mot_fichier(mot2)
        if not data_mot2:
            return -1

        eid_mot2 = get_eid(data_mot2)
        if not eid_mot2:
            return -1

    # Vérifier si mot1 a des relations avec le rid fourni
    #print(mot1, mot2, relation_id, eid_mot1, eid_mot2)
    
    related_data = []
    negative_data = []

    lines_mot1 = data_mot1.split('\n')
    #print(relation_id)
    for line_mot1 in lines_mot1:
        #print(line_mot1)
        if line_mot1.startswith('r;'):
            line_data_mot1 = line_mot1.split(';')

            if len(line_data_mot1) == 6:
                if line_data_mot1[4] == str(relation_id):
                    weight = int(line_data_mot1[5])
                    #print(line_data_mot1)

                    if weight >= 0:
                        if line_data_mot1[2] == eid_mot1:
                            nom = get_nom(data_mot1, line_data_mot1[3])
                            if nom == mot2:
                                #print("rel dir trouvee donc True + weight normalement")
                                if not renvoie[0]:
                                    renvoie[0] = True
                                    renvoie[2] = weight
                            elif nom is not None:
                                related_data.append((line_data_mot1[3], weight, nom))
                        else:
                            nom = get_nom(data_mot1, line_data_mot1[2])
                            if nom == mot2:
                                #print("rel dir trouvee donc True + weight normalement")
                                if not renvoie[0]:
                                    renvoie[0] = True
                                    renvoie[2] = weight
                            elif nom is not None:
                                related_data.append((line_data_mot1[2], weight, nom))
                    else:
                        if line_data_mot1[2] == eid_mot1:
                            nom = get_nom(data_mot1, line_data_mot1[3])
                            if nom == mot2:
                                #print("rel dir trouvee donc True + weight normalement")
                                if not renvoie[0]:
                                    renvoie[0] = True
                                    renvoie[2] = weight
                            elif nom is not None:
                                negative_data.append((line_data_mot1[3], weight, nom))
                        else:
                            nom = get_nom(data_mot1, line_data_mot1[2])
                            if nom == mot2:
                                #print("rel dir trouvee donc True + weight normalement")
                                if not renvoie[0]:
                                    renvoie[0] = True
                                    renvoie[2] = weight
                            elif nom is not None:
                                negative_data.append((line_data_mot1[2], weight, nom))

    # Trier les données en fonction du poids (du plus grand au plus petit)
    related_data.sort(key=lambda x: x[1], reverse=True)

    # Conserver uniquement les 20 identifiants ayant le poids le plus élevé (ou tous s'il y en a moins de 20)
    related_data = related_data[:20]

    # Trier les données avec des poids négatifs par poids (du plus petit au plus grand)
    negative_data.sort(key=lambda x: x[1])

    # Conserver uniquement les 10 identifiants ayant les poids négatifs les plus bas
    negative_data = negative_data[:10]

    # Ajouter les données avec des poids négatifs à la liste des données
    related_data.extend(negative_data)

    #print(related_data)
    noms_list = [data[2] for data in related_data]
    recup_infos_mots(noms_list)

    # Vérifier si mot2 a une relation avec les mots liés à mot1
    #print("for data in related_data")
    for data in related_data:
        #print("id de la boucle : "+related_id)
        #print(get_nom(data_mot1, related_id), related_id)
        #mot = get_nom(data_mot1, related_id)
        #print(mot)
        mot = data[2]
        poids_A_B = data[1]
        related_id = data[0]
        mot = remove_quotes(mot)
        #print(mot)
        data_related = recup_infos_mot_fichier(mot)
        if not data_related:
            continue

        # Vérifier si mot2 a une relation avec le mot lié à mot1
        lines_related = data_related.split('\n')
        for line_related in lines_related:
            if line_related.startswith('r;'):
                line_data_related = line_related.split(';')
                #print(mot)
                #print(line_data_related)
                if len(line_data_related)==6:
                    poids_B_C = line_data_related[5]
                    if line_data_related[2] == eid_mot2 and hypo:
                        #print("rel sec et append de la rel sec")
                        #print(line_data_related)
                        renvoie[1]=True
                        renvoie.append([get_nom(data_mot1, line_data_related[3]), get_rname(line_data_related[4]), int(poids_A_B), int(poids_B_C)])
                        continue
                    elif line_data_related[3] == eid_mot2 and not hypo:
                        #print("rel sec et append de la rel sec")
                        #print(line_data_related)
                        renvoie[1]=True
                        renvoie.append([get_nom(data_mot1, line_data_related[2]), get_rname(line_data_related[4]), int(poids_A_B), int(poids_B_C)])


    return renvoie