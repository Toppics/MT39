# -*- coding: utf-8 -*-
"""
Created on Wed May  1 23:43:37 2024

@author: yan-s
"""
from time import sleep
from matplotlib import rcParams
from matplotlib.cm import rainbow
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

rcParams['figure.dpi']:float = 300    # Augmenter la résolution des figures

class Lotka_Volterra:
    """Modèle dynamique par le système Lotka-Volterra."""
    def __init__(self, x0, y0, r, p, m, q):
        self.x0 = x0; self.y0 = y0
        self.r = r; self.p = p
        self.m = m; self.q = q
        self.orbite_x = self.m / self.q     # Plus cohérent de faire une liste pour intégrer orbite trivial?
        self.orbite_y = self.r / self.p

    def __getattr__(self, name):
        return self.__dict__[f"__{name}"]

    def __setattr__(self, name, value):
        if name in ['x0', 'y0', 'X']:
            if type(value) is not int:
                raise ValueError(f'{name} doit être un entier!')
        else:
            if type(value) is not float:
                raise ValueError(f'{name} doit être un réel!')
        if value < 0:
            raise ValueError(f'{name} doit être supérieur ou égal à 0!')
        self.__dict__[f"__{name}"] = value

    def _variation_lapin(self, x, y) -> float:
        """Variation du nombre de lapins."""
        return self.r*x - self.p*x*y

    def _variation_lynx(self, x, y) -> float:
        """Variation du nombre de lynx."""
        return -self.m*y + self.q*x*y

    def modele_Lotka_Volterra(self, t_min: int, t_max: int, h: float) -> pd.DataFrame:
        """h: le pas."""
        t = t_min
        dx, dy = self.x0, self.y0
        lst = [[t, dx, dy]]
        while lst[-1][0] <= t_max:
            t += h
            dx += self._variation_lapin(dx, dy)*h
            dy += self._variation_lynx(dx, dy)*h
            lst.append([t, dx, dy])
        return pd.DataFrame(lst, columns=["t", "x", "y"])

    def affichage(self, t_min: int, t_max: int, h: float):
        """Population de lièvres et de lynx en fonction du temps."""
        df = self.modele_Lotka_Volterra(t_min, t_max, h)
        plt.plot(df['t'], df['x'], 'b', label='Lapins', linestyle='solid')
        plt.plot(df['t'], df['y'], 'r', label='Lynx', linestyle='dashed')
        plt.xlabel('Mois'); plt.ylabel('Population en unité')
        plt.title(f'Population de lapins et de lynx au cours du temps.\nConditions initiales : {self.x0} lapins pour {self.y0} lynx sur une durée de {t_max-t_min} mois.')
        plt.legend(bbox_to_anchor=(1.05, 1), shadow=True)
        plt.grid(); plt.xlim(t_min, t_max)#; plt.ylim(0,)
        plt.show()

    ## Méthode d'affichage un peu plus complexes
    def affichage_variation__τ(self, t_min: int, t_max: int, h: float, var:str, Delta:float = 0.5):
        """Affichage des varations des τ.
        ----------
        var : str -> 'r' | 'p' | 'm' | 'q'.
        Delta : float, optional -> Varations totales avec un pas de 0.1, in fine le nombre de courbes. 0.5 par défaut.
        """
        if f'__{var}' not in self.__dict__:
            raise AttributeError(f'__{var} doit être dans {self.__dict__.keys()}!')
        if type(Delta) is not (float or int):
            raise ValueError(f'{Delta} doit être un réel ou un entier!')
        deltas = np.arange(eval(f'self.__{var}'), eval(f'self.__{var}') + Delta, 0.1)   # On créer l'intervalle
        colors = rainbow(np.linspace(0, 1, np.random.random((10,len(deltas))).shape[0]))  # On génére des couleurs pour chaque courbe
        fig, ax = plt.subplots(2,1)     # Créer la figure
        for delta, i in zip(deltas, range(len(deltas))):    # Créer chaque courbe
            setattr(self, var, float(delta))    # Réactualise la variable var de l'instance
            df = self.modele_Lotka_Volterra(t_min, t_max, h)
            ax[0].plot(df['t'], df['x'], color = colors[i],  linestyle = '-', label = r"$\delta = $" + "{0:.2f}".format(delta))
            ax[1].plot(df['t'], df['y'], color = colors[i], linestyle = '-', label = r" $\delta = $" + "{0:.2f}".format(delta))
            ax[1].legend()
        ax[0].set_xlabel('Mois'); ax[1].set_xlabel('Mois')
        ax[0].set_ylabel('Lapins'); ax[1].set_ylabel('Lynx')
        ax[1].legend(title=f'Variation de {var}', bbox_to_anchor=(1.05, 1), shadow=True)
        fig.suptitle(f'Population de lapins et de\nlynx au cours du temps.\nConditions initiales :\n{self.x0} lapins pour {self.y0} lynx sur\nune durée de {t_max-t_min} mois.', x=0.92, y=0.8, ha='left', fontsize= 10)
        ax[0].grid(); ax[1].grid(); plt.show()

    def affichage_orbite(self, t_min: int, t_max: int, h: float, lst_condition_initiale:list = [x for x in range(-2, 12, 2)], orbite:bool = False):
        """ """
        if type(orbite) is not bool:
            raise ValueError(f'{orbite} doit être un booléen!')
        if type(lst_condition_initiale) is not list:
            raise ValueError(f'{lst_condition_initiale} doit être une liste!')
        for element in lst_condition_initiale:
            if type(element) is not (float and int):
                raise ValueError(f'{element} doit être un réel ou un entier!')
        for init in lst_condition_initiale:     # Pas très poo mais fonctionne v(´・∀・｀*)v
            _dict = dict(self.__dict__) # Nouveau dictionnaire avec paramètres modifiés
            for key in self.__dict__.keys():
                if key.startswith('__'): _dict[key[2:]] = _dict.pop(key)
                else: _dict[key] = _dict.pop(key)
            _dict['x0'] = self.x0+init; _dict['y0'] = self.y0+init
            _dict.pop('orbite_x'); _dict.pop('orbite_y')
            ode = eval(self.__class__.__name__)(**_dict)   # Instancie un objet
            df = ode.modele_Lotka_Volterra(t_min, t_max, h)
            plt.plot(df['x'], df['y'], label=f'{init}', linestyle='solid')
        if orbite:  # Trace l'orbite (on se passe de l'obite trivial)
            plt.plot(self.orbite_x, self.orbite_y, 'x', label='Orbite')
        plt.xlabel('Lapins'); plt.ylabel('Lynx')
        plt.title(f'Population de lapins et de lynx au cours du temps\nPour des conditions initiales variantes sur une durée de {t_max-t_min} mois')
        plt.legend(bbox_to_anchor=(1.05, 1), shadow=True)
        plt.grid(); plt.show()


