import os
import time
import discord
from discord.ext import commands
import re
from request import *
 
TOKEN = 'Votre Token'#os.getenv('DISCORD_TOKEN')

LAST_REQUETE = None
REQUETE = []
EN_REQUETE = False
 
intents = discord.Intents.default()
intents.message_content = True
activity = discord.Activity(type=discord.ActivityType.listening, name="OIIAOIIA EXTENDED")
 
#client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='/', activity=activity, intents=intents, help_command=None)

 
@bot.event #startup, on supprime les caches trop vieux ou corrompus
async def on_ready():
    #await bot.change_presence(activity=discord.Game(name="Minecraft Forge (RLCraft)"))
    dossier_cache = 'cache/'
    nb_sec_semaine = 7 * 24 * 60 * 60

    # Parcourir tous les fichiers du dossier cache
    for nom_fichier in os.listdir(dossier_cache):
        chemin_fichier = os.path.join(dossier_cache, nom_fichier)

        # Vérifier si le fichier a plus d'une semaine ou s'il est mal formaté
        if (
            (time.time() - os.path.getmtime(chemin_fichier)) > nb_sec_semaine
            or open(chemin_fichier, 'r').read().startswith("MUTED")
        ):
            # Supprimer le fichier
            os.remove(chemin_fichier)
            print(f"Fichier supprimé car corrompu ou trop vieux : {nom_fichier}")
    print(f'{bot.user} has connected to Discord !')


@bot.command()
async def addr(ctx, *args): 
    if ctx.author.id == 351767123808354304:
        string = ' '.join(args)
        #print("string = "+string)
        phrase_correcte = traitement_str(string)[0]
        phrase_correcte+='\n'
        #print(phrase_correcte)
        #await ctx.send(phrase_correcte)
        with open('patrons.txt', 'a') as file:
            file.write(phrase_correcte)
        await ctx.send("phrase bien ajoutée au fichier des patrons")
        return

@bot.command()
async def addrs(ctx, *args):
    if ctx.author.id == 351767123808354304:
        phrase = ' '.join(args).split(' ')  # Divise les lignes par un saut de ligne
        phrase_correcte = ''
        for i in range(0, len(phrase)):
            if phrase[i] == '|':
                phrase.insert(i+2, '\n')
        phrase = ' '.join(phrase).split('\n')
        for line in phrase:
            phrase_correcte += traitement_str(line)[0] + '\n'
        #print("Phrase correcte : " + phrase_correcte)
        #await ctx.send(phrase_correcte)
        with open('patrons.txt', 'a') as file:
            file.write(phrase_correcte)
        await ctx.send("phrases bien ajoutées au fichier des patrons")
        return

@bot.command()
async def doublons(ctx):
    if ctx.author.id == 351767123808354304: # ctx.author.id == 351767123808354304
        with open("patrons.txt", 'r') as file:
            lines = file.readlines()

        # Créer un dictionnaire pour regrouper les lignes par motif
        grouped_lines = {}
        for line in lines:
            pattern, relation = line.strip().split(" | ")
            if pattern in grouped_lines:
                grouped_lines[pattern].add(relation)
            else:
                grouped_lines[pattern] = {relation}

        # Créer une liste de lignes uniques en combinant les relations pour les motifs en doublon
        unique_lines = [f"{pattern} | {' '.join(relations)}\n" for pattern, relations in grouped_lines.items()]

        with open("patrons.txt", 'w') as file:
            file.writelines(unique_lines)

        await ctx.send("Les doublons ont été supprimés du fichier des patrons.")

@bot.command()
async def help(ctx):
    if (ctx.channel.id == 1115192753274503189 or ctx.channel.id == 1118119783007793164):  #ctx.author.id == 351767123808354304   ctx.channel.id == 1115192753274503189 (stage) ctx.channel.id == 1118119783007793164 (LCC)
        print("channel id pour help : "+str(ctx.channel.id))
        await ctx.send("Bonjour, je suis LucasReBot, mon but est d'essayer de vous dire si ce que vous me dites est vrai ou faux. \nQue ce soit une question ou une affirmation, c'est ce que je vais tenter de faire.\nVoici comment m'utiliser :\n\n\tterme1 relation terme2\tpermet de déterminer si deux termes sont liés par une relation en particulier.\n\n\tpourquoi \"assertion\" permet d'avoir le raisonnement derrière un résultat que j'ai produit (pourquoi c'est vrai/faux...)\n\nEnfin, vous pouvez simplement envoyer un message pour que je l'analyse, je ferais de mon mieux pour vous donner une bonne réponse ! :smile:") #\t/addr\tpermet d'ajouter une relation (exemple : [x] oppose [y] | r_anto)\n\t/addrs\tpermet de faire la même chose que /addrs mais sur plusieurs lignes et donc avec plusieurs relations d'un seul coup !\n\t/doublons\tpermet d'effacer les doublons ou de regrouper les relations qui ont le même patron de phrase.\n
        return





