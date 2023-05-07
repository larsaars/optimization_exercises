# Mimimum Set Cover

from ortools.linear_solver import pywraplp
import json
import logging

logger = logging.basicConfig(level=logging.DEBUG)


def get_decisionVariables(solver, data):
    """ Erstellt eine Liste der Entscheidungsvariablen, z.B.:
        Entscheidungsvariable supplier_0 wird 1 wenn der Supplier verwendet wird und 0 wenn nicht
    """
    decisionVars = []
    for supplier in data:
        decisionVars.append(solver.IntVar(0, 1, supplier))
    return decisionVars


def get_supplier_indices_for_part_i(data, part_i):
    """ Erstellt eine Liste aus den Indizes der Supplier die Bauteil part_i anbieten
    """
    supplier_indices = []
    i = 0
    for supplier in data:
        if part_i in data[supplier]:
            supplier_indices.append(i)
        i += 1
    return supplier_indices


def sum_of_suppliers_of_part_i(data, part_i, decisionVars):
    """ Erstellt die Summe der Supplier, die für Bauteil part_i in Frage kommen
        _ decesionVars[supplier_idx] kann 0 oder 1 sein
        _ sum ist die Anzahl der Supplier, die Bauteil part_i anbieten und vom Solver ausgewählt wurden
    """
    suppliers_for_part_i = get_supplier_indices_for_part_i(data, part_i)
    sum = 0
    for supplier_idx in suppliers_for_part_i:
        sum += decisionVars[supplier_idx]
    return sum


def MIP_Solver(data, count_supplier, count_parts, verbose=True):
    # 1. Solver erstellen
    solver = pywraplp.Solver('MySolver', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
    if not solver:
        return
    
    # 2. Entscheidungsvariablen definieren
    decisionVars = get_decisionVariables(solver, data)
    if verbose: print('Number of decision variables =', solver.NumVariables())

    # 3. Einschränkungen definieren
    #    Eine Einschränkung pro Bauteil: Die Summe der Supplier die das Bauteil anbieten
    #                                    und vom Solver ausgewählt werden >=
    #    d.h. Bauteil muss min. einmal vorkommen
    for part_i in range(count_parts+1):
        solver.Add(sum_of_suppliers_of_part_i(data, part_i, decisionVars) >= 1)  # TODO funktioniert noch nicht ganz

    print('Number of constraints =', solver.NumConstraints())

    # 4. Ziel definieren
    #    Summe der ausgewählten Supplier minimal
    solver.Minimize(sum( decisionVars ))

    # 5. MIP-Lösen aufrufen
    status = solver.Solve()

    # 6. Lösung anzeigen
    if status == pywraplp.Solver.OPTIMAL:
        print('\nSolution:')
        print('Objective value =', solver.Objective().Value())
        print('Choosen Suppliers:')
        for decisionVar in decisionVars:
            if decisionVar.solution_value() == 1.0:
                print(decisionVar)
    else:
        print('The problem does not have an optimal solution.')


if __name__ == '__main__':
    data = {}
    with open('./min_set_cover_data.json') as file:
        data = json.load(file)

    # Anzahl der Bauteile berechnen
    count_parts = 0
    for supplier in data:
        if max(data[supplier]) > count_parts:
            count_parts = max(data[supplier])
    print("count parts = ", count_parts)

    # Anzahl der Supplier bestimmen
    count_supplier = len(data)
    print("count supplier = ", count_supplier)

    MIP_Solver(data, count_supplier, count_parts)