class Lotka_Volterra_chngt_var(Lotka_Volterra):
    """ """
    def __init__(self, x0, y0, r, p, m, q, alpha):
        super().__init__(x0, y0, r, p, m, q)
        self.alpha = alpha  # cte

    def _variation_lapin(self, v, w) -> float:
        """Variation du nombre de lapins."""
        return v - v*w

    def _variation_lynx(self, v, w) -> float:
        """Variation du nombre de lynx."""
        return -self.alpha*w + v*w

    def modele_Lotka_Volterra(self, t_min: int, t_max: int, h: float) -> pd.DataFrame:
        """Avec chgt de var"""
        s = self.r*t_min
        dv, dw = self.x0, self.y0   #'''Partie à revoir'''
        lst = [[s, dv, dw]]
        while lst[-1][0] <= t_max:
            s += h  # *r
            dv += (self.q/self.r) * self._variation_lapin(dv, dw)*h
            dw += (self.p/self.r) * self._variation_lynx(dv, dw)*h
            lst.append([s, dv, dw])
        return pd.DataFrame(lst, columns=["t", "x", "y"])


class Lotka_Volterra_limite(Lotka_Volterra):
    """ """
    def __init__(self, x0, y0, r, p, m, q, X):
        super().__init__(x0, y0, r, p, m, q)
        self.X = X
        self.orbite_y = (self.r/self.p)*(1-(self.orbite_x/self.X))

    def _variation_lapin(self, x, y) -> float:
        """Variation du nombre de lapins."""
        return self.r*x*(1-(x/self.X)) - self.p*x*y

