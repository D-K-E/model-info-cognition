# Sample Input #01

# 0 1
# -b--d
# -d--d
# --dd-
# --d--
# ----d

# Sample Output #01

# DOWN

# Resultant state

# ----d
# -d--d
# --dd-
# --d--
# ----d
from typing import List, Tuple, Set
import random
import pdb

Milieu = List[List[str]]


# fonctions d'utils


def montrer_milieu(m: Milieu):
    finale = ""
    for ligne in m:
        l = "".join(ligne)
        finale += "\n" + l
    return finale


def montrer_milieux(ms: List[Milieu], headers: List[str]):
    "cote a cote les milieux"
    finale = "\t".join(headers)
    mms = [m.splitlines() for m in ms]
    for i in range(len(mms[0])):
        finale += "\n" + "\t".join([m[i] for m in mms])
    return finale


def choisir_ligne_colonne(nb_ligne: int, nb_colonne: int):
    moche_ligne = random.choice(list(range(nb_ligne - 1)))
    moche_colonne = random.choice(list(range(nb_colonne - 1)))
    return moche_ligne, moche_colonne


def ft_m(nb_ligne: int, nb_colonne: int):
    return [["-" for c in range(nb_colonne)] for l in range(nb_ligne)]


def ft_milieu(milieu_range: Tuple[int, int], max_moche: int):
    "Create board with random dirt"
    nb_ligne = random.choice([i for i in range(milieu_range[0], milieu_range[1])])
    nb_colonne = random.choice([i for i in range(milieu_range[0], milieu_range[1])])
    milieu_pur = ft_m(nb_ligne, nb_colonne)
    milieu = ft_m(nb_ligne, nb_colonne)
    nb_moche = random.choice([i for i in range(1, max_moche)])
    agent_ligne, agent_colonne = choisir_ligne_colonne(nb_ligne, nb_colonne)
    for m in range(nb_moche):
        moche_ligne, moche_colonne = choisir_ligne_colonne(nb_ligne, nb_colonne)
        milieu[moche_ligne][moche_colonne] = "m"
    return (
        milieu,
        milieu_pur,
        nb_ligne,
        nb_colonne,
        nb_moche,
        agent_ligne,
        agent_colonne,
    )


class Etat:
    def __init__(self, milieu: Milieu, coordonne_agent=None, parent=None):
        self.milieu = tuple([tuple(m) for m in milieu])
        self.lieu_agent = coordonne_agent
        self.parent = parent
        self.act = None

    def __eq__(self, autreEtat):
        if isinstance(autreEtat, Etat):
            return (
                autreEtat.milieu == self.milieu
                and autreEtat.lieu_agent == self.lieu_agent
            )
        return False

    def __str__(self):
        if self.lieu_agent:
            milieu = self.milieu_a_list()
            l, c = self.lieu_agent
            milieu[l][c] += "A"
        else:
            milieu = self.milieu_a_list()
        return montrer_milieu(milieu)

    def __hash__(self):
        return hash((self.milieu, self.lieu_agent))

    def milieu_a_list(self):
        return [list(m) for m in self.milieu]

    def montre(self):
        print("Etat: ", str(self))

    def montre_actions(self):
        ""
        chemin = ""
        chemin = self.act + "\n" + chemin
        parent = self.parent
        while parent is not None:
            chemin += "\n" + str(parent.act)
            parent = parent.parent
        return chemin

    def montre_chemin(self):
        coords = []
        parent = self.parent
        while parent is not None:
            coords.append(parent.lieu_agent)
            parent = parent.parent
        #
        milieu = self.milieu_a_list()
        for coord in coords:
            ligne, colonne = coord
            milieu[ligne][colonne] = "×"
        return montrer_milieu(milieu)