@bot.event
async def on_message(message):
    #print("on_message")
    global EN_REQUETE
    global REQUETE
    global LAST_REQUETE

    await bot.process_commands(message) #Rend les commandes utilisables même en écoute d'events

    if (message.channel.id == 1115192753274503189 or message.channel.id == 1118119783007793164)  and message.clean_content[0] != '/': #ctx.author.id == 351767123808354304   ctx.channel.id == 1115192753274503189  (stage) ctx.channel.id == 1118119783007793164 (LCC)
        msg = message.clean_content.lower()
        if msg == "aide" or msg == "help" or msg == "?":
            print("channel id pour help : "+str(message.channel.id))
            await message.channel.send("Bonjour, je suis LucasReBot, mon but est d'essayer de vous dire si ce que vous me dites est vrai ou faux. \nQue ce soit une question ou une affirmation, c'est ce que je vais tenter de faire.\nVoici comment m'utiliser :\n\n\tterme1 relation terme2\tpermet de déterminer si deux termes sont liés par une relation en particulier.\n\n\tpourquoi \"assertion\" permet d'avoir le raisonnement derrière un résultat que j'ai produit (pourquoi c'est vrai/faux...)\n\nEnfin, vous pouvez simplement envoyer un message pour que je l'analyse, je ferais de mon mieux pour vous donner une bonne réponse ! :smile:") #\t/addr\tpermet d'ajouter une relation (exemple : [x] oppose [y] | r_anto)\n\t/addrs\tpermet de faire la même chose que /addrs mais sur plusieurs lignes et donc avec plusieurs relations d'un seul coup !\n\t/doublons\tpermet d'effacer les doublons ou de regrouper les relations qui ont le même patron de phrase.\n

        elif message.author == bot.user:
            if EN_REQUETE:
                if REQUETE:
                    message = REQUETE.pop(0)
                    await process_request(message, False)
                else:
                    EN_REQUETE = False
                    return
            else:
                return
        else:
            async with message.channel.typing():
                if EN_REQUETE:
                    REQUETE.append(message)
                    #await message.reply("Je suis actuellement occupé avec une autre requête, merci de bien vouloir attendre et désolé pour le délai  :sweat_smile:")
                else:
                    EN_REQUETE = True
                    if len(message.clean_content.split(" "))<3 and message.clean_content.split(" ")[0].lower() == "pourquoi" and LAST_REQUETE is not None:
                        await process_request(LAST_REQUETE, True)
                        LAST_REQUETE = None
                    else:
                        LAST_REQUETE = message
                        await process_request(message, False)
        return

