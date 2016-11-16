#!/usr/bin/env python
# -*- coding: Utf-8 -*-

# Purge d'un répertoire +
# =====================

# Les fichiers d'un répertoire sont purgés de manière à conserver les plus récents.

# Le critère de purge peut être :
# - Un nombre jours de rétention.
# - Une taille du répertoire.

# Lorsque le nombre de jours et la taille sont précisés, le nombre de jour est utilisé
# en premier et la taille totale en deuxième pour que la taille totale du répertoire
# ne soit pas être dépassée.

import sys, os, getopt, time, string
from stat import *

# Configuration ===============================================================
debug=0

# Constantes ==================================================================

# Nom de ce script
script_name=os.path.basename(sys.argv[0])

# Codes d'erreur
E_WRONGARGS=65  # Non-numerical argument (bad arg format)

# Affichage de l'aide =========================================================
def syntaxe(court, err_cde):
  if court:
    print("Tapez '" + script_name + " -h' pour de l'aide.")
  else:
    print("Purge d'un répertoire.")
    print("Syntaxe : ", script_name, " [-h | --help] [Options] chemin_a_purger")
    print("Options :")
    print("-h ou --help : Affichage de cet aide.")
    print("-d n = le nombre de jours de rétention. Les fichiers âgés de plus")
    print("       de n jours sont effacés.")
    print("-s n = la taille maximale. La taille par défaut est en octets.")
    print("       Elle peut aussi être spécifiée en Ko, Mo, Go ou To en")
    print("       ajoutant respectivement K, M, G ou T au chiffre. Par")
    print("       exemple -s8M correspond à 8 Mo ou 8 388 608 octets.")
    print("       Les fichiers les plus âgés sont supprimés pour que la")
    print("       taille totale du répertoire ne dépasse pas n.")
    print("-t ou --test : Ne supprime pas les fichiers.")
    print("-v : Affiche les fichiers à supprimer.")
    print("chemin_a_purger = le chemin du répertoire à purger")
    print("-d ET -s peuvent être donnés simmultanément. Dans ce cas l'âge")
    print("est pris en compte en premier.")
  sys.exit(err_cde)

# Traiement ===================================================================

# Extraction des paramètres ...................................................

# Valeurs par défaut
days=None	# Nombre de jours
tail=None	# Nombre de mégaoctets
chem=None	# Chemin
test = 0  # Mode test
verb = 0  # Mode verbose

# Lecture des arguments de la ligne de commande
try:
  opts, args = getopt.gnu_getopt(sys.argv[1:], "vhtd:s:", ["help", "test"])
except getopt.GetoptError as err:
  print(str(err))
  syntaxe(1, E_WRONGARGS)

# maintenant on les convertit
for opt, arg in opts:

  # Demande d'aide
  if opt in ("-h", "--help"):
    syntaxe(0, 0)
  
  # Passage en mode test
  if opt in ("-t", "--test"):
    test = 1
  
  # Passage en mode verbose
  if opt == '-v':
    verb = 1
  
  # Nombre de jours de rétention
  elif opt == '-d':
    if days != None:
      print("*** Nombre de jours déjà renseignés")
      syntaxe(1, E_WRONGARGS)
    try:
      days = int(arg)
    except ValueError:
      print("*** Nombre de jours invalides")
      syntaxe(1, E_WRONGARGS)
  
  # Taille maxi en Mo
  elif opt == '-s':
    if tail != None:
      print("*** Taille déjà renseignée")
      syntaxe(1, E_WRONGARGS)
    tail = arg
    i=len(tail)-1
    m = string.upper(tail[i])
    if m in ('K', 'M', 'G', 'T'):
      tail = tail[:i]
      if m == 'K':
        mult = 1024
      elif m == 'M':
        mult = 1024 * 1024
      elif m == 'G':
        mult = 1024 * 1024 * 1024
      else:   # 'T'
        mult = 1024 * 1024 * 1024 * 1024
    else:
      mult = 1
    try:
      tail = int(tail) * mult
    except ValueError:
      print("*** Taille invalide")
      syntaxe(1, E_WRONGARGS)
    
# Lecture du chemin
if len(args) > 0:
  if len(args) > 1:
    print("*** Trop d'arguments")
    syntaxe(1, E_WRONGARGS)
  chem = args[0]
  if not os.path.isdir(chem):
    print("*** Parametre inconnu ou répertoir non valide")
    syntaxe(1, E_WRONGARGS)
  if not os.access(chem, os.F_OK | os.R_OK | os.W_OK | os.X_OK):
    print("*** Droits d'acces au répertoire insuffisants")
    syntaxe(1, E_WRONGARGS)
  
# Test de validité des paramètres
if days == 0:
  print("*** Nombre de jours à 0 invalide")
  syntaxe(1, E_WRONGARGS)
if tail == 0:
  print("*** Taille à 0 invalide")
  syntaxe(1, E_WRONGARGS)
if days == None and tail == None:
  print("*** Nombre de jours OU taille obligatoire")
  syntaxe(1, E_WRONGARGS)
if chem == None:
  print("*** Chemin obligatoire")
  syntaxe(1, E_WRONGARGS)

# Tout semble ok ici. Les arguments sont extraits, affichons les
if debug:
  print("debug actif: Dump des variables")
  if days != None:
    print("days =", days)
  if tail != None:
    print("tail =", tail)
  print("chem = '" + chem + "'")

# Pour le stockage et le traitement des fichiers
class Fic:
  
  # Constructeur
  def __init__(self, nm, fi):
    
    # Stocker le nom
    self.nom = nm
    
    # La taille
    self.siz = fi.st_size
    
    # l'horodatage
    self.dat = fi.st_mtime   # Acces = st_atime, modif = st_mtime, creation = st_ctime
    
    # L'ancienneté en nombre de jours
    self.age = int((time.time() - self.dat) / (3600 * 24))
    
# Pour le tri par date décroissante
def sort_fic(f1, f2):
  if f2.dat < f1.dat:
    return -1
  return f2.dat > f1.dat
    
# Extracion de la liste des fichiers du répertoire
rep = os.listdir(chem)

# Oter le slash à la fin de chem
i=len(chem)-1
if chem[i] == '/':
  chem = chem[:i]

# Traiter la liste des fichier (récup taille et date à la'aide de FIC)
f = []
if verb:
  print(" SUPPR    DATE     HEURE\tTAILLE\tAGE\tNOM")
for fl in rep:
  fic = chem + '/' + fl
  try:
    fi = os.stat(fic)
  except OSError as err:
    print("*** Warning " + fl + ": " + str(err))
  else:
    if S_ISREG(fi[ST_MODE]):    # Que les fichiers (pas les répertoires)
      f.append(Fic(fl, fi))

# Petit tri par date décroissante
f.sort(sort_fic)

# Traitement final des fichiers
tots=0        # Taille totale des fichiers
for nm in f:

  if verb:
    msg = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(nm.dat)) + \
      "\t" + str(nm.siz) + "\t" + str(nm.age) + "\t" + nm.nom
  
  # Totaliser la taille
  tots = tots + nm.siz
  
  sup = 0
  if days != None:
    if nm.age > days:
      sup = 1
      
  if tail != None and not sup:
    if tots > tail:
      sup = 2

  if sup:
    if verb: 
      if sup == 1:
        msg = "-age   " + msg
      else:
        msg = "-taile " + msg
    if not test: 
      os.unlink(chem + '/' + nm.nom)
  elif verb:
    msg = "       " + msg
    
  if verb: print(msg)
    
sys.exit(0)
