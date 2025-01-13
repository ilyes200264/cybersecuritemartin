# **Seismic GUI**

> Seismic GUI est une interface graphique interactive développée en Python pour faciliter le **traitement** et **l'analyse** des données sismiques avec **Seismic Unix**.

---

## **📋 Fonctionnalités**

### **1. Chargement de Fichiers**
- **Formats supportés** : `.sgy`, `.segy`, `.su`
- **Conversion automatique** des fichiers SEGY en SU avec `segyread`.

### **2. Exécution des Modules Seismic Unix**
| **Module**     | **Description**                                         |
|-----------------|---------------------------------------------------------|
| `surange`      | Affiche les en-têtes d'un fichier SU.                   |
| `suvelan`      | Analyse de la vitesse avec paramètres personnalisés.    |
| `sunmo`        | Correction NMO basée sur des paires temps-vitesse.      |
| `sustack`      | Réalise l'empilement des données.                       |
| `suximage`     | Affiche les résultats en graphique interactif.          |
| `suxwigb`      | Affiche un **wiggle plot** des données.                 |

### **3. Génération de Scripts Bash**
- Exportation du workflow en **scripts bash** pour automatiser les commandes.
- Les scripts générés sont stockés dans `SeismicOutputs`.

---

## **⚙️ Prérequis**

### **1. Environnement Python**
- **Version requise** : Python 3.10+
- **Packages** :
    ```bash
    pip install tkinter subprocess os
    ```

### **2. Installation de Seismic Unix**
- Assurez-vous que **Seismic Unix** est installé :
    ```bash
    export CWPROOT=/usr/local/cwp
    export PATH=$CWPROOT/bin:$PATH
    ```

### **3. Xming (Affichage X11)**
- Téléchargement : [Xming X Server](https://sourceforge.net/projects/xming/)
- Configuration de la variable DISPLAY :
    ```bash
    export DISPLAY=<Votre_Adresse_IP>:0
    ```
    Pour **WSL** :
    - Activez le serveur X11 pour permettre l'affichage.

---

## **💡 Problèmes Courants**

| **Problème**                          | **Solution**                          |
|---------------------------------------|---------------------------------------|
| **Affichage des graphiques**          | Vérifiez que **Xming** est lancé et `DISPLAY` est configuré. |
| **Erreur "Seismic Unix non trouvé"**  | Ajoutez ceci à votre `.bashrc` :      |
|                                       | ```bash                               |
|                                       | export CWPROOT=/usr/local/cwp         |
|                                       | export PATH=$CWPROOT/bin:$PATH        |
|                                       | ```                                   |

---

## **👨‍💻 Crédits**
Projet réalisé pour le cours **INM5001** par :
- **Merwan FRADJ**
- **Mawuena TODO-ALIPUI**
- **Mohamed RAFED YAKOUBI**
- **Ilyes GHORIEB**
