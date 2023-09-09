import time

class ParseError(Exception):
    '''Raised when a given formula has incorrect formulation.'''

class TemporalFormula:

    def __init__(self, formula_string):
        if not isinstance(formula_string, str):
            raise TypeError("Formula must be a string.")
        self.formula = formula_string
        if not self.parse():
            raise ParseError("Incorrectly formulated temporal formula.")
    def __str__(self):
        return self.formula

    # Checks if the character at the specified index is an atomic proposition
    def prop(self, index):
        if self.formula[index].isalpha() and self.formula[index].islower():
            return True
        else:
            return False

    # Checks if the character at the specified index is an operator ~, F, P, G or H
    def operator(self, index):
        operators = ['~','F', 'P', 'H', 'G']
        for operator in operators:
            if self.formula[index] == operator:
                return True
        return False

    # Checks if the character at the specified index is a connective |, & or >
    def connective(self, index):
        connectives = ['|', '&', '>']
        for connective in connectives:
            if self.formula[index] == connective:
                return True
        return False

    # Returns a TemporalFormula object that is equal to the negation of the specified formula object
    def negation(self):
        if self.formula[0] == '~':
            return TemporalFormula(self.formula[1:])
        else:
            return TemporalFormula('~'+self.formula)

    # Returns left subformula as a TemporalFormula object
    def left_subformula(self):
        if self.formula[0] == '(':
            left_bracket_counter = 1
            for i in range(1, len(self.formula)):
                if self.formula[i] == '(':
                    left_bracket_counter += 1
                elif self.formula[i] == ')':
                    left_bracket_counter -= 1
                elif self.connective(i) and left_bracket_counter == 1:
                    formula_no_bracket = self.formula[1:-1]
                    return TemporalFormula(formula_no_bracket[:i - 1])
        else:
            return self

    # Returns right subformula as a TemporalFormula object
    def right_subformula(self):
        if self.formula[0] == '(':
            left_bracket_counter = 1
            for i in range(1, len(self.formula)):
                if self.formula[i] == '(':
                    left_bracket_counter += 1
                elif self.formula[i] == ')':
                    left_bracket_counter -= 1
                elif self.connective(i) and left_bracket_counter == 1:
                    formula_no_bracket = self.formula[1:-1]
                    return TemporalFormula(formula_no_bracket[i:])
        else:
            return self

    # Returns connective that is within 1 bracket access
    def conjunction(self):
        if self.formula[0] == '(':
            left_bracket_counter = 1
            for i in range(1, len(self.formula)):
                if self.formula[i] == '(':
                    left_bracket_counter += 1
                elif self.formula[i] == ')':
                    left_bracket_counter -= 1
                elif self.connective(i) and left_bracket_counter == 1:
                    return self.formula[i]

    # Expands ~(.) type formulas into (.)
    def expand(self):
        if self.formula.startswith('~('):
            temp = self.negation()
            if temp.conjunction() == '|':
                formula_string = '('+ temp.left_subformula().negation().formula+'&'+temp.right_subformula().negation().formula + ')'
                return TemporalFormula(formula_string)
            if temp.conjunction() == '&':
                formula_string = '('+ temp.left_subformula().negation().formula+'|'+temp.right_subformula().negation().formula + ')'
                return TemporalFormula(formula_string)
            if temp.conjunction() == '>':
                formula_string = '(' + temp.left_subformula().formula + '&' + temp.right_subformula().negation().formula + ')'
                return TemporalFormula(formula_string)
        else:
            return self

    # Checks whether the specified formula is correctly formulated
    def parse(self):
        if len(self.formula) == 0:
            return False
        elif not self.prop(0) and not self.operator(0) and self.formula[0]!='(':
            return False
        elif self.prop(0):
            if len(self.formula) == 1:
                return True
            else:
                return False
        elif self.operator(0):
            formula_no_operator = TemporalFormula(self.formula[1:])
            return formula_no_operator.parse()
        elif self.formula[0] == '(':
            if self.formula[-1]!=')':
                return False
            else:
                left_bracket_counter = 1
                for i in range(1, len(self.formula)):
                    if self.formula[i] == '(':
                        left_bracket_counter += 1
                    elif self.formula[i] == ')':
                        left_bracket_counter -= 1
                    elif self.connective(i) and left_bracket_counter == 1:
                        formula_no_bracket = self.formula[1:-1]
                        list_of_subformulas = [TemporalFormula(formula_no_bracket[:i - 1]),
                                               TemporalFormula(formula_no_bracket[i:])]
                        return all(subformula.parse() for subformula in list_of_subformulas)

    # Returns the closure set of the specified formula
    def get_closure_set(self):

        closure_set = set()

        if len(self.formula) == 1:
            new_items = {self.formula, self.negation().formula}
            closure_set.update(new_items)

            return closure_set

        elif self.operator(0):
            operator_subformula = TemporalFormula(self.formula[1:])
            new_items = {self.formula, self.negation().formula}
            closure_set.update(new_items)
            closure_set.update(operator_subformula.get_closure_set())

            return closure_set

        elif self.formula[0] == '(':

            bracket_counter = 1

            for i in range(1, len(self.formula)):
                if self.formula[i] == '(':
                    bracket_counter += 1
                elif self.formula[i] == ')':
                    bracket_counter -= 1
                elif self.connective(i) and bracket_counter == 1:
                    inner_formula = self.formula[1:-1]
                    left_subformula = TemporalFormula(inner_formula[:i - 1])
                    right_subformula = TemporalFormula(inner_formula[i:])
                    new_items = {self.formula, self.negation().formula}
                    closure_set.update(new_items)
                    closure_set.update(left_subformula.get_closure_set())
                    closure_set.update(right_subformula.get_closure_set())

                    return closure_set


    # Returns a list of choice sets of the specified formula
    def get_choice_set(self):
        subformulas = []
        list_of_choice_sets = []

        for subformula in self.get_closure_set():
            if not subformula[0] == '~':
                subformulas.append(subformula)

        for i in range(2 ** len(subformulas)):
            choice_set = set()

            combo = bin(i)[2:].zfill(len(subformulas))

            for j in range(len(subformulas)):
                temp = TemporalFormula(subformulas[j])
                if combo[j] == '1':
                    choice_set.add(temp.formula)
                else:
                    choice_set.add(temp.negation().formula)

            list_of_choice_sets.append(choice_set)

        return list_of_choice_sets

    # Returns a list of maximal propositionally consistent sets from the list of a choice set for a given formula
    def get_mc_set(self):

        # Checks that a set is propositionally consistent
        def is_consistent(choice_set):
            temp_set = set()
            for subformula in choice_set:
                temp_set.add(TemporalFormula(subformula).expand())
            for formula in temp_set:
                if "~HF"+formula.formula in choice_set:
                    return False
                if "~GP"+formula.formula in choice_set:
                    return False
                if formula.formula.startswith("F"):
                    if "G~"+formula.formula[1:] in choice_set:
                        return False
                if formula.formula.startswith("P"):
                    if "H~"+formula.formula[1:] in choice_set:
                        return False
                if formula.formula.startswith("G"):
                    if "F~"+formula.formula[1:] in choice_set:
                        return False
                if formula.formula.startswith("H"):
                    if "P~"+formula.formula[1:] in choice_set:
                        return False
                if formula.formula.startswith("~F"):
                    if "~G~"+formula.formula[2:] in choice_set:
                        return False
                if formula.formula.startswith("~P"):
                    if "~H~"+formula.formula[2:] in choice_set:
                        return False
                if formula.formula.startswith("~G"):
                    if "~F~"+formula.formula[2:] in choice_set:
                        return False
                if formula.formula.startswith("~H"):
                    if "~P~"+formula.formula[2:] in choice_set:
                        return False
                if formula.conjunction() == "|":
                    if formula.left_subformula().formula not in choice_set:
                        if formula.right_subformula().formula not in choice_set:
                            return False
                if formula.conjunction() == "&":
                    if formula.left_subformula().formula not in choice_set:
                        return False
                    if formula.right_subformula().formula not in choice_set:
                        return False
                if formula.conjunction() == ">":
                    if formula.left_subformula().formula in choice_set:
                        if formula.right_subformula().formula not in choice_set:
                            return False
            return True

        list_of_mc_sets = []

        for choice_set in self.get_choice_set():
            if is_consistent(choice_set):
                # if density(choice_set):
                list_of_mc_sets.append(choice_set)

        return list_of_mc_sets

    # Checks if a set m can access a set n i.e. m<n
    def access(self, m, n):
        for subformula in self.get_closure_set():
            if subformula.startswith("F"):
                if subformula in n:
                    if subformula not in m:
                        return False
                if subformula[1:] in n:
                    if subformula not in m:
                        return False
            elif subformula.startswith("P"):
                if subformula in m:
                    if subformula not in n:
                        return False
                if subformula[1:] in m:
                    if subformula not in n:
                        return False
            elif subformula.startswith("G"):
                if subformula in m:
                    if subformula not in n:
                        return False
                    if subformula[1:] not in n:
                        return False
            elif subformula.startswith("H"):
                if subformula in n:
                    if subformula not in m:
                        return False
                    if subformula[1:] not in m:
                        return False
            elif subformula.startswith("~F"):
                if subformula in m:
                    if TemporalFormula(subformula[2:]).negation().formula not in n:
                        return False
                    if subformula not in n:
                        return False
            elif subformula.startswith("~P"):
                if subformula in n:
                    if TemporalFormula(subformula[2:]).negation().formula not in m:
                        return False
                    if subformula not in m:
                        return False
            elif subformula.startswith("~G"):
                if subformula in n:
                    if subformula not in m:
                        return False
                if TemporalFormula(subformula[2:]).negation().formula in n:
                    if subformula not in m:
                        return False
            elif subformula.startswith("~H"):
                if subformula in m:
                    if subformula not in n:
                        return False
                if TemporalFormula(subformula[2:]).negation().formula in m:
                    if subformula not in n:
                        return False
        return True

    # Checks is a set is reflexive
    def is_reflexive(self, mcs):
        if self.access(mcs, mcs):
            return True
        else:
            return False

    # Returns a list of all clusters for a given temporal formula
    def list_of_clusters(self):

        # Given a reflexive mcs, returns the corresponding cluster [m]
        def get_cluster(m):
            if self.is_reflexive(m):
                cluster = [m]
                for n in self.get_mc_set():
                    if self.access(m, n) and self.access(n, m):
                        if n not in cluster:
                            cluster.append(n)
                return cluster
            else:
                return None

        list_of_clusters = []

        for mcs in self.get_mc_set():
            if self.is_reflexive(mcs):
                cluster = get_cluster(mcs)
                cluster_list = sorted([list(subset) for subset in cluster])
                if cluster_list not in list_of_clusters:
                    list_of_clusters.append(cluster_list)

        converted_clusters = []

        for cluster in list_of_clusters:
            converted_cluster = []
            for subset in cluster:
                converted_cluster.append(set(subset))
            converted_clusters.append(converted_cluster)

        sorted_clusters = sorted(converted_clusters,
                                 key=lambda cluster:[self.precedes(cluster, other)
                                                     for other in converted_clusters], reverse=True)
        return sorted_clusters

    # Returns a list of irreflexive maximal consistent sets
    def list_of_irref_mcs(self):
        list_of_irref_mcs = []
        for mcs in self.get_mc_set():
            if not self.is_reflexive(mcs):
                list_of_irref_mcs.append(mcs)
        sorted_irref_mcs = sorted(list_of_irref_mcs,
                                 key=lambda mcs: [self.access(mcs, other) for other in list_of_irref_mcs],
                                 reverse=True)
        return sorted_irref_mcs

    # Checks if c<d, where c,d are clusters
    def precedes(self, c, d):
        for m in c:
            for n in d:
                if not self.access(m, n):
                    return False
        return True

    # Checks if c<m, where c is a cluster and m is a maximal consistent set
    def cluster_before_mcs(self, cluster, mcs):
        for n in cluster:
            if not self.access(n, mcs):
                return False
        return True

    # Checks if m<c, where m is a maximal consistent set and c is a cluster
    def mcs_before_cluster(self, mcs, cluster):
        for n in cluster:
            if not self.access(mcs, n):
                return False
        return True

    # Computes the model; returns False if no model exists
    def get_model(self):

        # Finds the future defects in a cluster: returns a dictionary {defect: cure} e.g. {Fm: [Fm, m]}
        def future_defect(cluster):
            future_defects = {}
            if isinstance(cluster, set):
                cluster = [cluster]
            for mcs in cluster:
                for subformula in mcs:
                    if subformula.startswith("F"):
                        add_defect = True
                        for s in cluster:
                            if subformula[1:] in s:
                                add_defect = False
                                break
                        if add_defect:
                            future_defects[subformula] = [subformula, subformula[1:]]
                    elif subformula.startswith("~G"):
                        add_defect = True
                        for s in cluster:
                            if TemporalFormula(subformula[2:]).negation().formula in s:
                                add_defect = False
                                break
                        if add_defect:
                            future_defects[subformula] = [subformula, TemporalFormula(subformula[2:]).negation().formula]
            return future_defects

        # Finds the past defects in a cluster: returns a dictionary {defect: cure} e.g. {Pm: [Pm, m]}
        def past_defect(cluster):
            past_defects = {}
            if isinstance(cluster, set):
                cluster = [cluster]
            for mcs in cluster:
                for subformula in mcs:
                    if subformula.startswith("P"):
                        add_defect = True
                        for s in cluster:
                            if subformula[1:] in s:
                                add_defect = False
                                break
                        if add_defect:
                            past_defects[subformula] = [subformula, subformula[1:]]
                    elif subformula.startswith("~H"):
                        add_defect = True
                        for s in cluster:
                            if TemporalFormula(subformula[2:]).negation().formula in s:
                                add_defect = False
                                break
                        if add_defect:
                            past_defects[subformula] = [subformula, TemporalFormula(subformula[2:]).negation().formula]
            return past_defects

        # Returns candidate clusters for the last cluster in the filtration
        def get_top_clusters(clusters):
            top_clusters = []
            for c in clusters:
                if future_defect(c) == {}:
                    top_clusters.append(c)
            return top_clusters

        # Returns candidate clusters for the first cluster in the filtration
        def get_bottom_clusters(clusters):
            bottom_clusters = []
            for c in clusters:
                if past_defect(c) == {}:
                     bottom_clusters.append(c)
            return bottom_clusters

        def formula_in_model(model):
            for subset in model:
                if isinstance(subset, list):
                    for mcs in subset:
                        if self.formula in mcs:
                            return True
            return False

        # Computes next mcs in the model
        def find_next_mcs(previous, list_of_irref_mcs):

            def cured(cures, next_set):
                if isinstance(next_set, set):
                    next_set = [next_set]
                for subset in next_set:
                    if any(cure in subset for cure in cures):
                        return True
                return False

            def passed_up(defects, next_set):
                for defect, cures in defects.items():
                    if not cured(cures, next_set):
                        return False
                return True

            if list_of_irref_mcs == []:
                return None
            else:
                for irref in list_of_irref_mcs:
                    if self.cluster_before_mcs(previous, irref):
                        # Checks defects have been passed up
                        if passed_up(future_defect(previous), irref) and passed_up(past_defect(irref), previous):
                            return irref
                return None

        # Computes next cluster in the model
        def find_next_cluster(previous, list_of_clusters):

            def cured(cures, next_set):
                for subset in next_set:
                    if any(cure in subset for cure in cures):
                        return True
                return False

            def passed_up(defects, next_set):
                for defect, cures in defects.items():
                    if not cured(cures, next_set):
                        return False
                return True

            if list_of_clusters == []:
                return None
            else:
                for cluster in list_of_clusters:
                    if self.mcs_before_cluster(previous, cluster):
                        # Checks defects have been passed up
                        if passed_up(future_defect(previous), cluster) and passed_up(past_defect(cluster), previous):
                            return cluster
                return None

        # Computes a model for a given smallest cluster
        def compute_model(bottom_cluster):
            model = [bottom_cluster]
            list_of_irref_mcs = self.list_of_irref_mcs()
            list_of_clusters = self.list_of_clusters()
            while True:
                # print(model)
                if model[-1] in get_top_clusters(self.list_of_clusters()) and formula_in_model(model):
                    return model
                else:
                    if isinstance(model[-1], list):
                        if list_of_irref_mcs == []:
                            return False
                        else:
                            next_item = find_next_mcs(model[-1], list_of_irref_mcs)
                            if next_item is None:
                                if len(model) == 1:
                                    return False
                                else:
                                    list_of_clusters.remove(model[-1])
                                    model.pop()
                            else:
                                while next_item in model:
                                    list_of_irref_mcs.remove(next_item)
                                    next_item = find_next_mcs(model[-1], list_of_irref_mcs)
                                model.append(next_item)
                    elif isinstance(model[-1], set):
                        if list_of_clusters == []:
                            return False
                        else:
                            next_item = find_next_cluster(model[-1], list_of_clusters)
                            if next_item is None:
                                list_of_irref_mcs.remove(model[-1])
                                model.pop()
                            else:
                                while next_item in model:
                                    list_of_clusters.remove(next_item)
                                    next_item = find_next_mcs(model[-1], list_of_clusters)
                                model.append(next_item)
            return False

        # Iterates through all possible smallest clusters
        for bottom_cluster in get_bottom_clusters(self.list_of_clusters()):
            if compute_model(bottom_cluster) != False:
                return compute_model(bottom_cluster)
        return False

# Main program
def main():
    try:
        formula = TemporalFormula(input('Enter a temporal formula:'))
        print("The formula is formulated correctly.")
        print(f"The closure set is {formula.get_closure_set()}.")
        print(f"The choice sets are {formula.get_choice_set()}.")
        print(f"The maximal consistent sets are {formula.get_mc_set()}.")
        print(f"The clusters are {formula.list_of_clusters()}.")
        print(f"The irreflexive maximal consistent sets are {formula.list_of_irref_mcs()}.")
        if formula.get_model() == False:
            result = "No model found."
        else:
            result = f"A possible model is {formula.get_model()}."
        print(result)

    except ParseError:
        print("Incorrectly formulated temporal formula.")
    except Exception as e:
        print("An error occurred.")

start_time = time.time()
main()
end_time = time.time()

elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.6f} seconds")