class AgentSimple:
    def __init__(self, etat_init: Etat, but: Etat):
        """
        Notre agent qui nettoie les zones moches dans le bord
        """
        self.etat_init = etat_init
        self.but = but
        self.chemins: List[Etat] = []
        self.actions = ["GAUCHE", "DROIT", "HAUT", "BAS", "NETTOYER"]

    def evaluer_etat(self, etat: Etat) -> int:
        "evauler un etat en fonction d'un metrique"
        compte_moche = 0
        for ligne in etat.milieu:
            for colonne in ligne:
                if "m" in colonne:
                    compte_moche += 1
        return compte_moche

    def evaluer_chemin(self, etat: Etat) -> int:
        moche_total = 0
        etatn = etat.parent
        while etatn is not None:
            moche_total += self.evaluer_etat(etatn)
            etatn = etatn.parent
        return moche_total

    def tirer_chemins(self):
        "tirer les chemins existants"
        self.chemins.sort(key=self.evaluer_chemin)

    def etat_dans_chemins(self, e: Etat) -> int:
        for i, etat in enumerate(self.chemins):
            if etat == e:
                return i
        return -1

    def distance(self, etat1: Etat, etat2: Etat) -> int:
        "calcule la distance entre les deux etats"
        detat1 = self.evaluer_etat(etat1)
        detat2 = self.evaluer_etat(etat2)
        diff = abs(detat1 - detat2)
        #
        return diff

    def etat_but(self, etat_milieu: Etat) -> bool:
        return etat_milieu.milieu == self.but.milieu

    def bouger_agent(self, etat: Etat, action: str) -> Etat:
        "bouger agent dans l'etat"
        ligne, colonne = etat.lieu_agent
        if action == "GAUCHE":
            colonne -= 1
        elif action == "DROIT":
            colonne += 1
        elif action == "HAUT":
            ligne -= 1
        elif action == "BAS":
            ligne += 1
        nouvel_etat = Etat(etat.milieu, coordonne_agent=(ligne, colonne))
        return nouvel_etat

    def trouver_moche_proche(self, etat: Etat) -> (int, int):
        "trouver le moche le plus proche a l'agent"
        agent_ligne, agent_colonne = etat.lieu_agent
        total_diff = float("inf")
        moche_ligne = moche_colonne = 0
        for ligne_index, ligne in enumerate(etat.milieu):
            for colonne_index, colonne in enumerate(ligne):
                if "m" in colonne:
                    m_ligne_diff = abs(agent_ligne - ligne_index)
                    m_colonne_diff = abs(agent_colonne - colonne_index)
                    if m_ligne_diff + m_colonne_diff < total_diff:
                        moche_ligne = ligne_index
                        moche_colonne = colonne_index
                        total_diff = m_ligne_diff + m_colonne_diff
        return moche_ligne, moche_colonne

    def nettoyer_cellule(
        self, etat: Etat, moche_ligne: int, moche_colonne: int
    ) -> Etat:
        ""
        milieu = etat.milieu_a_list()
        milieu[moche_ligne][moche_colonne] = "-"
        nouvel_etat = Etat(milieu, coordonne_agent=etat.lieu_agent)
        return nouvel_etat

    def choisir_action(self, e: Etat):
        "choisir une direction"
        #
        moche_ligne, moche_colonne = self.trouver_moche_proche(e)
        agent_ligne, agent_colonne = e.lieu_agent
        ligne_diff = agent_ligne - moche_ligne
        colonne_diff = agent_colonne - moche_colonne

        if ligne_diff < 0:
            return "BAS", moche_ligne, moche_colonne
        elif ligne_diff > 0:
            return "HAUT", moche_ligne, moche_colonne
        if colonne_diff < 0:
            return "DROIT", moche_ligne, moche_colonne
        elif colonne_diff > 0:
            return "GAUCHE", moche_ligne, moche_colonne
        elif colonne_diff == 0 and ligne_diff == 0:
            return "NETTOYER", moche_ligne, moche_colonne

    def appliquer_action(
        self, e: Etat, action: str, moche_ligne: int, moche_colonne: int,
    ) -> Etat:
        ""
        if action == "NETTOYER":
            return self.nettoyer_cellule(e, moche_ligne, moche_colonne)
        else:
            return self.bouger_agent(e, action)

    def generer_nouvel_etat(self, etat: Etat) -> List[Etat]:
        "generer des nouvelles etats possibles"
        action, moche_ligne, moche_colonne = self.choisir_action(etat)
        nouvel_etat = self.appliquer_action(etat, action, moche_ligne, moche_colonne)
        nouvel_etat.act = action
        nouvel_etat.parent = etat
        return nouvel_etat

    def resoudre(self):
        "commencer au resoudre le probleme"
        if self.etat_init == self.but:
            return self.etat_init
        vu = set()
        self.chemins.append(self.etat_init)
        while self.chemins:
            dernier_etat = self.chemins.pop()
            vu.add(dernier_etat)
            nouvel_etat = self.generer_nouvel_etat(dernier_etat)
            etat_index = self.etat_dans_chemins(nouvel_etat)
            if nouvel_etat not in vu and etat_index < 0:
                if self.etat_but(nouvel_etat):
                    return nouvel_etat
                self.chemins.append(nouvel_etat)
                self.tirer_chemins()
            elif etat_index >= 0:
                etat_existant = self.chemins[etat_index]
                cout_existant = self.evaluer_chemin(etat_existant)
                cout_nouvel_etat = self.evaluer_chemin(nouvel_etat)
                if cout_nouvel_etat < cout_existant:
                    self.chemins[etat_index] = nouvel_etat
                    self.tirer_chemins()


if __name__ == "__main__":
    milieu_bas = input("Entrer une taille minimale du milieu: ")
    milieu_haut = input("Entrer une taille maximale du milieu: ")
    # milieu_haut = "6"
    # milieu_bas = "5"
    m_bas = int(milieu_bas)
    m_haut = int(milieu_haut)
    if m_haut < m_bas:
        raise ValueError("Taille maximale est plus petit que minimale")
    max_moche = input("Nombre maximale de moche: ")
    # max_moche = "4"
    max_moche = int(max_moche)
    if max_moche >= m_bas:
        raise ValueError(
            "Le nombre de moche est plus grand que taille minimale" " du milieu"
        )
    m, m_pur, nl, nc, nm, al, ac = ft_milieu(
        milieu_range=(m_bas, m_haut), max_moche=max_moche
    )
    print("nombre de ligne: ", nl)
    print("nombre de colonne: ", nc)
    print("nombre de cellule moche: ", nm)
    print("ligne d'agent: ", al)
    print("colonne d'agent: ", ac)
    etat_initiale = Etat(milieu=m, coordonne_agent=(al, ac), parent=None)
    etat_finale = Etat(milieu=m_pur, coordonne_agent=None, parent=None)

    print("Agent Commence ...")
    agent = AgentSimple(etat_initiale, but=etat_finale)
    solution = agent.resoudre()
    acts = solution.montre_actions()
    chemin = solution.montre_chemin()
    etat_init = str(etat_initiale)
    etat_fin = str(etat_finale)
    print("Les actions d'Agent: ")
    print(acts)
    evolution_agent = montrer_milieux(
        ms=[etat_init, chemin, etat_fin],
        headers=["État Initiale", "Chemin d'Agent", "État Finale"],
    )
    print(evolution_agent)