async def process_request(message, why):
    #print("process_request")
    liste_mots = message.clean_content.split()
    if liste_mots[0].lower() == "pourquoi" or liste_mots[0].lower() == "pq":
        why = True
        liste_mots = liste_mots[1:]

    newstring = ' '.join(liste_mots)
    phrase = traitement_str(newstring)
    phrase_correcte = phrase[0]
    mots_utiles = phrase_correcte.split(' ')
    negation = phrase[1]
    mots_utiles = [mot for mot in mots_utiles if mot != '']

    #IMPORTANT traitement dans les mots_utiles des raff sem avec chaque liaison entre chaque mots etc
    
    recup_infos_mots(mots_utiles)

    print("mots de la phrase : "+str(liste_mots))
    print("Phrase correcte : " + phrase_correcte)
    print("Mots utiles : " + str(mots_utiles))
        
    previous_words = ""
    mot_clef = None
    next_words = ""

    with open("data.txt", 'r') as file:
        #print("## Test détection inf ##")
        for line in file:
            data = line.strip().split('|')
            keyword = data[1].split('=')[1].strip("\"")
            #print(keyword)

            if keyword in liste_mots:
                index = liste_mots.index(keyword)
                if 0 < index < len(liste_mots) - 1:
                    previous_words = ' '.join(liste_mots[:index])
                    next_words = ' '.join(liste_mots[index+1:])
                    mot_clef = keyword
                    print("les trois chaines detéctées sont : ")
                    print(previous_words)
                    print(keyword)
                    print(next_words)
                    traitement_rf = traitement_raff_sem([previous_words, next_words])
                    previous_words = traitement_rf[0]
                    next_words = traitement_rf[1]
                    await inf(message, previous_words, keyword, next_words, why, negation)
                    return

    mots_utiles = traitement_raff_sem(mots_utiles)
    recup_infos_mots(mots_utiles)
    print("Mots utiles après raffinement sémantique : " + str(mots_utiles))


    pattern_found = False
    if len(mots_utiles) < 2:
        await message.reply("Je suis désolé mais je n'ai pas compris ce que vous m'avez dit, je n'ai pas pu déterminer plusieurs termes utiles à utiliser dans votre demande :sweat_smile:")
        return
    else:
        # Recherche dans les patrons
        with open("patrons.txt", 'r') as file:
            patrons = file.readlines()

        poids = 0
        for patron in patrons:
            #print(patron)
            patron = patron.strip()
            pattern, relations = patron.split(" | ")
            relations = relations.split()
            pattern_elements = pattern.split(" ")

            # Vérification mot par mot puis groupe de mot par groupe de mot
            termes_xy = ["", ""]
            match = True
            i = 0
            j = 0
            while i < len(mots_utiles) and j < len(pattern_elements):
                #print(mots_utiles[i], i, pattern_elements[j], j)
                if pattern_elements[j].startswith("["):
                    group = pattern_elements[j].strip("[]")
                    if group == "x":
                        #print(i, len(mots_utiles), mots_utiles[i], pattern_elements[j+1])
                        while i < len(mots_utiles) and mots_utiles[i] != pattern_elements[j+1]:
                            termes_xy[0] += mots_utiles[i] + " "
                            i += 1
                        #print(termes_xy[0])
                        j += 1
                        termes_xy[0] = termes_xy[0].strip()
                    elif group == "y":
                        while i < len(mots_utiles):
                            termes_xy[1] += mots_utiles[i] + " "
                            i += 1
                        termes_xy[1] = termes_xy[1].strip()
                    else:
                        group_elements = group.split(" ")
                        if mots_utiles[i:i+len(group_elements)] == group_elements:
                            i += len(group_elements)
                            j += 1
                        else:
                            match = False
                            break
                elif pattern_elements[j] == mots_utiles[i]:
                    i += 1
                    j += 1
                else:
                    match = False
                    break
                    
            #print(termes_xy)
            if termes_xy[0] == '' or termes_xy[1] == '':
                match = False
            

            if match:
                print("################ termes : ##############")
                print(termes_xy)
                print(liste_mots)
                print(mots_utiles)
                new_liste_mots = concatener_mots_entre_parentheses(liste_mots)
                print(new_liste_mots)

                if len(termes_xy[0].split()) > 1:
                    if ')' in termes_xy[0]:
                        termes_xy[0] = termes_xy[0].split(')')[0] + ')'
                        #print(termes_xy)
                    else:
                        # Récupérer l'indice du premier et du dernier mot de termes_xy[0] dans liste_mots
                        first_word = termes_xy[0].split()[0]
                        last_word = termes_xy[0].split()[-1]
                        # Récupérer tous les mots entre le premier et le dernier mot
                        regex_pattern = fr"\b{re.escape(first_word)}\b.*?\b{re.escape(last_word)}\b"
                        words_between = re.findall(regex_pattern, ' '.join(new_liste_mots))
                        #print(words_between)
                        termes_xy[0] = ' '.join(words_between)
                        if '(' in words_between:
                            termes_xy[0]+=')'

                if len(termes_xy[1].split()) > 1:
                    if ')' in termes_xy[1]:
                        #print("########################   )   ##########")
                        termes_xy[1] = termes_xy[1].split(')')[0] + ')'
                        #print(termes_xy)
                    else:
                        # Récupérer l'indice du premier et du dernier mot de termes_xy[1] dans liste_mots
                        first_word = termes_xy[1].split()[0]
                        last_word = termes_xy[1].split()[-1]
                        # Récupérer tous les mots entre le premier et le dernier mot
                        regex_pattern = fr"\b{re.escape(first_word)}\b.*?\b{re.escape(last_word)}\b"
                        words_between = re.findall(regex_pattern, ' '.join(new_liste_mots))
                        #print(words_between)
                        termes_xy[1] = ' '.join(words_between)
                        if '(' in termes_xy[1] and ')' not in termes_xy[1]:
                            termes_xy[1]+=')'

                #print(termes_xy)
                termes_xy = traitement_raff_sem(termes_xy)
                print(termes_xy)

                print("match avec le patron : "+patron+" et donc les relations suivantes :")
                if isinstance(relations, str):
                    relations = [relations]
                print(relations)

                # Les termes sont liés par la relation obtenue via les patrons
                data = recup_infos_mot_fichier(termes_xy[0])
                ok = None

                if data is not None:
                    poids_relations = [0 for _ in range(len(relations))]
                    for i in range(len(relations)):
                        poids_relations[i] = poids_connexion_avec_relation(data, get_eid(data), get_eid_global(data, termes_xy[1]), relations[i])
                    print(poids_relations)
                    await inf(message, termes_xy[0], relations[poids_relations.index(max(poids_relations))], termes_xy[1], why, negation)
                    return



        # En cas de non match :
        print("pas de match pour cette fois.............")

        poids = 0
        for i in range(0, len(mots_utiles)-1):
            data1 = recup_infos_mot_fichier(mots_utiles[i])
            if data1 is None:
                await message.reply("Soit "+mots_utiles[i]+" nest pas reconnu, soit il n'est pas connu de la base de connaissance")
                return
            eid1 = get_eid(data1)
            for j in range(i+1, len(mots_utiles)):
                #print("i : "+str(i)+", j : "+str(j))
                #print("mot actuel : "+ mots_utiles[j])
                data2 = recup_infos_mot_fichier(mots_utiles[j])
                if data2 is None:
                    await message.reply("Soit "+mots_utiles[j]+" n'est pas reconnu, soit il n\'est pas connu de la base de connaissance")
                    return
                eid2 = get_eid(data2)

                poids += poids_connexion(data1, eid1, eid2)

        if (poids >= len(mots_utiles)*40 and not negation) or (poids <= len(mots_utiles)*(-20) and negation):
            await message.reply("C'est vrai : "+ str(poids))
        elif (poids >= len(mots_utiles)*40 and negation) or (poids <= len(mots_utiles)*(-20) and not negation):
            await message.reply("C'est faux : "+ str(poids))
        else:

            total_vrai_deduc = 0
            total_faux_deduc = 0
            total_vrai_induc = 0
            total_faux_induc = 0
            total_combinaisons = 0

            for i in range(0, len(mots_utiles)-1):
                for j in range(i+1, len(mots_utiles)):
                    total_combinaisons += 1
                    #print(mots_utiles[i], mots_utiles[j])

                    result_deduc = inference(mots_utiles[i], mots_utiles[j], get_rid("r_isa"))
                    if result_deduc != -1:
                        if result_deduc[0] == True or result_deduc[1] == True:
                            total_vrai_deduc += 1
                        else:
                            total_faux_deduc += 1
                    else:
                        print("J'ai rencontré une erreur pendant la récupération des données, l'un des fichier nécessaire à l'analyse est arrivé corrompu (sûrement trop de demandes au serveur), désolé :sweat_smile: avec les mots "+mots_utiles[i] + " et " + mots_utiles[j])
                        continue

                    result_induc = inference(mots_utiles[i], mots_utiles[j], get_rid("r_hypo"))
                    if result_induc != -1:
                        if result_induc[0] == True or result_induc[1] == True:
                            total_vrai_induc += 1
                        else:
                            total_faux_induc += 1
                    else:
                        print("J'ai rencontré une erreur pendant la récupération des données, l'un des fichier nécessaire à l'analyse est arrivé corrompu (sûrement trop de demandes au serveur), désolé :sweat_smile: avec les mots "+mots_utiles[i] + " et " + mots_utiles[j])
                        continue

            #poids_deduc = total_combinaisons/2
            #poids_induc = total_combinaisons/2

            #total_vrai_deduc += poids_deduc
            #total_vrai_induc += poids_induc

            # IMPORTANT : refaire cette partie pour l'interprétation des résultats et ajouter la negation ! conclusions pas pratiques pour peu de combinaisons 
            
            print("total vrai deduc : "+str(total_vrai_deduc))
            print("total vrai induc : "+str(total_vrai_induc))
            print("total combinaisons : "+str(total_combinaisons))

            if (total_vrai_deduc > 2*(total_combinaisons/3) and not negation) or (not (total_vrai_deduc > 2*(total_combinaisons/3)) and negation):
                await message.reply("Déduction : la phrase \""+newstring+"\" est vraie")
            elif (total_vrai_deduc < (total_combinaisons/3) and not negation) or (not (total_vrai_deduc < (total_combinaisons/3)) and negation):
                await message.reply("Déduction : la phrase \""+newstring+"\" est fausse")

            else:
                if (total_vrai_induc > 2*(total_combinaisons/3) and not negation) or (not (total_vrai_induc > 2*(total_combinaisons/3)) and negation):
                    await message.reply("Induction : la phrase \""+newstring+"\" est vraie")
                elif (total_vrai_induc < (total_combinaisons/3) and not negation) or (not (total_vrai_induc < (total_combinaisons/3)) and negation):
                    await message.reply("Induction : la phrase \""+newstring+"\" est fausse")
                else:
                    await message.reply("Je n'ai pas pu déterminer si ce que vous m'avez dit est vrai ou faux...............")
        return


