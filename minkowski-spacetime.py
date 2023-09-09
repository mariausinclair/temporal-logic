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

    # Checks if a<b where a, b can be either clusters or maximal consistent sets
    def before(self, a, b):
        if isinstance(a, set):
            if isinstance(b, set):
                return self.access(a, b)
            elif isinstance(b, list):
                return self.mcs_before_cluster(a, b)
        elif isinstance(a, list):
            if isinstance(b, set):
                return self.cluster_before_mcs(a, b)
            elif isinstance(b, list):
                return self.precedes(a, b)

    # Checks if the formula is in the maximal consistent set
    def formula_in_mcs(self, mcs):
        for formula in mcs:
            if formula == self.formula:
                return True
        return False

    # Checks if m is a successor of c; c and m can be either clusters or mcs
    def successor(self, c, m):
        if not self.before(c, m):
            return False
        for z in self.get_mc_set():
            if z!=m and z!=c:
                if z not in m and z not in c:
                    if self.before(c, z) and self.before(z, m):
                        if not self.before(z, c):
                            return False
                        if not self.before(m, z):
                            return False
        return True

    def all_cluster_successors(self, c):
        list_of_successors = []
        for d in self.list_of_clusters():
            if self.successor(c, d) == True:
                list_of_successors.append(d)
        return list_of_successors

    def all_irref_successors(self, c):
        list_of_successors = []
        for d in self.list_of_irref_mcs():
            if self.successor(c,d) == True:
                list_of_successors.append(d)
        return list_of_successors

    def all_cluster_predecessors(self, c):
        list_of_successors = []
        for d in self.list_of_clusters():
            if self.successor(d, c) == True:
                list_of_successors.append(d)
        return list_of_successors

    def all_irref_predecessors(self, c):
        list_of_successors = []
        for d in self.list_of_irref_mcs():
            if self.successor(d,c) == True:
                list_of_successors.append(d)
        return list_of_successors

    def check_sat(self):

        # Checks formula is in at least one mcs
        for s in self.get_mc_set():
            if self.formula_in_mcs(s):
                break
        else:
            return False

        for m in self.get_mc_set():
            if self.formula_in_mcs(m):
                M_irref = []
                for n in self.list_of_irref_mcs():
                    for k in self.get_mc_set():
                        if self.before(m, n) and self.before(k, n):
                            M_irref.append(n)
                for irref in M_irref:
                    if len(self.all_cluster_successors(irref)) not in {1, 2}:
                        return False
                    if len(self.all_cluster_predecessors(irref)) not in {1, 2}:
                        return False

                M_clusters = []
                for x in self.list_of_irref_mcs():
                    for y in self.get_mc_set():
                        if self.before(m, y) and self.before(y, x):
                            M_clusters.append(x)
                for cluster in M_clusters:
                    if (len(self.all_irref_successors(cluster))+len(self.all_cluster_successors(cluster))) > 2:
                        if len(self.all_cluster_successors(cluster))!= 0:
                            return False
        return True

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

        if formula.check_sat():
            print(f"The formula is likely to be valid in irreflexive 2-dimensional Minkowski spacetime.")
        else:
            print(f"The formula is invalid in irreflexive 2-dimensional Minkowski spacetime.")

    except ParseError:
        print("Incorrectly formulated temporal formula.")
    except Exception as e:
        print("An error occurred.")

start_time = time.time()
main()
end_time = time.time()

elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.6f} seconds")