## Menu
def menu():
    """Même un p'tit menu!"""
    def menu_choix(choix, possibilite:str)->int:
        for option in choix.keys(): print(f"{option} - {choix[option]}")
        while (entree:=input("Entrée : ")) not in possibilite:
            print('Mauvaise entrée!')
            sleep(1); print("\033[H\033[J", end="")
            menu_choix(choix, possibilite)
        return int(entree)

    def choix_modele()->tuple((str,int)):
        print('Veuillez choisir le modèle.')
        entree = menu_choix({1:"Modèle 1 - 4 variables",2:"Modèle 2 - 3 variables",3:"Modèle 3 - 4 variables et limite de lapins ",4:"Modèle 4 - 3 variables et limite de lapins",0:"Sortie"},'01234')
        if entree==0: raise KeyboardInterrupt('-Fin')
        if entree==1: return 'Lotka_Volterra',1
        if entree==2: return 'Lotka_Volterra_chngt_var',2
        if entree==3: return 'Lotka_Volterra_limite',3
        if entree==4: return '',4

    def choix_donnee(num)->str:
        print('\nVeuillez choisir les données du modèle.')
        entree = menu_choix({1:"Données préchargées (mieux pour les affichages simples)",2:"Données préchargées (mieux pour les affichages d'orbite)",3:"Entrée manuelle",0:"Sortie"},'0123')
        if entree==0: raise KeyboardInterrupt('-Fin')
        if entree==1:
            if num == 1: return '2,2,1.0,1.0,1.0,1.0'
            if num == 2: return ''
            if num == 3: return '2,2,1.0,1.0,1.0,1.0,50'
            if num == 4: return ''
        if entree==2:
            if num == 1: return '4,10,1.5,0.05,0.48,0.05'
            if num == 2: return ''
            if num == 3: return '4,10,1.5,0.05,0.48,0.05,50'
            if num == 4: return ''
        if entree==3:
            if num == 1: return f'{input("nombre de lapins (int>=0) :")},{input("nombre de lynx (int>=0) :")},{input("τ de reproduction intrinsèques des lapins (float>=0) :")},{input("τ de mortalité des lapins due aux lynx rencontrés (float>=0) :")},{input("τ de mortalité intrinsèques des lynx (float>=0) :")},{input("τ de reproduction des lynx en f° des lapins mangés (float>=0) :")}'
            if num == 2: return ''
            if num == 3: return f'{input("nombre de lapins (int>=0) :")},{input("nombre de lynx (int>=0) :")},{input("τ de reproduction intrinsèques des lapins (float>=0) :")},{input("τ de mortalité des lapins due aux lynx rencontrés (float>=0) :")},{input("τ de mortalité intrinsèques des lynx (float>=0) :")},{input("τ de reproduction des lynx en f° des lapins mangés (float>=0) :")},{input("limite du nombre de lapins (int>=0) :")}'
            if num == 4: return ''

    def choix_intervalle()->str:
        print('\nVeuillez choisir l\'intervalle d\'affichage.')
        entree = menu_choix({1:"Intervalle prédéfini",2:"Entrée manuelle",0:"Sortie"},'012')
        if entree==0: raise KeyboardInterrupt('-Fin')
        if entree==1: return '0, 50, 0.0005'
        if entree==2: return f'{input("Début (float>=0): ")},{input("Fin (float>=0 et >=start): ")},{input("Pas (float>=0): ")}'

    def choix_affichage()->tuple((str,str)):
        print('\nVeuillez choisir l\'affichage.')
        entree = menu_choix({1:"Affichage simple",2:"Affichage avec variations des coefficients",3:"Portrait de phase (visualisation des orbites)",0:"Sortie"},'0123')
        if entree==0: raise KeyboardInterrupt('-Fin')
        if entree==1: return 'affichage',None
        if entree==2:
            entree = menu_choix({1:"τ de reproduction intrinsèques des lapins",2:"τ de mortalité des lapins due aux lynx rencontrés",3:"τ de mortalité intrinsèques des lynx",4:"τ de reproduction des lynx en f° des lapins mangés",0:"Sortie"},'01234')
            if entree==0: raise KeyboardInterrupt('-Fin')
            if entree==1: return 'affichage_variation__τ','r'
            if entree==2: return 'affichage_variation__τ','p'
            if entree==3: return 'affichage_variation__τ','m'
            if entree==4: return 'affichage_variation__τ','q'
        if entree==3:
            print()
            entree = menu_choix({1:"Activé point d'équilibre",2:"Désactivé point d'équilibre",0:"Sortie"},'01234')
            print("Nombres (int) séparés par <espace>\nNB: <entree> pour liste par défaut.")
            lst = [int(x) for x in input('>>').split()]
            if len(lst) == 0:
                lst = [-2, 0, 2, 50, 65, 80, 100]
            if entree==0: raise KeyboardInterrupt('-Fin')
            if entree==1: return 'affichage_orbite',f'lst_condition_initiale={lst},orbite=True'
            if entree==2: return 'affichage_orbite',f'lst_condition_initiale={lst},orbite=False'

    print("Bienvenue!")
    modele, num = choix_modele()
    donnee = choix_donnee(num)
    intervalle = choix_intervalle()
    affichage,sup = choix_affichage()
    # Dangereux, mais fonctionne... # eval(modele(donnee).affichage(intervalle,sup))
    eval(f'{modele}(*{eval(donnee)}).{affichage}{f'(*{eval(intervalle)},{sup})' if sup else f'(*{eval(intervalle)})'}')

if __name__ == '__main__':
    menu()