async def inf(message, arg1, arg2, arg3, why, negation):
    #print("inf")
    poids = 0
    liste = [arg1, arg3]

    recup_infos_mots(liste)

    data1 = recup_infos_mot_fichier(arg1)
    if data1 is None:
        await message.reply("Soit "+arg1+" nest pas reconnu, soit il n'est pas connu de la base de connaissance")
        return
    eid1 = get_eid(data1)

    data2 = recup_infos_mot_fichier(arg3)
    if data2 is None:
        await message.reply("Soit "+arg3+" n'est pas reconnu, soit il n\'est pas connu de la base de connaissance")
        return
    eid2 = get_eid(data2)

    result = inference(arg1, arg3, get_rid(arg2))
    #print(result)
    if result != -1:
        print("####### nouveau inf tests #######")
        print(result)
        #[Bool rel_directe_trouvee, Bool rel_secondaire_trouvee, str nom_noeud_B, str nom_rel_B-C,int poids_rel_directe,int poids_rel_A-B, int poids_rel_B-C]
        rel_directe_trouvee = result[0]
        rel_secondaire_trouvee = result[1]
        relations_secondaires = []
        relations_pos = 0
        relations_neg = 0
        positive = None

        if rel_secondaire_trouvee:
            print("rel sec trouvée")
            for i in range(3, len(result)):
                relations_secondaires.append(result[i]) #[str nom_noeud_B, str nom_rel_B-C,int poids_rel_A-B, int poids_rel_B-C]
            noms_relations = list(set([liste[1] for liste in relations_secondaires])) #La liste de toutes les relations trouvées 
            print(relations_secondaires)
            for relation in relations_secondaires:
                if relation[2]>=20 and relation[3]>=20:
                    relations_pos+=1
                elif relation[2]>=20 and relation[3]<0:
                    relations_neg+=1
            print("relations pos : "+str(relations_pos))
            print("relations neg : "+str(relations_neg))
            print("total relations : "+str(len(relations_secondaires)))
            print("negation : "+str(negation))

            if ((relations_pos>2*relations_neg or relations_pos>len(relations_secondaires)/2) and negation==False) or ((relations_neg>2*relations_pos or relations_neg>len(relations_secondaires)/2) and negation==True):
                positive = True
            elif ((relations_neg>2*relations_pos or relations_neg>len(relations_secondaires)/2) and negation==False) or ((relations_pos>2*relations_neg or relations_pos>len(relations_secondaires)/2) and negation==True):
                positive = False
            print("positive : "+str(positive))

        string = ""
        relations_deja_vues = []  # Ensemble pour stocker les noms de relations déjà vus
        mots_deja_vus = []  # Ensemble pour stocker les noms de mots déjà vus
        if rel_directe_trouvee:
            print("rel dir")
            poids_rel_directe = int(result[2])
            if (poids_rel_directe >= 20 and positive == True) or (poids_rel_directe < 0 and positive == True):
                print("true rel dir")
                if why:
                    string += "Conclusion : "+arg1+" et "+arg3+" sont bien reliés par la relation "+arg2+" et c'est vrai ! (poids = "+str(poids_rel_directe)+")\n"
                    if rel_secondaire_trouvee:
                        string += "Voici quelques pistes d'explications :\n"
                        i = 1
                        for donnees in relations_secondaires:
                            if i == 6:
                                break
                            if donnees[1] in noms_relations and donnees[2] >= 20 and donnees[3] >= 20:
                                if (donnees[1] not in relations_deja_vues or donnees[0] not in mots_deja_vus) and relations_deja_vues.count(donnees[1]) < 2 and mots_deja_vus.count(donnees[0]) < 2:
                                    relations_deja_vues.append(donnees[1])
                                    mots_deja_vus.append(donnees[0])
                                    string += str(i) + ". " + arg1 + " est relié à " + donnees[0] + " qui est lié à " + arg3 + " par la relation " + donnees[1] + ". (poids : rel A-B = " + str(donnees[2]) + " et rel B-C = " + str(donnees[3]) + ")\n"
                                    i+=1
                    else:
                        string += "Je n'ai pas pu trouver de relations permettant de confirmer cette liaison d'une autre manière, désolé :sweat_smile:"
                else:
                    string += "Conclusion : c'est vrai ! :thumbsup:"

            elif (poids_rel_directe < 0 and positive == False) or (poids_rel_directe >= 20 and positive == False):
                print("false rel dir")
                if why:
                    string += "Conclusion : "+arg1+" et "+arg3+" sont bien reliés par la relation "+arg2+" mais c'est faux ! (poids = "+str(poids_rel_directe)+")\n"
                    if rel_secondaire_trouvee:
                        string += "Voici quelques pistes d'explications :\n"
                        i = 1
                        for donnees in relations_secondaires:
                            if i == 6:
                                break
                            if donnees[1] in noms_relations and donnees[2]>=20 and donnees[3]<0:
                                if (donnees[1] not in relations_deja_vues or donnees[0] not in mots_deja_vus) and relations_deja_vues.count(donnees[1]) < 2 and mots_deja_vus.count(donnees[0]) < 2:
                                    relations_deja_vues.append(donnees[1])
                                    mots_deja_vus.append(donnees[0])
                                    string += str(i)+". "+arg1+" est relié à "+donnees[0]+" qui est un contraire de "+arg3+", lié par la relation "+donnees[1]+". (poids : rel A-B = "+str(donnees[2])+" et rel B-C = "+str(donnees[3])+")\n"
                                    i+=1
                    else:
                        string += "Je n'ai pas pu trouver de relations permettant de confirmer cette liaison d'une autre manière, désolé :sweat_smile:"
                else:
                    string += "Conclusion : c'est faux ! :thumbsdown:"

            else:
                print("nsp rel dir")
                if why:
                    string += "Conclusion : "+arg1+" et "+arg3+" sont bien reliés par la relation "+arg2+", mais je n'ai pas assez d'informations pour déterminer correctement si c'est vrai ou faux... (poids = "+str(poids_rel_directe)+")\n"
                    if rel_secondaire_trouvee:
                        string += "Voici quelques pistes d'explications :\n"
                        i = 1
                        for donnees in relations_secondaires:
                            if i == 6:
                                break
                            if donnees[1] in noms_relations and donnees[2]>=20:
                                if (donnees[1] not in relations_deja_vues or donnees[0] not in mots_deja_vus) and relations_deja_vues.count(donnees[1]) < 2 and mots_deja_vus.count(donnees[0]) < 2:
                                    relations_deja_vues.append(donnees[1])
                                    mots_deja_vus.append(donnees[0])
                                    string += str(i)+". "+arg1+" est relié à "+donnees[0]+" qui est lié à "+arg3+" par la relation "+donnees[1]+". (poids : rel A-B = "+str(donnees[2])+" et rel B-C = "+str(donnees[3])+")\n"
                                    i+=1
                        string += "\nLe tout ne permet pas vraiment de déterminer si c'est vrai ou si c'est faux"
                    else:
                        string += "De plus, je n'ai pas pu trouver de relations permettant de confirmer cette liaison d'une autre manière, désolé :sweat_smile:"
                else:
                    string += "Conclusion : je n'en suis pas certain, les deux mots sont reliés mais ce n'est pas assez précis pour que je le sache :sweat_smile:"


        elif rel_secondaire_trouvee:
            print("rel sec")
            if positive == True:
                print("pos rel sec")
                if why:
                    string += "Les mots "+arg1+" et "+arg3+" ne sont pas reliés, mais partagent les relations positives suivantes :\n"
                    i = 1
                    for donnees in relations_secondaires:
                        if i == 6:
                            break
                        if donnees[1] in noms_relations and donnees[2]>=20 and donnees[3]>=20:
                            if (donnees[1] not in relations_deja_vues or donnees[0] not in mots_deja_vus) and relations_deja_vues.count(donnees[1]) < 2 and mots_deja_vus.count(donnees[0]) < 2:
                                relations_deja_vues.append(donnees[1])
                                mots_deja_vus.append(donnees[0])
                                string += str(i)+". "+arg1+" est relié à "+donnees[0]+" qui est lié à "+arg3+" par la relation "+donnees[1]+". (poids : rel A-B = "+str(donnees[2])+" et rel B-C = "+str(donnees[3])+")\n"
                                i+=1
                string += "Conclusion : selon moi c'est vrai ! :thumbsup:"

            elif positive == False:
                print("neg rel sec")
                if why:
                    string += "Les mots "+arg1+" et "+arg3+" ne sont pas reliés, mais partagent les relations négatives suivantes :\n"
                    i = 1
                    for donnees in relations_secondaires:
                        if i == 6:
                            break
                        if donnees[1] in noms_relations and donnees[2]>=20 and donnees[3]<0:
                            if (donnees[1] not in relations_deja_vues or donnees[0] not in mots_deja_vus) and relations_deja_vues.count(donnees[1]) < 2 and mots_deja_vus.count(donnees[0]) < 2:
                                relations_deja_vues.append(donnees[1])
                                mots_deja_vus.append(donnees[0])
                                string += str(i)+". "+arg1+" est relié à "+donnees[0]+" qui est lié à "+arg3+" par la relation "+donnees[1]+". (poids : rel A-B = "+str(donnees[2])+" et rel B-C = "+str(donnees[3])+")\n"
                                i+=1
                string += "Conclusion : selon moi c'est faux ! :thumbsdown:"

            else:
                print("nsp rel sec")
                if why:
                    string += "Les mots "+arg1+" et "+arg3+" ne sont pas reliés, mais partagent les relations positives suivantes dont je ne suis pas encore capable d'examiner la pertinence :\n"
                    i = 1
                    for donnees in relations_secondaires:
                        if i == 6:
                            break
                        if donnees[1] in noms_relations and donnees[2]>=20:
                            if (donnees[1] not in relations_deja_vues or donnees[0] not in mots_deja_vus) and relations_deja_vues.count(donnees[1]) < 2 and mots_deja_vus.count(donnees[0]) < 2:
                                relations_deja_vues.append(donnees[1])
                                mots_deja_vus.append(donnees[0])
                                string += str(i)+". "+arg1+" est relié à "+donnees[0]+" qui est lié à "+arg3+" par la relation "+donnees[1]+". (poids : rel A-B = "+str(donnees[2])+" et rel B-C = "+str(donnees[3])+")\n"
                                i+=1
                string += "Conclusion : je n'en suis pas certain, les deux mots sont reliés mais ce n'est pas assez précis pour que je le sache :sweat_smile:"

        else:
            string += "Je n'ai pas trouvé de relation du tout entre "+arg1+" et "+arg3+" via la relation "+arg2+", désolé :sweat_smile:"
        
        await message.reply(string)
        return

    else:
        await message.reply("J'ai rencontré une erreur pendant la récupération des données, l'un des fichier nécessaire à l'analyse est arrivé corrompu (sûrement trop de demandes au serveur), désolé :sweat_smile:")
        return

bot.run(TOKEN)
#client.run(TOKEN)
